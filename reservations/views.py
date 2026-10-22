from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsAdministrator
from .models import Reservation
from .permissions import ReservationAccessPermission
from .serializers import (
    ReservationCreateSerializer,
    ReservationLogSerializer,
    ReservationSerializer,
)
from .services import (
    InvalidTransition,
    ReservationConflict,
    ReservationOwnershipError,
    SpaceUnavailable,
    approve_reservation,
    cancel_reservation,
    create_reservation,
    reject_reservation,
)


class ReservationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (ReservationAccessPermission,)
    queryset = Reservation.objects.select_related('space', 'requester')

    def get_queryset(self):
        queryset = super().get_queryset()
        if IsAdministrator().has_permission(self.request, self):
            return queryset
        return queryset.filter(requester=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return ReservationCreateSerializer
        return ReservationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            reservation = create_reservation(
                requester=request.user,
                space_id=serializer.validated_data['space'].pk,
                purpose=serializer.validated_data['purpose'],
                start_at=serializer.validated_data['start_at'],
                end_at=serializer.validated_data['end_at'],
            )
        except ReservationConflict as error:
            return Response(
                {'detail': str(error)},
                status=status.HTTP_409_CONFLICT,
            )
        except SpaceUnavailable as error:
            return Response(
                {'detail': str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            ReservationSerializer(reservation).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAdministrator,),
    )
    def pending(self, request):
        reservations = self.get_queryset().filter(
            status=Reservation.Status.PENDING,
        )
        return Response(
            ReservationSerializer(reservations, many=True).data,
        )

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(IsAdministrator,),
    )
    def approve(self, request, pk=None):
        reservation = self.get_object()
        try:
            reservation = approve_reservation(
                reservation_id=reservation.pk,
                actor=request.user,
            )
        except (InvalidTransition, ReservationConflict, SpaceUnavailable) as error:
            return Response(
                {'detail': str(error)},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(ReservationSerializer(reservation).data)

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(IsAdministrator,),
    )
    def reject(self, request, pk=None):
        reservation = self.get_object()
        try:
            reservation = reject_reservation(
                reservation_id=reservation.pk,
                actor=request.user,
            )
        except InvalidTransition as error:
            return Response(
                {'detail': str(error)},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(ReservationSerializer(reservation).data)

    @action(detail=True, methods=('get',))
    def history(self, request, pk=None):
        reservation = self.get_object()
        entries = reservation.history.select_related('actor').all()
        return Response(ReservationLogSerializer(entries, many=True).data)

    @action(detail=True, methods=('post',))
    def cancel(self, request, pk=None):
        reservation = self.get_object()
        if reservation.requester_id != request.user.pk:
            return Response(
                {'detail': 'Solo quien solicitó la reserva puede cancelarla.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            reservation = cancel_reservation(
                reservation_id=reservation.pk,
                requester=request.user,
            )
        except ReservationOwnershipError as error:
            return Response(
                {'detail': str(error)},
                status=status.HTTP_403_FORBIDDEN,
            )
        except (InvalidTransition, ReservationConflict) as error:
            return Response(
                {'detail': str(error)},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(ReservationSerializer(reservation).data)
