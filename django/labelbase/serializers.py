import json
from rest_framework import serializers
from labelbase.models import Labelbase, Label


class LabelSerializer_v1(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = [
            "id",
            "labelbase",
            "type",
            "ref",
            "label",
            "origin",
            "spendable",
        ]
        read_only_fields = [
            "id",
        ]


class LabelSerializer(serializers.ModelSerializer):
    # Additional BIP-329 fields
    height = serializers.IntegerField(required=False, allow_null=True)
    time = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    fee = serializers.IntegerField(required=False, allow_null=True)
    value = serializers.IntegerField(required=False, allow_null=True)
    rate = serializers.JSONField(required=False, allow_null=True)
    keypath = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    fmv = serializers.JSONField(required=False, allow_null=True)
    heights = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Label
        fields = [
            "id",
            "labelbase",
            "type",
            "ref",
            "label",
            "origin",
            "spendable", 
            # Additional BIP-329 fields
            "height",
            "time",
            "fee",
            "value",
            "rate",
            "keypath",
            "fmv",
            "heights",
        ]
        read_only_fields = [
            "id",
        ]

    def validate(self, data):
        """Validate BIP-329 field combinations based on type"""
        label_type = data.get('type')

        # Define valid fields per type (from BIP-329 spec)
        valid_fields = {
            'tx': {'height', 'time', 'fee', 'value', 'rate'},
            'addr': {'keypath', 'heights'},
            'pubkey': {'keypath'},
            'input': {'keypath', 'value', 'fmv', 'height', 'time'},
            'output': {'spendable', 'keypath', 'value', 'fmv', 'height', 'time'},
            'xpub': set()
        }

        # Get allowed additional fields for this type
        allowed = valid_fields.get(label_type, set())

        # Check for invalid field combinations
        additional_fields = {'height', 'time', 'fee', 'value', 'rate', 'keypath', 'fmv', 'heights', 'spendable'}
        for field in additional_fields:
            if field in data and data[field] is not None:
                # Allow origin for all types
                if field == 'origin':
                    continue
                # Check if field is valid for this type
                if field not in allowed and field in additional_fields - {'origin'}:
                    # Remove invalid field instead of raising error (for compatibility)
                    data.pop(field, None)

        return data

    def create(self, validated_data):
        """Override create to convert data types for storage"""
        # Convert integers to strings for storage
        if 'height' in validated_data and validated_data['height'] is not None:
            validated_data['height'] = str(validated_data['height'])

        if 'fee' in validated_data and validated_data['fee'] is not None:
            validated_data['fee'] = str(validated_data['fee'])

        if 'value' in validated_data and validated_data['value'] is not None:
            validated_data['value'] = str(validated_data['value'])

        # Convert JSON objects to strings
        if 'rate' in validated_data and validated_data['rate'] is not None:
            validated_data['rate'] = json.dumps(validated_data['rate'])

        if 'fmv' in validated_data and validated_data['fmv'] is not None:
            validated_data['fmv'] = json.dumps(validated_data['fmv'])

        if 'heights' in validated_data and validated_data['heights'] is not None:
            validated_data['heights'] = json.dumps(validated_data['heights'])
        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        """Override update to convert data types for storage"""
        # Convert integers to strings for storage
        if 'height' in validated_data and validated_data['height'] is not None:
            validated_data['height'] = str(validated_data['height'])

        if 'fee' in validated_data and validated_data['fee'] is not None:
            validated_data['fee'] = str(validated_data['fee'])

        if 'value' in validated_data and validated_data['value'] is not None:
            validated_data['value'] = str(validated_data['value'])

        # Convert JSON objects to strings
        if 'rate' in validated_data and validated_data['rate'] is not None:
            validated_data['rate'] = json.dumps(validated_data['rate'])

        if 'fmv' in validated_data and validated_data['fmv'] is not None:
            validated_data['fmv'] = json.dumps(validated_data['fmv'])

        if 'heights' in validated_data and validated_data['heights'] is not None:
            validated_data['heights'] = json.dumps(validated_data['heights'])

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Convert stored data back to API format"""
        data = super().to_representation(instance)

        # Convert string integers back to integers
        if data.get('height'):
            try:
                data['height'] = int(data['height'])
            except (ValueError, TypeError):
                data['height'] = None

        if data.get('fee'):
            try:
                data['fee'] = int(data['fee'])
            except (ValueError, TypeError):
                data['fee'] = None

        if data.get('value'):
            try:
                data['value'] = int(data['value'])
            except (ValueError, TypeError):
                data['value'] = None

        # Convert JSON strings back to objects
        if data.get('rate'):
            try:
                data['rate'] = json.loads(data['rate'])
            except (json.JSONDecodeError, TypeError):
                data['rate'] = None

        if data.get('fmv'):
            try:
                data['fmv'] = json.loads(data['fmv'])
            except (json.JSONDecodeError, TypeError):
                data['fmv'] = None

        if data.get('heights'):
            try:
                data['heights'] = json.loads(data['heights'])
            except (json.JSONDecodeError, TypeError):
                data['heights'] = None

        return data


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
