from datetime import timedelta

from django.db import OperationalError, transaction
from django.db.models import F

from spaces.models import Space

from .models import Reservation, ReservationLog


class ReservationConflict(Exception):
    pass


class SpaceUnavailable(Exception):
    pass


class InvalidTransition(Exception):
    pass


class ReservationOwnershipError(Exception):
    pass


class ReservationDurationExceeded(Exception):
    pass


MAX_CONTIGUOUS_RESERVATION_DURATION = timedelta(hours=4)


def overlapping_reservations(space, start_at, end_at, exclude_id=None):
    reservations = Reservation.objects.filter(
        space=space,
        status__in=(Reservation.Status.PENDING, Reservation.Status.APPROVED),
        start_at__lt=end_at,
        end_at__gt=start_at,
    )
    if exclude_id is not None:
        reservations = reservations.exclude(pk=exclude_id)
    return reservations


def validate_reservation_duration(
    *,
    requester_id,
    space_id,
    start_at,
    end_at,
    exclude_id=None,
):
    if end_at - start_at > MAX_CONTIGUOUS_RESERVATION_DURATION:
        raise ReservationDurationExceeded(
            'La duración continua reservada por una misma persona para este '
            'espacio no puede superar 4 horas.'
        )

    reservations = Reservation.objects.filter(
        requester_id=requester_id,
        space_id=space_id,
        status__in=(Reservation.Status.PENDING, Reservation.Status.APPROVED),
    )
    if exclude_id is not None:
        reservations = reservations.exclude(pk=exclude_id)

    block_start = start_at
    block_end = end_at
    neighbors = list(reservations.values_list('start_at', 'end_at'))
    extended = True
    while extended:
        extended = False
        for neighbor_start, neighbor_end in neighbors:
            if neighbor_end == block_start:
                block_start = neighbor_start
                extended = True
            elif neighbor_start == block_end:
                block_end = neighbor_end
                extended = True

    if block_end - block_start > MAX_CONTIGUOUS_RESERVATION_DURATION:
        raise ReservationDurationExceeded(
            'La duración continua reservada por una misma persona para este '
            'espacio no puede superar 4 horas.'
        )


def is_space_available(space, start_at, end_at, exclude_id=None):
    return bool(
        space.is_active
        and start_at < end_at
        and not overlapping_reservations(
            space,
            start_at,
            end_at,
            exclude_id=exclude_id,
        ).exists()
    )


def create_reservation(*, requester, space_id, purpose, start_at, end_at):
    if start_at >= end_at:
        raise ValueError('La hora de inicio debe ser anterior a la hora de fin.')

    try:
        with transaction.atomic():
            locked_space = Space.objects.filter(pk=space_id).update(
                reservation_version=F('reservation_version') + 1,
            )
            if not locked_space:
                raise SpaceUnavailable('El espacio no existe.')

            space = Space.objects.get(pk=space_id)
            if not space.is_active:
                raise SpaceUnavailable('El espacio está inactivo.')
            if overlapping_reservations(space, start_at, end_at).exists():
                raise ReservationConflict(
                    'El espacio ya tiene una solicitud o reserva en ese horario.'
                )
            validate_reservation_duration(
                requester_id=requester.pk,
                space_id=space.pk,
                start_at=start_at,
                end_at=end_at,
            )

            reservation = Reservation.objects.create(
                requester=requester,
                space=space,
                purpose=purpose,
                start_at=start_at,
                end_at=end_at,
                status=Reservation.Status.PENDING,
            )
            ReservationLog.objects.create(
                reservation=reservation,
                status=Reservation.Status.PENDING,
                actor=requester,
            )
            return reservation
    except OperationalError as error:
        if 'locked' not in str(error).lower():
            raise
        raise ReservationConflict(
            'No se pudo reservar el horario mientras otra solicitud lo procesaba.'
        ) from error


def _lock_space(space_id):
    updated = Space.objects.filter(pk=space_id).update(
        reservation_version=F('reservation_version') + 1,
    )
    if not updated:
        raise SpaceUnavailable('El espacio no existe.')
    return Space.objects.get(pk=space_id)


def _transition_reservation(
    *,
    reservation_id,
    actor,
    new_status,
    check_availability=False,
):
    try:
        with transaction.atomic():
            reservation = Reservation.objects.get(pk=reservation_id)
            space = _lock_space(reservation.space_id)
            reservation = Reservation.objects.select_related('space').get(
                pk=reservation_id,
            )
            if reservation.status != Reservation.Status.PENDING:
                raise InvalidTransition(
                    'Solo se pueden modificar solicitudes pendientes.'
                )
            if check_availability:
                if not space.is_active:
                    raise SpaceUnavailable('El espacio está inactivo.')
                if overlapping_reservations(
                    space,
                    reservation.start_at,
                    reservation.end_at,
                    exclude_id=reservation.pk,
                ).exists():
                    raise ReservationConflict(
                        'El horario dejó de estar disponible.'
                    )
                validate_reservation_duration(
                    requester_id=reservation.requester_id,
                    space_id=space.pk,
                    start_at=reservation.start_at,
                    end_at=reservation.end_at,
                    exclude_id=reservation.pk,
                )

            reservation.status = new_status
            reservation.save(update_fields=('status',))
            ReservationLog.objects.create(
                reservation=reservation,
                status=new_status,
                actor=actor,
            )
            return reservation
    except OperationalError as error:
        if 'locked' not in str(error).lower():
            raise
        raise ReservationConflict(
            'No se pudo actualizar la solicitud mientras otra operación '
            'la procesaba.'
        ) from error


def approve_reservation(*, reservation_id, actor):
    return _transition_reservation(
        reservation_id=reservation_id,
        actor=actor,
        new_status=Reservation.Status.APPROVED,
        check_availability=True,
    )


def reject_reservation(*, reservation_id, actor):
    return _transition_reservation(
        reservation_id=reservation_id,
        actor=actor,
        new_status=Reservation.Status.REJECTED,
    )


def cancel_reservation(*, reservation_id, requester):
    try:
        with transaction.atomic():
            reservation = Reservation.objects.get(pk=reservation_id)
            _lock_space(reservation.space_id)
            reservation = Reservation.objects.get(pk=reservation_id)
            if reservation.requester_id != requester.pk:
                raise ReservationOwnershipError(
                    'Solo quien solicitó la reserva puede cancelarla.'
                )
            if reservation.status not in (
                Reservation.Status.PENDING,
                Reservation.Status.APPROVED,
            ):
                raise InvalidTransition(
                    'Solo se pueden cancelar solicitudes pendientes o aprobadas.'
                )

            reservation.status = Reservation.Status.CANCELLED
            reservation.save(update_fields=('status',))
            ReservationLog.objects.create(
                reservation=reservation,
                status=Reservation.Status.CANCELLED,
                actor=requester,
            )
            return reservation
    except OperationalError as error:
        if 'locked' not in str(error).lower():
            raise
        raise ReservationConflict(
            'No se pudo cancelar la solicitud mientras otra operación '
            'la procesaba.'
        ) from error
