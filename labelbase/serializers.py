from rest_framework import serializers
from labelbase.models import Labelbase, Label


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = [
            "id",
            "labelbase",
            "type",
            "ref",
            "label",
        ]
        read_only_fields = [
            "id",
        ]


class LabelbaseSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super(LabelbaseSerializer, self).__init__(*args, **kwargs)
        self.request = self.context.get("request")

    class Meta:
        model = Labelbase
        fields = [
            "id",
            "name",
            "fingerprint",
            "about",
        ]
        read_only_fields = [
            "id",
            "user",
        ]

    def create(self, validated_data):
        obj = Labelbase(**validated_data)
        obj.user_id = self.request.user.id
        obj.save()
        return obj
