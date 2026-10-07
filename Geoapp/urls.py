from django.urls import path

from .views import (
    home,
    result,
    upload_file_api,
    get_file_api,
    get_measurements_api,
    file_details,
    measurements
)


urlpatterns = [

    # ========================================================
    # HTML
    # ========================================================

    path(
        "",
        home,
        name="home"
    ),

    path(
        "result/<uuid:file_id>/",
        result,
        name="result"
    ),


    # ========================================================
    # REST API
    # ========================================================

    # POST /api/files/
    path(
        "api/files/",
        upload_file_api,
        name="api-upload-file"
    ),

    # GET /api/files/<id>/
    path(
        "api/files/<uuid:file_id>/",
        get_file_api,
        name="api-file-detail"
    ),

    # GET /api/files/<id>/measurements/
    path(
        "api/files/<uuid:file_id>/measurements/",
        get_measurements_api,
        name="api-file-measurements"
    ),
    path(
    "file-details/<uuid:file_id>/",
    file_details,
    name="file-details"
),

path(
    "measurements/<uuid:file_id>/",
    measurements,
    name="measurements"
),

]