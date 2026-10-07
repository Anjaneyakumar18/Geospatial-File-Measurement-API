from rest_framework import serializers
from .models import GeoFile


class GeoFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = GeoFile
        fields = [
            "id",
            "filename",
            "feature_count",
            "crs",
            "status",
            "created_at"
        ]