import uuid

from django.db import models


class GeoFile(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    file = models.FileField(
        upload_to="geospatial/"
    )

    filename = models.CharField(
        max_length=255
    )

    feature_count = models.IntegerField(
        default=0
    )

    crs = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    measurement_crs = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        default="PROCESSING"
    )

    error_message = models.TextField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.filename