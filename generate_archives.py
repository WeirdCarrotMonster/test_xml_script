#!/usr/bin/env python3
import argparse
import os.path
import random
import xml.etree.ElementTree as et
import zipfile
from pathlib import Path
from uuid import uuid4

ARCHIVE_COUNT = 50
XML_COUNT = 100


def prepare_target_directory(dir_path: str) -> Path:
    path = Path(dir_path)

    if not os.path.exists(path):
        os.mkdir(path)
        return path

    if not os.path.isdir(path):
        raise Exception("Path is not a directory")

    if os.listdir(path):
        raise Exception("Directory is not empty")

    return path


def generate_random_id() -> str:
    return str(uuid4())


def generate_random_level() -> int:
    return random.randint(1, 100)


def generate_random_name() -> str:
    return str(uuid4())


def get_random_object_count() -> int:
    return random.randint(1, 10)


def generate_xml() -> et.Element:
    root = et.Element("root")
    et.SubElement(root, "val", name="id", value=generate_random_id())
    et.SubElement(root, "val", name="level", value=str(generate_random_level()))

    objects_element = et.SubElement(root, "objects")
    objects_count = get_random_object_count()

    for _ in range(objects_count):
        et.SubElement(objects_element, "object", name=generate_random_name())

    return root


def generate_xml_archive(archive_path: Path) -> None:
    xml_tree = generate_xml()

    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("data.xml", et.tostring(xml_tree))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=str, help="Path to directory for archives")
    parser.add_argument(
        "--archive-count",
        type=int,
        default=ARCHIVE_COUNT,
        help="Number of created archives",
    )
    parser.add_argument(
        "--xml-count",
        type=int,
        default=XML_COUNT,
        help="Number of XML files per archive",
    )

    args = parser.parse_args()

    target_directory = prepare_target_directory(args.target)
    for archive_id in range(args.archive_count):
        archive_name = f"{archive_id}.zip"
        archive_path = target_directory / archive_name
        generate_xml_archive(archive_path)


if __name__ == "__main__":
    main()
