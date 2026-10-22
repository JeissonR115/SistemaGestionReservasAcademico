from rest_framework import serializers

from .models import Space


class SpaceSerializer(serializers.ModelSerializer):
    capacity = serializers.IntegerField(min_value=1)

    class Meta:
        model = Space
        fields = ('id', 'name', 'space_type', 'capacity', 'is_active')
        read_only_fields = ('id',)

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('El nombre es obligatorio.')
        return value

    def validate_space_type(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('El tipo es obligatorio.')
        return value
