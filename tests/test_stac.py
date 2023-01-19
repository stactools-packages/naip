import unittest

from stactools.naip.stac import create_collection, create_item
from tests import test_data


class StacTest(unittest.TestCase):
    def test_create_collection(self):
        collection = create_collection(seasons=[2011, 2013, 2015, 2017, 2019])

        collection.set_self_href("http://example.com/collection.json")
        collection.validate()

    def test_create_item(self):
        item = create_item(
            "al",
            "2011",
            test_data.get_path("data-files/m_3008501_ne_16_1_20110815-downsampled.tif"),
            test_data.get_path("data-files/m_3008501_ne_16_1_20110815.txt"),
        )

        self.assertEqual(item.properties["sci:doi"], "10.5066/F7QN651G")
