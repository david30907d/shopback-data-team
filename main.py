"""
A simple ETL script for shopback
"""
import re
import csv
import json
from abc import ABC, abstractmethod
from typing import Dict, List

import jieba
import defusedxml.ElementTree as ET


class BaseParser(ABC):
    """
    Abstract parser
    """

    @abstractmethod
    def parse(self, filename: str):
        pass


class CsvParser(BaseParser):
    """
    Parser for csv and transform them into uniform format
    """

    def __init__(self):
        self._field_mapping = {
            "item_id": lambda x: [("product_id", x["item_id"])],
            "name": lambda x: [
                ("product_title", x["name"]),
                ("segmented_product_title", jieba.lcut(x["name"])),
            ],
            "brand": lambda x: [("brand", x["brand"])],
            "product_url": self._validate_url_of_specific_field("url", "product_url"),
            "image_url": self._validate_url_of_specific_field("image_url", "image_url"),
            "price": lambda x: [("price", x["price"])],
            "shop_name": lambda x: [("merchant", x["shop_name"])],
            "_extra": lambda _: [("seller", "")],
        }

    @property
    def field_mapping(self):
        return self._field_mapping

    @staticmethod
    def _validate_url_of_specific_field(datawarehouse_field_name, raw_field_name):
        def _closure(row):
            assert "http" in row[raw_field_name]
            return [(datawarehouse_field_name, row[raw_field_name])]

        return _closure

    def parse(self, filename: str) -> List[Dict[str, str]]:
        result = []
        with open(filename, "r") as csvfile:
            rows = csv.DictReader(csvfile)
            for row in rows:
                payload = []
                for key, handler in self.field_mapping.items():
                    if key in row:
                        payload += handler(row)
                # add extra fields
                payload += self.field_mapping["_extra"](None)
                result.append(dict(payload))
        return result


class XmlParser(BaseParser):
    """
    Parser for xml and transform them into uniform format
    """

    def __init__(self):
        self._field_mapping = {
            "ProductID": lambda x: [("product_id", x)],
            "ProductName": lambda x: [
                ("product_title", x),
                (
                    "merchant",
                    re.search(r"【(.+?)】", x).group(1)
                    if re.search(r"【(.+?)】", x)
                    else "",
                ),
                ("segmented_product_title", jieba.lcut(x)),
            ],
            "ProductSalePrice": lambda x: [("price", x)],
            "ProductImage": lambda x: [("image_url", x)],
            "BuyURL": lambda x: [("url", x)],
            "_extra": lambda _: [("seller", ""), ("brand", "")],
        }

    @property
    def field_mapping(self):
        return self._field_mapping

    def parse(self, filename: str) -> List[Dict[str, str]]:
        tree = ET.parse(filename)
        root = tree.getroot()
        result = []
        for product in root.findall("product"):
            payload = []
            for element in product.iter():
                if element.tag in self.field_mapping:
                    payload += self.field_mapping[element.tag](element.text)
            # add extra fields
            payload += self.field_mapping["_extra"](None)
            result.append(dict(payload))
        return result


if __name__ == "__main__":
    csv_parser = CsvParser()
    xml_parser = XmlParser()
    RESULT = []
    RESULT += csv_parser.parse("sb_a.csv")
    RESULT += xml_parser.parse("sb_b.xml")
    json.dump(RESULT, open("sb.json", "w"))
