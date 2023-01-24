import unittest
from datetime import datetime

from pystac.extensions.raster import DataType, RasterExtension
from pystac.extensions.scientific import ItemScientificExtension

from stactools.naip.stac import create_collection, create_item
from tests import test_data


class StacTest(unittest.TestCase):
    def test_create_collection(self):
        collection = create_collection(seasons=[2011, 2013, 2015, 2017, 2019])

        collection.set_self_href("http://example.com/collection.json")
        collection.validate()

    def test_create_item_txt(self):
        item = create_item(
            "al",
            "2011",
            test_data.get_path("data-files/m_3008501_ne_16_1_20110815-downsampled.tif"),
            test_data.get_path("data-files/m_3008501_ne_16_1_20110815.txt"),
        )

        image_asset = item.assets["image"]
        raster_ext = RasterExtension.ext(image_asset)
        self.assertEqual(len(raster_ext.bands), 4)
        for raster_band in RasterExtension.ext(image_asset).bands:
            self.assertEqual(raster_band.nodata, 0)
            self.assertEqual(raster_band.spatial_resolution, item.properties["gsd"])
            self.assertEqual(raster_band.data_type, DataType.UINT8)
            self.assertEqual(raster_band.unit, "none")

        sci_ext = ItemScientificExtension.ext(item)

        self.assertEqual(sci_ext.doi, "10.5066/F7QN651G")
        self.assertGreaterEqual(len(sci_ext.publications), 1)

    def test_create_item_xml(self):
        item = create_item(
            "tx",
            "2020",
            test_data.get_path(
                "data-files/m_3610332_se_13_060_20200903-downsampled.tif"
            ),
            test_data.get_path("data-files/m_3610332_se_13_060_20200903_20201204.xml"),
        )

        image_asset = item.assets["image"]
        raster_ext = RasterExtension.ext(image_asset)
        self.assertEqual(len(raster_ext.bands), 4)
        for raster_band in RasterExtension.ext(image_asset).bands:
            self.assertEqual(raster_band.nodata, 0)
            self.assertEqual(raster_band.spatial_resolution, item.properties["gsd"])
            self.assertEqual(raster_band.data_type, DataType.UINT8)
            self.assertEqual(raster_band.unit, "none")

        sci_ext = ItemScientificExtension.ext(item)

        self.assertEqual(sci_ext.doi, "10.5066/F7QN651G")
        self.assertGreaterEqual(len(sci_ext.publications), 1)

        self.assertEqual(type(item.datetime), datetime)
        self.assertEqual(type(item.id), str)
