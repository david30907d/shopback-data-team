"""
test main.py
"""
from main import CsvParser, XmlParser


def test_csv_parser():
    csv_parser = CsvParser()
    if __debug__:
        if not isinstance(csv_parser.parse("sb_a.csv"), list):
            raise AssertionError("Parsing Error!")


def test_xml_parser():
    xml_parser = XmlParser()
    if __debug__:
        if not isinstance(xml_parser.parse("sb_b.xml"), list):
            raise AssertionError("Parsing Error!")
