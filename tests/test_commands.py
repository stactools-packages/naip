import os
from tempfile import TemporaryDirectory

import pystac
from stactools.testing import CliTestCase

from stactools.naip.commands import create_naip_command
from tests import test_data


class CreateItemTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_naip_command]

    def test_create_item_txt(self):
        fgdc_href = test_data.get_path("data-files/m_3008501_ne_16_1_20110815.txt")
        cog_href = test_data.get_path("data-files/m_3008501_ne_16_1_20110815.tif")

        with TemporaryDirectory() as tmp_dir:
            cmd = [
                "naip",
                "create-item",
                "al",
                "2011",
                cog_href,
                "--fgdc",
                fgdc_href,
                tmp_dir,
            ]
            self.run_command(cmd)

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
            self.assertEqual(len(jsons), 1)

            item_path = os.path.join(tmp_dir, jsons[0])

            item = pystac.Item.from_file(item_path)

        item.validate()

    def test_create_item_no_resource_desc(self):
        fgdc_href = test_data.get_path("data-files/m_4207201_ne_18_h_20160809.txt")
        cog_href = (
            "https://naipeuwest.blob.core.windows.net/"
            "naip/v002/vt/2016/vt_060cm_2016/42072/m_4207201_ne_18_h_20160809.tif"
        )

        with TemporaryDirectory() as tmp_dir:
            cmd = [
                "naip",
                "create-item",
                "al",
                "2016",
                cog_href,
                "--fgdc",
                fgdc_href,
                tmp_dir,
            ]
            self.run_command(cmd)

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
            self.assertEqual(len(jsons), 1)

            item_path = os.path.join(tmp_dir, jsons[0])

            item = pystac.read_file(item_path)

        item.validate()

    def test_create_item_no_fgdc(self):
        cog_href = (
            "https://naipeuwest.blob.core.windows.net/"
            "naip/v002/ar/2010/ar_100cm_2010/33093/m_3309302_sw_15_1_20100623.tif"
        )

        with TemporaryDirectory() as tmp_dir:
            cmd = ["naip", "create-item", "al", "2016", cog_href, tmp_dir]
            self.run_command(cmd)

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
            self.assertEqual(len(jsons), 1)

            item_path = os.path.join(tmp_dir, jsons[0])

            item = pystac.read_file(item_path)

        item.validate()

    def test_create_item_xml(self):
        fgdc_href = test_data.get_path(
            "data-files/m_3610332_se_13_060_20200903_20201204.xml"
        )
        cog_href = test_data.get_path(
            "data-files/m_3610332_se_13_060_20200903-downsampled.tif"
        )
        with TemporaryDirectory() as tmp_dir:
            cmd = [
                "naip",
                "create-item",
                "tx",
                "2020",
                cog_href,
                "--fgdc",
                fgdc_href,
                tmp_dir,
            ]
            self.run_command(cmd)

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
            self.assertEqual(len(jsons), 1)

            item_path = os.path.join(tmp_dir, jsons[0])

            item = pystac.Item.from_file(item_path)

        item.validate()
