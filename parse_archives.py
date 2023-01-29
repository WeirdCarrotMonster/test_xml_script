#!/usr/bin/env python3
import argparse
import csv
import logging
import os.path
import xml.etree.ElementTree as et
import zipfile
from dataclasses import dataclass
from multiprocessing.pool import Pool
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ArchiveData:
    id: str
    level: int
    object_names: list[str]


def get_archive_file_paths(src_dir: Path) -> list[Path]:
    if not os.path.exists(src_dir):
        raise Exception("Source directory does not exist")

    if not os.path.isdir(src_dir):
        raise Exception("Source path is not a directory")

    # Assuming each file in source directory is an archive
    return [src_dir / _ for _ in os.listdir(src_dir)]


def parse_xml(tree: et.ElementTree) -> ArchiveData:
    id_elem = tree.findall("./var[@name='id']")[0]
    level_elem = tree.findall("./var[@name='level']")[0]
    object_elements = tree.findall("./objects/object")

    level_value = int(level_elem.get("value"))

    id_value = id_elem.get("value")
    if not id_value:
        raise ValueError("Invalid level value")

    object_names = [obj.get("name") for obj in object_elements]
    if not all([name for name in object_names]):
        raise ValueError("Invalid object name")

    return ArchiveData(
        id=id_value,
        level=level_value,
        object_names=object_names,
    )


def parse_archive(archive_path: Path) -> ArchiveData | None:
    try:
        with zipfile.ZipFile(archive_path, "r") as archive:
            with archive.open("data.xml", "r") as data_xml:
                tree = et.parse(data_xml)
    except Exception as error:
        logger.exception("Failed to read XML from archive: %s", error)
        return None

    try:
        result = parse_xml(tree)
    except Exception as error:
        logger.exception("Failed to parse XML structure: %s", error)
        return None

    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("src_dir", type=Path, help="Path to directory with archives")
    parser.add_argument(
        "level_csv", type=argparse.FileType("w"), help="Path to level CSV"
    )
    parser.add_argument(
        "object_csv", type=argparse.FileType("w"), help="Path to objects CSV"
    )
    parser.add_argument(
        "--processes", type=int, default=None, help="Number of parser processes"
    )

    args = parser.parse_args()

    archive_files = get_archive_file_paths(args.src_dir)

    level_csv = csv.writer(args.level_csv)
    object_csv = csv.writer(args.object_csv)

    process_pool = Pool(processes=args.processes)

    for result in process_pool.imap_unordered(parse_archive, archive_files):
        level_csv.writerow([result.id, result.level])

        for object_name in result.object_names:
            object_csv.writerow([result.id, object_name])


if __name__ == "__main__":
    main()
