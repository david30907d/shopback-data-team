"""
A simple ETL script for shopback
"""
import re
import csv
import json
from typing import Dict, List

import jieba
import defusedxml.ElementTree as ET


def _validate_url_of_specific_field(datawarehouse_field_name, raw_field_name):
    def _closure(row):
        assert "http" in row[raw_field_name]
        return [(datawarehouse_field_name, row[raw_field_name])]

    return _closure


CSV_FIELD_MAPPING = {
    "item_id": lambda x: [("product_id", x["item_id"])],
    "name": lambda x: [
        ("product_title", x["name"]),
        ("segmented_product_title", jieba.lcut(x["name"])),
    ],
    "brand": lambda x: [("brand", x["brand"])],
    "product_url": _validate_url_of_specific_field("url", "product_url"),
    "image_url": _validate_url_of_specific_field("image_url", "image_url"),
    "price": lambda x: [("price", x["price"])],
    "shop_name": lambda x: [("merchant", x["shop_name"])],
    "_extra": lambda _: [("seller", "")],
}


XML_FIELD_MAPPING = {
    "ProductID": lambda x: [("product_id", x)],
    "ProductName": lambda x: [
        ("product_title", x),
        (
            "merchant",
            re.search(r"【(.+?)】", x).group(1) if re.search(r"【(.+?)】", x) else "",
        ),
        ("segmented_product_title", jieba.lcut(x)),
    ],
    "ProductSalePrice": lambda x: [("price", x)],
    "ProductImage": lambda x: [("image_url", x)],
    "BuyURL": lambda x: [("url", x)],
    "_extra": lambda _: [("seller", ""), ("brand", "")],
}


def parse_csv(filename: str) -> List[Dict[str, str]]:
    result = []
    with open(filename, "r") as csvfile:
        rows = csv.DictReader(csvfile)
        for row in rows:
            payload = []
            for key, handler in CSV_FIELD_MAPPING.items():
                if key in row:
                    payload += handler(row)
            # add extra fields
            payload += CSV_FIELD_MAPPING["_extra"](None)
            result.append(dict(payload))
    return result


def parse_xml(filename: str) -> List[Dict[str, str]]:
    tree = ET.parse(filename)
    root = tree.getroot()
    result = []
    for product in root.findall("product"):
        payload = []
        for element in product.iter():
            if element.tag in XML_FIELD_MAPPING:
                payload += XML_FIELD_MAPPING[element.tag](element.text)
        # add extra fields
        payload += XML_FIELD_MAPPING["_extra"](None)
        result.append(dict(payload))
    return result


if __name__ == "__main__":
    RESULT = []
    RESULT += parse_csv("sb_a.csv")
    RESULT += parse_xml("sb_b.xml")
    json.dump(RESULT, open("sb.json", "w"))
