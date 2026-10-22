from rest_framework import serializers

from spaces.models import Space

from .models import Reservation


class ReservationCreateSerializer(serializers.Serializer):
    space = serializers.PrimaryKeyRelatedField(queryset=Space.objects.all())
    purpose = serializers.CharField(max_length=500)
    start_at = serializers.DateTimeField()
    end_at = serializers.DateTimeField()

    def validate_purpose(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('El motivo es obligatorio.')
        return value

    def validate(self, attrs):
        if attrs['start_at'] >= attrs['end_at']:
            raise serializers.ValidationError({
                'end_at': 'La hora de fin debe ser posterior al inicio.'
            })
        return attrs


class ReservationSerializer(serializers.ModelSerializer):
    space_name = serializers.CharField(source='space.name', read_only=True)
    requester_username = serializers.CharField(
        source='requester.username',
        read_only=True,
    )

    class Meta:
        model = Reservation
        fields = (
            'id',
            'space',
            'space_name',
            'requester',
            'requester_username',
            'purpose',
            'start_at',
            'end_at',
            'status',
            'created_at',
        )
        read_only_fields = fields


class ReservationLogSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(
        source='actor.username',
        read_only=True,
    )

    class Meta:
        from .models import ReservationLog

        model = ReservationLog
        fields = ('id', 'status', 'actor', 'actor_username', 'changed_at')
        read_only_fields = fields
