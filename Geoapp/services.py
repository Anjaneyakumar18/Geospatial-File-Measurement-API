import geopandas as gpd
import pandas as pd


def clean_value(value):
    """
    Convert Pandas / NumPy values into
    Django-template-safe values.
    """

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    if hasattr(value, "item"):
        try:
            value = value.item()
        except (ValueError, AttributeError):
            pass

    if isinstance(value, pd.Timestamp):

        if pd.isna(value):
            return None

        return value.isoformat()

    return value


def process_geospatial_file(file_path):

    # ---------------------------------------------------------
    # Read file
    # ---------------------------------------------------------

    gdf = gpd.read_file(file_path)

    if gdf.empty:
        raise ValueError(
            "The uploaded file contains no features."
        )

    # ---------------------------------------------------------
    # Original CRS
    # ---------------------------------------------------------

    original_crs = gdf.crs

    if original_crs:
        crs_string = original_crs.to_string()
    else:
        crs_string = "Unknown"

    # ---------------------------------------------------------
    # Measurement CRS
    # ---------------------------------------------------------

    if gdf.crs is None:

        measurement_gdf = gdf
        measurement_crs = None

    elif gdf.crs.is_geographic:

        measurement_crs = gdf.estimate_utm_crs()

        if measurement_crs is None:
            raise ValueError(
                "Could not determine a suitable projected CRS."
            )

        measurement_gdf = gdf.to_crs(
            measurement_crs
        )

    else:

        measurement_gdf = gdf
        measurement_crs = gdf.crs

    # ---------------------------------------------------------
    # Process features
    # ---------------------------------------------------------

    features = []

    for position, (_, row) in enumerate(
        gdf.iterrows()
    ):

        geometry = row.geometry

        projected_geometry = (
            measurement_gdf.iloc[position].geometry
        )

        # -----------------------------------------------------
        # Feature
        # -----------------------------------------------------

        feature = {

            "feature_id": position,

            "geometry_type": (
                geometry.geom_type
                if geometry is not None
                else "Unknown"
            ),

            "geometry": (
                geometry.wkt
                if geometry is not None
                else None
            ),

            "crs": crs_string,

            "properties": {}
        }

        # -----------------------------------------------------
        # Properties
        # -----------------------------------------------------

        for column in gdf.columns:

            if column == "geometry":
                continue

            value = clean_value(
                row[column]
            )

            # Don't show empty KML metadata
            if value is not None:

                feature["properties"][column] = value

        # -----------------------------------------------------
        # Measurement
        # -----------------------------------------------------

        if geometry is None:

            feature["measurement_type"] = None
            feature["measurement"] = None
            feature["unit"] = None
            feature["status"] = "NO_GEOMETRY"

        elif geometry.geom_type in [
            "Polygon",
            "MultiPolygon"
        ]:

            feature["measurement_type"] = "Area"

            feature["measurement"] = clean_value(
                projected_geometry.area
            )

            feature["unit"] = "m²"

            feature["status"] = "SUCCESS"

        elif geometry.geom_type in [
            "LineString",
            "MultiLineString"
        ]:

            feature["measurement_type"] = "Length"

            feature["measurement"] = clean_value(
                projected_geometry.length
            )

            feature["unit"] = "m"

            feature["status"] = "SUCCESS"

        elif geometry.geom_type in [
            "Point",
            "MultiPoint"
        ]:

            feature["measurement_type"] = None
            feature["measurement"] = None
            feature["unit"] = None

            feature["status"] = (
                "NO_MEASUREMENT_REQUIRED"
            )

        else:

            feature["measurement_type"] = None
            feature["measurement"] = None
            feature["unit"] = None

            feature["status"] = "NOT_SUPPORTED"

        features.append(feature)

    # ---------------------------------------------------------
    # Return result
    # ---------------------------------------------------------

    return {

        "feature_count": len(gdf),

        "crs": crs_string,

        "measurement_crs": (
            measurement_crs.to_string()
            if measurement_crs
            else None
        ),

        "features": features
    }