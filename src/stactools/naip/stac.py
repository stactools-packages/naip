import itertools
import os
import re
from datetime import timedelta
from typing import Final, List, Optional, Pattern

import fsspec
import pystac
import rasterio as rio
import shapely
from lxml import etree
from pystac.extensions.eo import EOExtension
from pystac.extensions.grid import GridExtension
from pystac.extensions.item_assets import ItemAssetsExtension
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.raster import DataType, RasterBand, RasterExtension
from pystac.extensions.scientific import CollectionScientificExtension, Publication
from pystac.utils import str_to_datetime
from stactools.core.io import read_text
from stactools.core.io.xml import XmlElement
from stactools.core.projection import reproject_geom

from stactools.naip import constants
from stactools.naip.utils import (
    maybe_extract_id_and_date,
    parse_fgdc_metadata,
    process_xpath_resource_desc,
)

DOQQ_PATTERN: Final[Pattern[str]] = re.compile(r"[A-Za-z]{2}_m_(\d{7})_(ne|se|nw|sw)_")


def naip_item_id(state, resource_name):
    """Generates a STAC Item ID based on the state and the "Resource Description"
    contained in the FGDC metadata.

    Args:
        state (str): The two-letter state code for the state this belongs to.
        resource_name (str): The resource name, e.g. m_3008501_ne_16_1_20110815_20111017.tif

    Returns:
        str: The STAC ID to use for this scene.
    """

    return "{}_{}".format(state, os.path.splitext(resource_name)[0])


def create_collection(seasons: List[int]) -> pystac.Collection:
    """Creates a STAC COllection for NAIP data.

    Args:
        seasons (List[int]): List of years that represent the NAIP seasons
            this collection represents.
    """
    extent = pystac.Extent(
        pystac.SpatialExtent(bboxes=[[-124.784, 24.744, -66.951, 49.346]]),
        pystac.TemporalExtent(
            intervals=[
                [
                    pystac.utils.str_to_datetime(f"{min(seasons)}-01-01T00:00:00Z"),
                    pystac.utils.str_to_datetime(f"{max(seasons)}-01-01T00:00:00Z"),
                ]
            ]
        ),
    )

    collection = pystac.Collection(
        id=constants.NAIP_ID,
        description=constants.NAIP_DESCRIPTION,
        title=constants.NAIP_TITLE,
        license=constants.NAIP_LICENSE,
        providers=[constants.USDA_PROVIDER],
        extent=extent,
        extra_fields={
            "item_assets": {
                "image": {
                    "eo:bands": [b.properties for b in constants.NAIP_BANDS],
                    "roles": ["data"],
                    "title": "RGBIR COG tile",
                    "type": pystac.MediaType.COG,
                },
            }
        },
    )

    # Scientific Extension
    sci_ext = CollectionScientificExtension.ext(collection, add_if_missing=True)
    sci_ext.doi = "10.5066/F7QN651G"

    pub_citation = """Maxwell, A. E., Warner, T. A., Vanderbilt, B. C., &amp; Ramezan, C. A.\n
    (2017). Land cover classification and feature extraction from National Agriculture Imagery\n
    Program (NAIP) orthoimagery: A Review. Photogrammetric Engineering &amp; Remote Sensing,\n
    83(11), 737-747. https://doi.org/10.14358/pers.83.10.737"""

    sci_ext.publications = [
        Publication("10.14358/PERS.83.10.737", " ".join(pub_citation.split()))
    ]

    # Item Asset Extension
    ItemAssetsExtension.add_to(collection)

    return collection


def create_item(
    state,
    year,
    cog_href,
    fgdc_metadata_href: Optional[str],
    thumbnail_href=None,
    additional_providers=None,
):
    """Creates a STAC Item from NAIP data.

    Args:
        state (str): The 2-letter state code for the state this item belongs to.
        year (str): The NAIP year.
        fgdc_metadata_href (str): The href to the FGDC metadata
            for this NAIP scene. Optional, a some NAIP scenes to not have this
            (e.g. 2010)
        cog_href (str): The href to the image as a COG. This needs
            to be an HREF that rasterio is able to open.
        thumbnail_href (str): Optional href for a thumbnail for this scene.
        additional_providers(List[pystac.Provider]): Optional list of additional
            providers to the USDA that will be included on this Item.

    This function will read the metadata file for information to place in
    the STAC item.

    Returns:
        pystac.Item: A STAC Item representing this NAIP scene.
    """

    with rio.open(cog_href) as ds:
        gsd = round(ds.res[0], 1)
        epsg = int(ds.crs.to_authority()[1])
        image_shape = list(ds.shape)
        original_bbox = list(ds.bounds)
        transform = list(ds.transform)
        geom = reproject_geom(
            ds.crs,
            "epsg:4326",
            shapely.geometry.mapping(shapely.geometry.box(*ds.bounds)),
            precision=6,
        )

    if fgdc_metadata_href is not None:
        if year == "2020":
            first_xpath = "gmd:fileIdentifier/gco:CharacterString"

            second_xpath = "idinfo/citation/citeinfo/title"

            with fsspec.open(fgdc_metadata_href) as file:
                root = XmlElement(
                    etree.parse(file, base_url=fgdc_metadata_href).getroot()
                )
                try:
                    resource_desc = root.find_text(first_xpath)
                except SyntaxError:
                    resource_desc = root.find_text(second_xpath)

                if resource_desc is not None:
                    resource_desc = process_xpath_resource_desc(resource_desc)
                    dt = str_to_datetime(resource_desc.split("_")[-1])
                else:
                    res = maybe_extract_id_and_date(cog_href)
                    if res is not None:
                        resource_desc, dt = res
                    else:
                        raise Exception(
                            f"Failed to extract item resource_desc and dt: {cog_href}"
                        )

        elif year < "2020":
            fgdc_metadata_text = read_text(fgdc_metadata_href)
            fgdc = parse_fgdc_metadata(fgdc_metadata_text)
            try:
                resource_desc = fgdc["Distribution_Information"]["Resource_Description"]
                dt = str_to_datetime(
                    fgdc["Identification_Information"]["Time_Period_of_Content"][
                        "Time_Period_Information"
                    ]["Single_Date/Time"]["Calendar_Date"]
                )
            except KeyError:
                res = maybe_extract_id_and_date(cog_href)
                if res is not None:
                    resource_desc, dt = res
                else:
                    raise Exception(
                        f"Failed to extract item resource_desc and dt: {cog_href}"
                    )
        else:
            raise Exception(f"Metadata for year {year} is not supported.")

    else:
        res = maybe_extract_id_and_date(cog_href)
        if res is not None:
            resource_desc, dt = res
        else:
            raise Exception(f"Failed to extract item resource_desc and dt: {cog_href}")

    item_id = naip_item_id(state, resource_desc)

    shapely_shape = shapely.geometry.shape(geom)
    bounds = list(shapely_shape.bounds)
    centroid = shapely_shape.centroid

    dt = dt + timedelta(hours=16)  # UTC is +4 ET, so is around 9-12 AM in CONUS
    properties = {"naip:state": state, "naip:year": year}

    item = pystac.Item(
        id=item_id, geometry=geom, bbox=bounds, datetime=dt, properties=properties
    )

    # Common metadata
    item.common_metadata.providers = [constants.USDA_PROVIDER]
    if additional_providers is not None:
        item.common_metadata.providers.extend(additional_providers)
    item.common_metadata.gsd = gsd

    # EO Extension, for asset bands
    EOExtension.add_to(item)

    # Projection Extension
    projection = ProjectionExtension.ext(item, add_if_missing=True)
    projection.epsg = epsg
    projection.shape = image_shape
    projection.bbox = original_bbox
    projection.transform = transform
    projection.centroid = {"lat": round(centroid.y, 5), "lon": round(centroid.x, 5)}

    # Grid Extension
    grid = GridExtension.ext(item, add_if_missing=True)
    if match := DOQQ_PATTERN.search(item_id):
        grid.code = f"DOQQ-{match.group(1)}{match.group(2).upper()}"

    # COG
    item.add_asset(
        "image",
        pystac.Asset(
            href=cog_href,
            media_type=pystac.MediaType.COG,
            roles=["data"],
            title="RGBIR COG tile",
        ),
    )

    # Metadata
    if fgdc_metadata_href is not None:
        item.add_asset(
            "metadata",
            pystac.Asset(
                href=fgdc_metadata_href,
                media_type=pystac.MediaType.TEXT,
                roles=["metadata"],
                title="FGDC Metadata",
            ),
        )

    if thumbnail_href is not None:
        media_type = pystac.MediaType.JPEG
        if thumbnail_href.lower().endswith("png"):
            media_type = pystac.MediaType.PNG
        item.add_asset(
            "thumbnail",
            pystac.Asset(
                href=thumbnail_href,
                media_type=media_type,
                roles=["thumbnail"],
                title="Thumbnail",
            ),
        )

    image_asset = item.assets["image"]

    # EO Extension
    asset_eo = EOExtension.ext(image_asset)
    asset_eo.bands = constants.NAIP_BANDS

    # Raster Extension
    RasterExtension.ext(image_asset, add_if_missing=True).bands = list(
        itertools.repeat(
            RasterBand.create(
                nodata=0,
                spatial_resolution=gsd,
                data_type=DataType.UINT8,
                unit="none",
            ),
            4,
        )
    )

    return item
