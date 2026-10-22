from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsAdministrator
from reservations.services import is_space_available
from .models import Space
from .permissions import AdministratorOrAuthenticatedReadOnly
from .serializers import SpaceSerializer


class AvailabilityQuerySerializer(serializers.Serializer):
    start_at = serializers.DateTimeField()
    end_at = serializers.DateTimeField()

    def validate(self, attrs):
        if attrs['start_at'] >= attrs['end_at']:
            raise serializers.ValidationError(
                'La hora de inicio debe ser anterior a la hora de fin.'
            )
        return attrs


class SpaceViewSet(viewsets.ModelViewSet):
    serializer_class = SpaceSerializer
    permission_classes = (AdministratorOrAuthenticatedReadOnly,)
    queryset = Space.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        if IsAdministrator().has_permission(self.request, self):
            return queryset
        return queryset.filter(is_active=True)

    def destroy(self, request, *args, **kwargs):
        space = self.get_object()
        space.is_active = False
        space.save(update_fields=('is_active',))
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('get',), url_path='availability')
    def availability(self, request, pk=None):
        space = Space.objects.filter(pk=pk).first()
        if space is None:
            return Response(
                {'detail': 'El espacio no existe.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = AvailabilityQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        available = is_space_available(
            space,
            serializer.validated_data['start_at'],
            serializer.validated_data['end_at'],
        )
        return Response({'space': space.pk, 'available': available})
