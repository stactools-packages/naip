import unittest
from datetime import datetime, timedelta

from pystac.extensions.raster import DataType, RasterExtension
from pystac.extensions.scientific import CollectionScientificExtension
from pystac.utils import str_to_datetime

from stactools.naip.stac import create_collection, create_item
from tests import test_data


class StacTest(unittest.TestCase):
    def test_create_collection(self):
        collection = create_collection(seasons=[2011, 2013, 2015, 2017, 2019])

        sci_ext = CollectionScientificExtension.ext(collection)

        self.assertEqual(sci_ext.doi, "10.5066/F7QN651G")
        self.assertGreaterEqual(len(sci_ext.publications), 1)

        collection.set_self_href("http://example.com/collection.json")
        collection.validate()

    # test stac on years < 2020
    def test_create_item_txt(self):
        item = create_item(
            "al",
            "2011",
            test_data.get_path("data-files/m_3008501_ne_16_1_20110815.tif"),
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

    # test stac on year = 2020
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

        self.assertEqual(type(item.datetime), datetime)
        self.assertEqual(type(item.id), str)

    # test stac on year 2011
    # resource description key is missing from the metadata
    def test_incorrect_metadata_txt(self):
        item = create_item(
            "al",
            "2011",
            test_data.get_path("data-files/m_3008501_ne_16_1_20110815.tif"),
            test_data.get_path("data-files/m_3008501_ne_16_1_20110815_incorrect.txt"),
        )

        self.assertEqual(item.id, "al_m_3008501_ne_16_1_20110815")
        self.assertEqual(
            item.datetime, str_to_datetime("20110815") + timedelta(hours=16)
        )

    # test stac on year 2020
    # updated resource description location in xml
    def test_create_item_xml_grid_code(self):
        item = create_item(
            "wi",
            "2020",
            test_data.get_path("data-files/m_4208701_ne_16_060_20200902.tif"),
            test_data.get_path("data-files/m_4208701_ne_16_060_20200902_20201202.xml"),
        )

        self.assertEqual(item.id, "wi_m_4208701_ne_16_060_20200902")
        self.assertEqual(
            item.datetime, str_to_datetime("20200902") + timedelta(hours=16)
        )

    # test stac on year 2020
    # handles resource desc from xml (with and without ".tif" extension)
    # handles resource desc pulled from cog_href
    def test_create_item_xml_ext(self):
        for filename in [
            "data-files/m_3211605_ne_11_060_20200415_20200730.xml",
            "data-files/m_3211605_ne_11_060_20200415_20200730_missing_resource_desc.xml",
        ]:

            item = create_item(
                "ca",
                "2020",
                test_data.get_path("data-files/m_3211605_ne_11_060_20200415.tif"),
                test_data.get_path(filename),
            )

            self.assertEqual(item.id, "ca_m_3211605_ne_11_060_20200415")
            self.assertEqual(
                item.datetime, str_to_datetime("20200415") + timedelta(hours=16)
            )
