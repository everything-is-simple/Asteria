from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile


def read_first_sheet(path: Path) -> list[list[str]]:
    with ZipFile(path) as zf:
        shared_strings = _read_shared_strings(zf)
        sheet_name = _first_sheet_name(zf)
        root = ElementTree.fromstring(zf.read(sheet_name))
    namespace = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    table: list[list[str]] = []
    for row in root.findall(".//x:sheetData/x:row", namespace):
        values: dict[int, str] = {}
        max_index = 0
        for cell in row.findall("x:c", namespace):
            ref = cell.attrib.get("r", "")
            column_index = _column_index(ref)
            max_index = max(max_index, column_index)
            values[column_index] = _cell_text(cell, shared_strings)
        table.append([values.get(index, "") for index in range(1, max_index + 1)])
    return table


def _read_shared_strings(zf: ZipFile) -> list[str]:
    try:
        root = ElementTree.fromstring(zf.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    namespace = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    values = []
    for item in root.findall("x:si", namespace):
        texts = [text.text or "" for text in item.findall(".//x:t", namespace)]
        values.append("".join(texts))
    return values


def _first_sheet_name(zf: ZipFile) -> str:
    if "xl/worksheets/sheet1.xml" in zf.namelist():
        return "xl/worksheets/sheet1.xml"
    return next(name for name in zf.namelist() if name.startswith("xl/worksheets/"))


def _cell_text(cell: ElementTree.Element, shared_strings: list[str]) -> str:
    namespace = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        texts = [text.text or "" for text in cell.findall(".//x:t", namespace)]
        return "".join(texts)
    value = cell.find("x:v", namespace)
    raw = "" if value is None or value.text is None else value.text
    if cell_type == "s" and raw:
        return shared_strings[int(raw)]
    return raw


def _column_index(ref: str) -> int:
    letters = "".join(char for char in ref if char.isalpha())
    index = 0
    for char in letters:
        index = index * 26 + ord(char.upper()) - 64
    return index
