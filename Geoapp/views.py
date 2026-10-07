from django.shortcuts import (
    render,
    get_object_or_404
)

from rest_framework.decorators import (
    api_view,
    parser_classes
)

from rest_framework.parsers import (
    MultiPartParser,
    FormParser
)

from rest_framework.response import Response

from rest_framework import status

from .models import GeoFile

from .services import (
    process_geospatial_file
)


# ============================================================
# HOME PAGE
# ============================================================

def home(request):

    return render(
        request,
        "Geoapp/home.html"
    )


# ============================================================
# RESULT PAGE
# ============================================================

def file_details(request, file_id):

    geo_file = get_object_or_404(
        GeoFile,
        id=file_id
    )

    return render(
        request,
        "Geoapp/file_details.html",
        {
            "file": geo_file
        }
    )


def measurements(request, file_id):

    geo_file = get_object_or_404(
        GeoFile,
        id=file_id
    )

    result_data = None

    if geo_file.status == "COMPLETED":

        result_data = process_geospatial_file(
            geo_file.file.path
        )

    return render(
        request,
        "Geoapp/measurements.html",
        {
            "file": geo_file,
            "result": result_data
        }
    )


def result(request, file_id):

    geo_file = get_object_or_404(
        GeoFile,
        id=file_id
    )

    result_data = None

    if geo_file.status == "COMPLETED":

        result_data = process_geospatial_file(
            geo_file.file.path
        )

    return render(
        request,
        "Geoapp/result.html",
        {
            "file": geo_file,
            "result": result_data
        }
    )


# ============================================================
# API 1
# POST /api/files/
# ============================================================

@api_view(["POST"])
@parser_classes([
    MultiPartParser,
    FormParser
])
def upload_file_api(request):

    uploaded_file = request.FILES.get(
        "file"
    )

    if not uploaded_file:

        return Response(
            {
                "error":
                    "Please upload a file using the 'file' field."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    filename = uploaded_file.name.lower()

    # Only KML and ZIP
    if not (
        filename.endswith(".kml")
        or filename.endswith(".zip")
    ):

        return Response(
            {
                "error":
                    "Only .kml files and .zip Shapefiles are supported."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create database record
    geo_file = GeoFile.objects.create(

        file=uploaded_file,

        filename=uploaded_file.name,

        status="PROCESSING"
    )

    try:

        # Process file
        result_data = process_geospatial_file(
            geo_file.file.path
        )

        # Update database
        geo_file.feature_count = (
            result_data["feature_count"]
        )

        geo_file.crs = (
            result_data["crs"]
        )

        geo_file.measurement_crs = (
            result_data["measurement_crs"]
        )

        geo_file.status = "COMPLETED"

        geo_file.save()

        return Response(

            {
                "id": str(
                    geo_file.id
                ),

                "filename":
                    geo_file.filename,

                "status":
                    geo_file.status,

                "feature_count":
                    geo_file.feature_count,

                "crs":
                    geo_file.crs,

                "measurement_crs":
                    geo_file.measurement_crs,

                "detail_url":
                    f"/api/files/{geo_file.id}/",

                "measurements_url":
                    f"/api/files/{geo_file.id}/measurements/",

                "result_url":
                    f"/result/{geo_file.id}/"
            },

            status=status.HTTP_201_CREATED
        )

    except Exception as e:

        geo_file.status = "FAILED"

        geo_file.error_message = str(e)

        geo_file.save()

        return Response(

            {
                "id":
                    str(geo_file.id),

                "status":
                    "FAILED",

                "error":
                    str(e)
            },

            status=status.HTTP_400_BAD_REQUEST
        )


# ============================================================
# API 2
# GET /api/files/{id}/
# ============================================================

@api_view(["GET"])
def get_file_api(
    request,
    file_id
):

    try:

        geo_file = GeoFile.objects.get(
            id=file_id
        )

    except GeoFile.DoesNotExist:

        return Response(

            {
                "error":
                    "File not found."
            },

            status=status.HTTP_404_NOT_FOUND
        )

    return Response(

        {
            "id":
                str(geo_file.id),

            "filename":
                geo_file.filename,

            "feature_count":
                geo_file.feature_count,

            "crs":
                geo_file.crs,

            "measurement_crs":
                geo_file.measurement_crs,

            "status":
                geo_file.status,

            "error":
                geo_file.error_message,

            "created_at":
                geo_file.created_at
        }
    )


# ============================================================
# API 3
# GET /api/files/{id}/measurements/
# ============================================================

@api_view(["GET"])
def get_measurements_api(
    request,
    file_id
):

    try:

        geo_file = GeoFile.objects.get(
            id=file_id
        )

    except GeoFile.DoesNotExist:

        return Response(

            {
                "error":
                    "File not found."
            },

            status=status.HTTP_404_NOT_FOUND
        )

    if geo_file.status != "COMPLETED":

        return Response(

            {
                "error":
                    "File has not been processed successfully.",

                "status":
                    geo_file.status
            },

            status=status.HTTP_400_BAD_REQUEST
        )

    try:

        result_data = process_geospatial_file(
            geo_file.file.path
        )

        return Response(

            {
                "id":
                    str(geo_file.id),

                "filename":
                    geo_file.filename,

                "feature_count":
                    result_data["feature_count"],

                "crs":
                    result_data["crs"],

                "measurement_crs":
                    result_data["measurement_crs"],

                "features":
                    result_data["features"]
            }
        )

    except Exception as e:

        return Response(

            {
                "error":
                    str(e)
            },

            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    