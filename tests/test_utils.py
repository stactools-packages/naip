import unittest

import dateutil.parser

from stactools.naip.utils import maybe_extract_id_and_date, parse_fgdc_metadata
from tests import test_data

# Test cases, file names to keys and values that should exist.
FGDC_FILES = {
    "m_4107212_se_18_060_20180816.txt": {
        "Distribution_Information": {
            "Resource_Description": "m_4107212_se_18_060_20180816_20181211.tif"
        },
        "Identification_Information": {
            "Spatial_Domain": {
                "Bounding_Coordinates": {
                    "West_Bounding_Coordinate": "-72.5625",
                    "East_Bounding_Coordinate": "-72.5000",
                    "North_Bounding_Coordinate": "41.8125",
                    "South_Bounding_Coordinate": "41.7500",
                }
            }
        },
    }
}


WRONG_COG_HREF = (
    "s3://naip-analytic/tx/2020/60cm/rgbir_cog/35102/m_3510264_13_ne_060_20200905.tif"
)
CORRECT_COG_HREF = (
    "s3://naip-analytic/tx/2020/60cm/rgbir_cog/35102/m_3510264_ne_13_060_20200905.tif"
)


class UtilsTest(unittest.TestCase):
    def check_values(self, actual_dict, expected_dict):
        for k in expected_dict:
            self.assertIn(k, actual_dict)
            actual_value = actual_dict[k]
            expected_value = expected_dict[k]
            self.assertEqual(type(actual_value), type(expected_value))
            if type(actual_value) is dict:
                self.check_values(actual_value, expected_value)
            else:
                self.assertEqual(actual_value, expected_value)

    def test_parses_fgdc(self):
        for test_file, expected in FGDC_FILES.items():
            path = test_data.get_path("data-files/{}".format(test_file))
            with self.subTest(test_file):
                with open(path) as f:
                    fgdc_txt = f.read()
                actual = parse_fgdc_metadata(fgdc_txt)
                self.check_values(actual, expected)

    def test_extract_id_datetime(self):
        wrong_res = maybe_extract_id_and_date(WRONG_COG_HREF)
        correct_res = maybe_extract_id_and_date(CORRECT_COG_HREF)
        self.assertEqual(wrong_res, None)
        self.assertEqual(correct_res[0], ("m_3510264_ne_13_060_20200905.tif"))
        self.assertEqual(correct_res[1], dateutil.parser.isoparse("20200905"))
