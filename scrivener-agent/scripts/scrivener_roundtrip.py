#!/usr/bin/env python3
"""Read-only Scrivener package inspection and verification CLI.

This harness is intentionally dependency-free. It parses the .scrivx XML with
ElementTree and reads associated package files without modifying the project.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class ScrivenerError(Exception):
    """Expected CLI error with a clean message."""


def local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def children_named(element: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in list(element) if local_name(child.tag) == name]


def first_child(element: ET.Element, name: str) -> ET.Element | None:
    for child in list(element):
        if local_name(child.tag) == name:
            return child
    return None


def child_text(element: ET.Element, name: str) -> str | None:
    child = first_child(element, name)
    if child is None or child.text is None:
        return None
    return child.text


@dataclass
class BinderItem:
    uuid: str
    title: str
    type: str | None
    depth: int
    parent_uuid: str | None
    order: int
    label_id: str | None = None
    status_id: str | None = None
    element: ET.Element | None = field(default=None, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "uuid": self.uuid,
            "title": self.title,
            "type": self.type,
            "depth": self.depth,
            "parent_uuid": self.parent_uuid,
            "order": self.order,
            "label_id": self.label_id,
            "status_id": self.status_id,
        }


class ScrivenerProject:
    def __init__(self, project_path: Path):
        self.input_path = project_path.expanduser()
        self.package_path, self.scrivx_path = self._resolve_paths(self.input_path)
        self.tree = self._parse_xml(self.scrivx_path)
        self.root = self.tree.getroot()
        self.items = self._load_binder_items()
        self.by_uuid = {item.uuid: item for item in self.items}
        self.children_by_parent: dict[str | None, list[BinderItem]] = {}
        for item in self.items:
            self.children_by_parent.setdefault(item.parent_uuid, []).append(item)

    @staticmethod
    def _resolve_paths(path: Path) -> tuple[Path, Path]:
        if not path.exists():
            raise ScrivenerError(f"Project path does not exist: {path}")

        if path.is_file() and path.suffix.lower() == ".scrivx":
            package_path = path.parent
            if package_path.suffix.lower() != ".scriv":
                raise ScrivenerError(
                    f".scrivx file is not inside a .scriv package: {path}"
                )
            return package_path, path

        if path.is_dir() and path.suffix.lower() == ".scriv":
            scrivx_files = sorted(path.glob("*.scrivx"))
            if len(scrivx_files) == 1:
                return path, scrivx_files[0]
            if not scrivx_files:
                raise ScrivenerError(f"No .scrivx file found inside package: {path}")
            names = ", ".join(file.name for file in scrivx_files)
            raise ScrivenerError(
                f"Multiple .scrivx files found in package; pass one explicitly: {names}"
            )

        raise ScrivenerError(
            f"Expected a .scriv package directory or .scrivx file, got: {path}"
        )

    @staticmethod
    def _parse_xml(path: Path) -> ET.ElementTree:
        try:
            return ET.parse(path)
        except ET.ParseError as exc:
            raise ScrivenerError(f"Invalid XML in {path}: {exc}") from exc
        except OSError as exc:
            raise ScrivenerError(f"Could not read {path}: {exc}") from exc

    def _find_binder_root(self) -> ET.Element:
        for element in self.root.iter():
            if local_name(element.tag) == "Binder":
                return element
        raise ScrivenerError(f"No Binder element found in {self.scrivx_path}")

    def _load_binder_items(self) -> list[BinderItem]:
        binder = self._find_binder_root()
        items: list[BinderItem] = []
        counter = 0

        def walk(container: ET.Element, depth: int, parent_uuid: str | None) -> None:
            nonlocal counter
            for child in children_named(container, "BinderItem"):
                counter += 1
                uuid = self._item_uuid(child)
                title = (child_text(child, "Title") or child.get("Title") or "").strip()
                item = BinderItem(
                    uuid=uuid,
                    title=title,
                    type=child.get("Type"),
                    depth=depth,
                    parent_uuid=parent_uuid,
                    order=counter,
                    label_id=self._metadata_value(child, "LabelID"),
                    status_id=self._metadata_value(child, "StatusID"),
                    element=child,
                )
                items.append(item)
                child_container = first_child(child, "Children")
                if child_container is not None:
                    walk(child_container, depth + 1, uuid)

        walk(binder, 0, None)
        return items

    @staticmethod
    def _item_uuid(element: ET.Element) -> str:
        uuid = element.get("UUID") or element.get("Uuid") or element.get("ID")
        if not uuid:
            title = child_text(element, "Title") or "<untitled>"
            raise ScrivenerError(f"Binder item lacks UUID: {title}")
        return uuid

    @staticmethod
    def _metadata_value(element: ET.Element, key: str) -> str | None:
        metadata = first_child(element, "MetaData")
        if metadata is not None:
            for candidate in metadata.iter():
                if local_name(candidate.tag) == key:
                    return (candidate.text or "").strip()
        for attr_key, value in element.attrib.items():
            if attr_key.lower() == key.lower():
                return value
        return None

    def require_uuid(self, uuid: str) -> BinderItem:
        item = self.by_uuid.get(uuid)
        if not item:
            raise ScrivenerError(f"UUID not found in binder: {uuid}")
        return item

    def docs_dir(self, uuid: str) -> Path:
        return self.package_path / "Files" / "Data" / uuid


def project_from_args(args: argparse.Namespace) -> ScrivenerProject:
    project_path = args.project or getattr(args, "project_path", None)
    if not project_path:
        raise ScrivenerError("Pass --project Project.scriv or a .scrivx project path.")
    return ScrivenerProject(Path(project_path))


def emit(data: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True))
    elif isinstance(data, str):
        print(data)
    else:
        print_human(data)


def print_human(data: Any) -> None:
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                print(format_item_line(item))
            else:
                print(item)
    elif isinstance(data, dict):
        for key, value in data.items():
            print(f"{key}: {value}")
    else:
        print(data)


def format_item_line(item: dict[str, Any]) -> str:
    depth = int(item.get("depth") or 0)
    indent = "  " * depth
    item_type = item.get("type") or "-"
    title = item.get("title") or "<untitled>"
    uuid = item.get("uuid") or "-"
    return f"{indent}{title} [{uuid}] type={item_type}"


def command_list(args: argparse.Namespace) -> int:
    project = project_from_args(args)
    items = [item.to_dict() for item in project.items]
    emit(items, args.json)
    return 0


def command_find(args: argparse.Namespace) -> int:
    project = project_from_args(args)
    needle = args.title if args.case_sensitive else args.title.lower()
    matches = []
    for item in project.items:
        haystack = item.title if args.case_sensitive else item.title.lower()
        matched = haystack == needle if args.exact else needle in haystack
        if matched:
            matches.append(item.to_dict())
    emit(matches, args.json)
    return 0 if matches else 2


def command_tree(args: argparse.Namespace) -> int:
    project = project_from_args(args)
    root_uuid = args.uuid
    if root_uuid:
        project.require_uuid(root_uuid)
        items = subtree(project, root_uuid)
    else:
        items = project.items
    emit([item.to_dict() for item in items], args.json)
    return 0


def subtree(project: ScrivenerProject, root_uuid: str) -> list[BinderItem]:
    root_item = project.require_uuid(root_uuid)
    result = [root_item]
    root_depth = root_item.depth

    def walk(parent_uuid: str) -> None:
        for child in project.children_by_parent.get(parent_uuid, []):
            adjusted = BinderItem(
                uuid=child.uuid,
                title=child.title,
                type=child.type,
                depth=child.depth - root_depth,
                parent_uuid=child.parent_uuid,
                order=child.order,
                label_id=child.label_id,
                status_id=child.status_id,
            )
            result.append(adjusted)
            walk(child.uuid)

    result[0] = BinderItem(
        uuid=root_item.uuid,
        title=root_item.title,
        type=root_item.type,
        depth=0,
        parent_uuid=root_item.parent_uuid,
        order=root_item.order,
        label_id=root_item.label_id,
        status_id=root_item.status_id,
    )
    walk(root_uuid)
    return result


def command_children(args: argparse.Namespace) -> int:
    project = project_from_args(args)
    project.require_uuid(args.uuid)
    children = project.children_by_parent.get(args.uuid, [])
    emit([item.to_dict() for item in children], args.json)
    return 0


def read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise ScrivenerError(f"Could not read {path}: {exc}") from exc


def rtf_to_text(path: Path) -> tuple[str, str]:
    textutil = shutil.which("textutil")
    if textutil:
        try:
            proc = subprocess.run(
                [textutil, "-convert", "txt", "-stdout", str(path)],
                check=False,
                capture_output=True,
                text=True,
            )
            if proc.returncode == 0:
                return proc.stdout, "textutil"
        except OSError:
            pass
    return fallback_rtf_to_text(read_text_file(path)), "fallback"


def fallback_rtf_to_text(raw: str) -> str:
    # Small, conservative fallback. Good enough for inspection when textutil is
    # unavailable; it is not intended to be a full RTF parser.
    raw = re.sub(r"\\'[0-9a-fA-F]{2}", " ", raw)
    raw = raw.replace("\\par", "\n").replace("\\line", "\n")
    raw = re.sub(r"\\[a-zA-Z]+-?\d* ?", "", raw)
    raw = raw.replace("\\{", "{").replace("\\}", "}").replace("\\\\", "\\")
    raw = re.sub(r"[{}]", "", raw)
    raw = re.sub(r"\n{3,}", "\n\n", raw)
    return raw.strip()


def candidate_files(doc_dir: Path, field_name: str) -> list[Path]:
    fields = {
        "body": ["content.rtf", "content.txt", "content.md"],
        "notes": ["notes.rtf", "notes.txt", "notes.md"],
        "synopsis": ["synopsis.txt", "synopsis.rtf", "synopsis.md"],
    }
    return [doc_dir / name for name in fields[field_name]]


def extract_field(project: ScrivenerProject, uuid: str, field_name: str) -> dict[str, Any]:
    doc_dir = project.docs_dir(uuid)
    for path in candidate_files(doc_dir, field_name):
        if not path.exists():
            continue
        if path.suffix.lower() == ".rtf":
            text, converter = rtf_to_text(path)
        else:
            text, converter = read_text_file(path), "plain"
        return {
            "uuid": uuid,
            "field": field_name,
            "path": str(path),
            "converter": converter,
            "text": text,
        }
    return {
        "uuid": uuid,
        "field": field_name,
        "path": None,
        "converter": None,
        "text": "",
        "missing": True,
    }


def extract_snapshots(project: ScrivenerProject, uuid: str) -> dict[str, Any]:
    snapshots_dir = project.package_path / "Snapshots" / f"{uuid}.snapshots"
    snapshots = []
    if snapshots_dir.exists():
        for path in sorted(snapshots_dir.iterdir()):
            if not path.is_file() or path.name.startswith("."):
                continue
            if path.suffix.lower() == ".rtf":
                text, converter = rtf_to_text(path)
            elif path.suffix.lower() in {".txt", ".md", ".xml"}:
                text, converter = read_text_file(path), "plain"
            else:
                text, converter = "", "unsupported"
            snapshots.append(
                {
                    "path": str(path),
                    "name": path.name,
                    "converter": converter,
                    "text": text,
                }
            )
    return {"uuid": uuid, "field": "snapshots", "snapshots": snapshots}


def command_extract(args: argparse.Namespace) -> int:
    project = project_from_args(args)
    project.require_uuid(args.uuid)
    fields = ["body", "notes", "synopsis", "snapshots"] if args.field == "all" else [args.field]
    results = []
    for field_name in fields:
        if field_name == "snapshots":
            results.append(extract_snapshots(project, args.uuid))
        else:
            results.append(extract_field(project, args.uuid, field_name))

    if args.json:
        emit(results if args.field == "all" else results[0], True)
    else:
        for result in results:
            if result["field"] == "snapshots":
                print(f"# snapshots ({len(result['snapshots'])})")
                for snapshot in result["snapshots"]:
                    print(f"\n## {snapshot['name']}")
                    if snapshot["text"]:
                        print(snapshot["text"])
                    else:
                        print(f"[{snapshot['converter']}] {snapshot['path']}")
            else:
                path = result.get("path") or "missing"
                print(f"# {result['field']} ({path})")
                print(result.get("text", ""))
                if result is not results[-1]:
                    print()
    return 0


def command_verify_parent(args: argparse.Namespace) -> int:
    project = project_from_args(args)
    child = project.require_uuid(args.child_uuid)
    parent = project.require_uuid(args.parent_uuid)
    ok = child.parent_uuid == parent.uuid
    result = {
        "ok": ok,
        "child_uuid": child.uuid,
        "child_title": child.title,
        "expected_parent_uuid": parent.uuid,
        "expected_parent_title": parent.title,
        "actual_parent_uuid": child.parent_uuid,
        "actual_parent_title": project.by_uuid[child.parent_uuid].title
        if child.parent_uuid in project.by_uuid
        else None,
    }
    emit(result, args.json)
    return 0 if ok else 1


def command_verify_meta(args: argparse.Namespace) -> int:
    project = project_from_args(args)
    item = project.require_uuid(args.uuid)
    checks = {}
    if args.label is not None:
        checks["label"] = {"expected": args.label, "actual": item.label_id}
    if args.status is not None:
        checks["status"] = {"expected": args.status, "actual": item.status_id}
    if not checks:
        raise ScrivenerError("Pass at least one of --label or --status.")
    ok = all(value["expected"] == value["actual"] for value in checks.values())
    result = {
        "ok": ok,
        "uuid": item.uuid,
        "title": item.title,
        "checks": checks,
    }
    emit(result, args.json)
    return 0 if ok else 1


def command_validate(args: argparse.Namespace) -> int:
    project = project_from_args(args)
    result = {
        "ok": True,
        "scrivx": str(project.scrivx_path),
        "elementtree": "ok",
        "xmllint": "not-found",
        "binder_items": len(project.items),
    }
    xmllint = shutil.which("xmllint")
    if xmllint:
        proc = subprocess.run(
            [xmllint, "--noout", str(project.scrivx_path)],
            check=False,
            capture_output=True,
            text=True,
        )
        result["xmllint"] = "ok" if proc.returncode == 0 else "failed"
        if proc.returncode != 0:
            result["ok"] = False
            result["xmllint_error"] = (proc.stderr or proc.stdout).strip()
    emit(result, args.json)
    return 0 if result["ok"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only Scrivener .scriv/.scrivx inspection harness."
    )
    add_common_options(parser)

    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List binder titles and UUIDs.")
    add_common_options(list_parser, suppress_defaults=True)
    list_parser.set_defaults(func=command_list)

    find_parser = subparsers.add_parser("find", help="Find binder items by title.")
    add_common_options(find_parser, suppress_defaults=True)
    find_parser.add_argument("title", help="Title text to search for.")
    find_parser.add_argument("--exact", action="store_true", help="Require exact title match.")
    find_parser.add_argument(
        "--case-sensitive", action="store_true", help="Use case-sensitive matching."
    )
    find_parser.set_defaults(func=command_find)

    tree_parser = subparsers.add_parser("tree", help="Show the full binder tree or a subtree.")
    add_common_options(tree_parser, suppress_defaults=True)
    tree_parser.add_argument("--uuid", help="Root UUID for subtree output.")
    tree_parser.set_defaults(func=command_tree)

    children_parser = subparsers.add_parser("children", help="Show direct children of a UUID.")
    add_common_options(children_parser, suppress_defaults=True)
    children_parser.add_argument("uuid", help="Parent binder UUID.")
    children_parser.set_defaults(func=command_children)

    extract_parser = subparsers.add_parser(
        "extract", help="Extract body, notes, synopsis, snapshots, or all fields by UUID."
    )
    add_common_options(extract_parser, suppress_defaults=True)
    extract_parser.add_argument("uuid", help="Binder UUID to extract.")
    extract_parser.add_argument(
        "field",
        choices=["body", "notes", "synopsis", "snapshots", "all"],
        help="Content field to extract.",
    )
    extract_parser.set_defaults(func=command_extract)

    parent_parser = subparsers.add_parser(
        "verify-parent", help="Verify that one binder UUID is a direct child of another."
    )
    add_common_options(parent_parser, suppress_defaults=True)
    parent_parser.add_argument("child_uuid")
    parent_parser.add_argument("parent_uuid")
    parent_parser.set_defaults(func=command_verify_parent)

    meta_parser = subparsers.add_parser(
        "verify-meta", help="Verify LabelID and/or StatusID for a binder UUID."
    )
    add_common_options(meta_parser, suppress_defaults=True)
    meta_parser.add_argument("uuid")
    meta_parser.add_argument("--label", help="Expected LabelID.")
    meta_parser.add_argument("--status", help="Expected StatusID.")
    meta_parser.set_defaults(func=command_verify_meta)

    validate_parser = subparsers.add_parser("validate", help="Validate .scrivx XML.")
    add_common_options(validate_parser, suppress_defaults=True)
    validate_parser.set_defaults(func=command_validate)

    return parser


def add_common_options(
    parser: argparse.ArgumentParser, suppress_defaults: bool = False
) -> None:
    project_default = argparse.SUPPRESS if suppress_defaults else None
    json_default = argparse.SUPPRESS if suppress_defaults else False
    parser.add_argument(
        "--project",
        default=project_default,
        help="Path to a .scriv package directory or a .scrivx file.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=json_default,
        help="Emit machine-readable JSON where practical.",
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ScrivenerError as exc:
        if getattr(args, "json", False):
            print(json.dumps({"ok": False, "error": str(exc)}, indent=2), file=sys.stderr)
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 1
    except BrokenPipeError:
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
