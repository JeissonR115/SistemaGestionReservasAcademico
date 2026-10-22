from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from django.contrib.auth import get_user_model
from django.db import close_old_connections
from django.test import TransactionTestCase
from django.utils import timezone
from rest_framework.test import APITestCase

from spaces.models import Space

from .models import Reservation
from .services import (
    ReservationConflict,
    ReservationDurationExceeded,
    create_reservation,
    is_space_available,
)

User = get_user_model()


class ReservationRequestTests(APITestCase):
    def setUp(self):
        self.requester = User.objects.create_user(
            username='reservation-requester',
            password='RequesterPass123!',
        )
        self.other_requester = User.objects.create_user(
            username='other-requester',
            password='OtherPass123!',
        )
        self.admin = User.objects.create_user(
            username='reservation-admin',
            password='AdminPass123!',
            role=User.Role.ADMINISTRATOR,
        )
        self.space = Space.objects.create(
            name='Reserva Lab',
            space_type='Laboratorio',
            capacity=20,
        )
        self.start_at = timezone.make_aware(datetime(2030, 1, 2, 9, 0))
        self.end_at = self.start_at + timedelta(hours=1)
        self.client.force_authenticate(user=self.requester)

    def request_data(self, **overrides):
        data = {
            'space': self.space.pk,
            'purpose': 'Clase de programación',
            'start_at': self.start_at.isoformat(),
            'end_at': self.end_at.isoformat(),
        }
        return {**data, **overrides}

    def create_reservation(self, **overrides):
        reservation_data = {
            'requester': self.requester,
            'space_id': self.space.pk,
            'purpose': 'Actividad académica',
            'start_at': self.start_at,
            'end_at': self.end_at,
        }
        reservation_data.update(overrides)
        return create_reservation(**reservation_data)

    def test_requester_creates_pending_reservation(self):
        response = self.client.post(
            '/api/reservations/',
            self.request_data(),
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], Reservation.Status.PENDING)
        self.assertEqual(response.data['requester'], self.requester.pk)
        self.assertEqual(response.data['space_name'], self.space.name)
        reservation = Reservation.objects.get(pk=response.data['id'])
        self.assertEqual(reservation.requester, self.requester)
        self.assertEqual(reservation.history.count(), 1)
        self.assertEqual(reservation.history.first().actor, self.requester)

    def test_duration_limit_accepts_three_hours_fifty_nine_minutes_and_four_hours(self):
        for offset, duration in enumerate(
            (timedelta(hours=3, minutes=59), timedelta(hours=4)),
        ):
            with self.subTest(duration=duration):
                start_at = self.start_at + timedelta(days=offset)
                reservation = self.create_reservation(
                    start_at=start_at,
                    end_at=start_at + duration,
                )
                self.assertEqual(reservation.status, Reservation.Status.PENDING)

    def test_duration_limit_rejects_more_than_four_hours(self):
        with self.assertRaises(ReservationDurationExceeded):
            self.create_reservation(
                start_at=self.start_at,
                end_at=self.start_at + timedelta(hours=4, minutes=1),
            )

        self.assertEqual(Reservation.objects.count(), 0)

    def test_api_returns_bad_request_for_over_four_hours_for_every_role(self):
        for user in (self.requester, self.admin):
            with self.subTest(role=user.role):
                self.client.force_authenticate(user=user)
                response = self.client.post(
                    '/api/reservations/',
                    self.request_data(
                        end_at=(
                            self.start_at + timedelta(hours=4, minutes=1)
                        ).isoformat(),
                    ),
                    format='json',
                )

                self.assertEqual(response.status_code, 400)
                self.assertIn('4 horas', response.data['detail'])
                self.assertEqual(Reservation.objects.count(), 0)

    def test_contiguous_same_requester_pending_reservation_counts_toward_limit(self):
        first_end = self.start_at + timedelta(hours=2)
        self.create_reservation(
            start_at=self.start_at,
            end_at=first_end,
        )

        with self.assertRaises(ReservationDurationExceeded):
            self.create_reservation(
                start_at=first_end,
                end_at=first_end + timedelta(hours=2, minutes=1),
            )

    def test_contiguous_same_requester_approved_reservation_counts_toward_limit(self):
        first_end = self.start_at + timedelta(hours=2)
        reservation = self.create_reservation(
            start_at=self.start_at,
            end_at=first_end,
        )
        Reservation.objects.filter(pk=reservation.pk).update(
            status=Reservation.Status.APPROVED,
        )

        with self.assertRaises(ReservationDurationExceeded):
            self.create_reservation(
                start_at=first_end,
                end_at=first_end + timedelta(hours=2, minutes=1),
            )

    def test_contiguous_same_requester_reservations_allow_exactly_four_hours(self):
        first_end = self.start_at + timedelta(hours=2)
        self.create_reservation(
            start_at=self.start_at,
            end_at=first_end,
        )

        reservation = self.create_reservation(
            start_at=first_end,
            end_at=first_end + timedelta(hours=2),
        )

        self.assertEqual(reservation.status, Reservation.Status.PENDING)

    def test_contiguous_reservation_for_another_requester_does_not_count(self):
        first_end = self.start_at + timedelta(hours=2)
        self.create_reservation(
            requester=self.other_requester,
            start_at=self.start_at,
            end_at=first_end,
        )

        reservation = self.create_reservation(
            start_at=first_end,
            end_at=first_end + timedelta(hours=4),
        )

        self.assertEqual(reservation.requester, self.requester)

    def test_contiguous_rejected_or_cancelled_reservations_do_not_count(self):
        for offset, state in enumerate(
            (Reservation.Status.REJECTED, Reservation.Status.CANCELLED),
        ):
            with self.subTest(state=state):
                start_at = self.start_at + timedelta(days=offset)
                first_end = start_at + timedelta(hours=2)
                existing = self.create_reservation(
                    start_at=start_at,
                    end_at=first_end,
                )
                Reservation.objects.filter(pk=existing.pk).update(status=state)

                reservation = self.create_reservation(
                    start_at=first_end,
                    end_at=first_end + timedelta(hours=4),
                )

                self.assertEqual(reservation.status, Reservation.Status.PENDING)

    def test_contiguous_multi_reservation_chain_counts_toward_limit(self):
        first_end = self.start_at + timedelta(hours=1)
        second_end = first_end + timedelta(hours=1)
        self.create_reservation(start_at=self.start_at, end_at=first_end)
        self.create_reservation(start_at=first_end, end_at=second_end)

        with self.assertRaises(ReservationDurationExceeded):
            self.create_reservation(
                start_at=second_end,
                end_at=second_end + timedelta(hours=2, minutes=1),
            )

    def test_contiguous_reservation_after_request_counts_toward_limit(self):
        candidate_end = self.start_at + timedelta(hours=2, minutes=1)
        self.create_reservation(
            start_at=candidate_end,
            end_at=candidate_end + timedelta(hours=2),
        )

        with self.assertRaises(ReservationDurationExceeded):
            self.create_reservation(
                start_at=self.start_at,
                end_at=candidate_end,
            )

    def test_new_overlapping_request_is_rejected_when_pending_exists(self):
        first_response = self.client.post(
            '/api/reservations/',
            self.request_data(),
            format='json',
        )
        second_response = self.client.post(
            '/api/reservations/',
            self.request_data(
                start_at=(self.start_at + timedelta(minutes=15)).isoformat(),
                end_at=(self.end_at + timedelta(minutes=15)).isoformat(),
            ),
            format='json',
        )

        self.assertEqual(first_response.status_code, 201)
        self.assertEqual(second_response.status_code, 409)
        self.assertIn('detail', second_response.data)
        self.assertEqual(Reservation.objects.count(), 1)

    def test_request_rejects_missing_required_fields(self):
        response = self.client.post(
            '/api/reservations/',
            {'space': self.space.pk},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('purpose', response.data)
        self.assertIn('start_at', response.data)
        self.assertIn('end_at', response.data)
        self.assertEqual(Reservation.objects.count(), 0)

    def test_request_rejects_empty_or_reversed_period(self):
        response = self.client.post(
            '/api/reservations/',
            self.request_data(end_at=self.start_at.isoformat()),
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('end_at', response.data)
        self.assertEqual(Reservation.objects.count(), 0)

    def test_request_rejects_inactive_or_missing_space(self):
        self.space.is_active = False
        self.space.save(update_fields=('is_active',))
        inactive_response = self.client.post(
            '/api/reservations/',
            self.request_data(),
            format='json',
        )
        missing_response = self.client.post(
            '/api/reservations/',
            self.request_data(space=9999),
            format='json',
        )

        self.assertEqual(inactive_response.status_code, 400)
        self.assertEqual(missing_response.status_code, 400)
        self.assertEqual(Reservation.objects.count(), 0)

    def test_requester_sees_own_request_details(self):
        reservation = self.create_reservation()

        response = self.client.get(f'/api/reservations/{reservation.pk}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['space_name'], self.space.name)
        self.assertEqual(response.data['purpose'], reservation.purpose)
        self.assertEqual(response.data['status'], Reservation.Status.PENDING)

    def test_admin_lists_pending_requests_with_review_details(self):
        reservation = self.create_reservation()
        self.client.force_authenticate(user=self.admin)

        response = self.client.get('/api/reservations/pending/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], reservation.pk)
        self.assertEqual(
            response.data[0]['requester_username'],
            self.requester.username,
        )
        self.assertEqual(response.data[0]['space_name'], self.space.name)

    def test_admin_approves_valid_request_excluding_itself_from_conflicts(self):
        reservation = self.create_reservation()
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            f'/api/reservations/{reservation.pk}/approve/',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], Reservation.Status.APPROVED)
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, Reservation.Status.APPROVED)
        self.assertEqual(reservation.history.count(), 2)
        self.assertEqual(reservation.history.last().actor, self.admin)

    def test_approval_revalidates_duration_and_preserves_violating_request(self):
        neighbor_end = self.start_at + timedelta(hours=2)
        self.create_reservation(
            start_at=self.start_at,
            end_at=neighbor_end,
        )
        neighbor = Reservation.objects.get(
            requester=self.requester,
            start_at=self.start_at,
        )
        neighbor.status = Reservation.Status.APPROVED
        neighbor.save(update_fields=('status',))
        candidate = Reservation.objects.create(
            requester=self.requester,
            space=self.space,
            purpose='Solicitud preexistente',
            start_at=neighbor_end,
            end_at=neighbor_end + timedelta(hours=2, minutes=1),
            status=Reservation.Status.PENDING,
        )
        candidate.history.create(
            status=Reservation.Status.PENDING,
            actor=self.requester,
        )

        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            f'/api/reservations/{candidate.pk}/approve/',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('4 horas', response.data['detail'])
        candidate.refresh_from_db()
        self.assertEqual(candidate.status, Reservation.Status.PENDING)
        self.assertEqual(candidate.history.count(), 1)

    def test_admin_cannot_approve_request_for_inactive_space(self):
        reservation = self.create_reservation()
        self.space.is_active = False
        self.space.save(update_fields=('is_active',))
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            f'/api/reservations/{reservation.pk}/approve/',
        )

        self.assertEqual(response.status_code, 409)
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, Reservation.Status.PENDING)
        self.assertEqual(reservation.history.count(), 1)

    def test_admin_cannot_approve_request_if_another_blocker_exists(self):
        reservation = self.create_reservation()
        Reservation.objects.create(
            space=self.space,
            requester=self.other_requester,
            purpose='Conflicto legado',
            start_at=self.start_at,
            end_at=self.end_at,
            status=Reservation.Status.APPROVED,
        )
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            f'/api/reservations/{reservation.pk}/approve/',
        )

        self.assertEqual(response.status_code, 409)
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, Reservation.Status.PENDING)

    def test_admin_rejects_pending_request(self):
        reservation = self.create_reservation()
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            f'/api/reservations/{reservation.pk}/reject/',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], Reservation.Status.REJECTED)
        reservation.refresh_from_db()
        self.assertEqual(reservation.history.last().actor, self.admin)

    def test_admin_cannot_decide_non_pending_request(self):
        reservation = self.create_reservation()
        self.client.force_authenticate(user=self.admin)
        rejected = self.client.post(
            f'/api/reservations/{reservation.pk}/reject/',
        )
        duplicate = self.client.post(
            f'/api/reservations/{reservation.pk}/approve/',
        )

        self.assertEqual(rejected.status_code, 200)
        self.assertEqual(duplicate.status_code, 409)
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, Reservation.Status.REJECTED)
        self.assertEqual(reservation.history.count(), 2)

    def test_requester_cannot_review_or_decide_pending_requests(self):
        reservation = self.create_reservation()

        pending_response = self.client.get('/api/reservations/pending/')
        approve_response = self.client.post(
            f'/api/reservations/{reservation.pk}/approve/',
        )

        self.assertEqual(pending_response.status_code, 403)
        self.assertEqual(approve_response.status_code, 403)

    def test_requester_cancels_pending_request_and_releases_period(self):
        reservation = self.create_reservation()

        response = self.client.post(
            f'/api/reservations/{reservation.pk}/cancel/',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], Reservation.Status.CANCELLED)
        reservation.refresh_from_db()
        self.assertEqual(reservation.history.count(), 2)
        self.assertTrue(
            is_space_available(self.space, self.start_at, self.end_at)
        )

    def test_requester_cancels_approved_reservation_and_releases_period(self):
        reservation = self.create_reservation()
        self.client.force_authenticate(user=self.admin)
        approved = self.client.post(
            f'/api/reservations/{reservation.pk}/approve/',
        )
        self.assertEqual(approved.status_code, 200)

        self.client.force_authenticate(user=self.requester)
        cancelled = self.client.post(
            f'/api/reservations/{reservation.pk}/cancel/',
        )

        self.assertEqual(cancelled.status_code, 200)
        self.assertEqual(cancelled.data['status'], Reservation.Status.CANCELLED)
        self.assertTrue(
            is_space_available(self.space, self.start_at, self.end_at)
        )

    def test_requester_cannot_cancel_another_users_reservation(self):
        reservation = self.create_reservation()
        self.client.force_authenticate(user=self.other_requester)

        response = self.client.post(
            f'/api/reservations/{reservation.pk}/cancel/',
        )

        self.assertEqual(response.status_code, 404)
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, Reservation.Status.PENDING)

    def test_requester_cannot_cancel_terminal_reservation(self):
        reservation = self.create_reservation()
        self.client.force_authenticate(user=self.admin)
        rejected = self.client.post(
            f'/api/reservations/{reservation.pk}/reject/',
        )
        self.assertEqual(rejected.status_code, 200)
        self.client.force_authenticate(user=self.requester)

        rejected_cancel = self.client.post(
            f'/api/reservations/{reservation.pk}/cancel/',
        )
        self.assertEqual(rejected_cancel.status_code, 409)

        reservation.status = Reservation.Status.CANCELLED
        reservation.save(update_fields=('status',))
        cancelled_cancel = self.client.post(
            f'/api/reservations/{reservation.pk}/cancel/',
        )
        self.assertEqual(cancelled_cancel.status_code, 409)

    def test_status_changes_record_actor_and_timestamp(self):
        reservation = self.create_reservation()
        self.client.force_authenticate(user=self.admin)
        approved = self.client.post(
            f'/api/reservations/{reservation.pk}/approve/',
        )
        self.assertEqual(approved.status_code, 200)
        self.client.force_authenticate(user=self.requester)
        cancelled = self.client.post(
            f'/api/reservations/{reservation.pk}/cancel/',
        )
        self.assertEqual(cancelled.status_code, 200)

        history = list(reservation.history.all())
        self.assertEqual(
            [entry.status for entry in history],
            [
                Reservation.Status.PENDING,
                Reservation.Status.APPROVED,
                Reservation.Status.CANCELLED,
            ],
        )
        self.assertEqual(
            [entry.actor for entry in history],
            [self.requester, self.admin, self.requester],
        )
        self.assertEqual(
            [entry.changed_at for entry in history],
            sorted(entry.changed_at for entry in history),
        )

    def test_authorized_viewer_sees_chronological_history(self):
        reservation = self.create_reservation()
        self.client.force_authenticate(user=self.admin)
        self.client.post(f'/api/reservations/{reservation.pk}/approve/')

        response = self.client.get(
            f'/api/reservations/{reservation.pk}/history/',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [entry['status'] for entry in response.data],
            [Reservation.Status.PENDING, Reservation.Status.APPROVED],
        )
        self.assertEqual(
            response.data[0]['actor_username'],
            self.requester.username,
        )

    def test_pending_request_blocks_overlapping_period(self):
        self.create_reservation()

        self.assertFalse(
            is_space_available(
                self.space,
                self.start_at + timedelta(minutes=30),
                self.end_at + timedelta(minutes=30),
            )
        )

    def test_rejected_and_cancelled_requests_do_not_block_period(self):
        reservation = self.create_reservation()
        Reservation.objects.filter(pk=reservation.pk).update(
            status=Reservation.Status.REJECTED,
        )
        self.assertTrue(
            is_space_available(self.space, self.start_at, self.end_at)
        )

        Reservation.objects.filter(pk=reservation.pk).update(
            status=Reservation.Status.CANCELLED,
        )
        self.assertTrue(
            is_space_available(self.space, self.start_at, self.end_at)
        )

    def test_adjacent_periods_do_not_overlap(self):
        self.create_reservation()

        self.assertTrue(
            is_space_available(
                self.space,
                self.end_at,
                self.end_at + timedelta(hours=1),
            )
        )

    def test_intersecting_periods_overlap(self):
        self.create_reservation()

        self.assertFalse(
            is_space_available(
                self.space,
                self.start_at - timedelta(minutes=1),
                self.start_at + timedelta(minutes=1),
            )
        )

    def test_inactive_space_is_unavailable(self):
        self.space.is_active = False
        self.space.save(update_fields=('is_active',))

        self.assertFalse(
            is_space_available(self.space, self.start_at, self.end_at)
        )

    def test_availability_endpoint_reports_space_status(self):
        response = self.client.get(
            f'/api/spaces/{self.space.pk}/availability/',
            {
                'start_at': self.start_at.isoformat(),
                'end_at': self.end_at.isoformat(),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['available'])

        self.create_reservation()
        response = self.client.get(
            f'/api/spaces/{self.space.pk}/availability/',
            {
                'start_at': self.start_at.isoformat(),
                'end_at': self.end_at.isoformat(),
            },
        )
        self.assertFalse(response.data['available'])

        self.space.is_active = False
        self.space.save(update_fields=('is_active',))
        response = self.client.get(
            f'/api/spaces/{self.space.pk}/availability/',
            {
                'start_at': self.start_at.isoformat(),
                'end_at': self.end_at.isoformat(),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['available'])


class ConcurrentReservationTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.requesters = [
            User.objects.create_user(username=f'concurrent-{index}')
            for index in range(2)
        ]
        self.space = Space.objects.create(
            name='Concurrent Lab',
            space_type='Laboratorio',
            capacity=20,
        )
        self.start_at = timezone.make_aware(datetime(2030, 2, 1, 9, 0))
        self.end_at = self.start_at + timedelta(hours=1)
        self.barrier = Barrier(2)

    def submit_request(self, requester_id):
        close_old_connections()
        try:
            requester = User.objects.get(pk=requester_id)
            self.barrier.wait(timeout=10)
            try:
                create_reservation(
                    requester=requester,
                    space_id=self.space.pk,
                    purpose='Solicitud concurrente',
                    start_at=self.start_at,
                    end_at=self.end_at,
                )
                return 'accepted'
            except ReservationConflict:
                return 'conflict'
        finally:
            close_old_connections()

    def test_concurrent_overlapping_requests_accept_at_most_one(self):
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(
                self.submit_request,
                [user.pk for user in self.requesters],
            ))

        self.assertCountEqual(results, ('accepted', 'conflict'))
        self.assertEqual(
            Reservation.objects.filter(
                status=Reservation.Status.PENDING,
            ).count(),
            1,
        )

# Create your tests here.
