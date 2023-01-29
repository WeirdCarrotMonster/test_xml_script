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


def prepare_target_directory(dir_path: Path) -> None:
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    if not os.path.isdir(dir_path):
        raise Exception("Path is not a directory")

    if os.listdir(dir_path):
        raise Exception("Directory is not empty")


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
    et.SubElement(root, "var", name="id", value=generate_random_id())
    et.SubElement(root, "var", name="level", value=str(generate_random_level()))

    objects_element = et.SubElement(root, "objects")
    objects_count = get_random_object_count()

    for _ in range(objects_count):
        et.SubElement(objects_element, "object", name=generate_random_name())

    return root


def generate_xml_archive(archive_path: Path, xml_count: int) -> None:
    with zipfile.ZipFile(archive_path, "w") as archive:
        for xml_index in range(xml_count):
            xml_tree = generate_xml()
            archive.writestr(f"{xml_index}.xml", et.tostring(xml_tree))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=Path, help="Path to directory for archives")
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

    prepare_target_directory(args.target)
    for archive_id in range(args.archive_count):
        archive_name = f"{archive_id}.zip"
        archive_path = args.target / archive_name
        generate_xml_archive(archive_path, args.xml_count)


if __name__ == "__main__":
    main()
