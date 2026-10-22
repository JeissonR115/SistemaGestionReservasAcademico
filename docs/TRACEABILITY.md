# Matriz de trazabilidad

Esta matriz vincula los 39 escenarios de aceptación de OpenSpec con pruebas automatizadas previstas. Las rutas de prueba son objetivos para la implementación; la etapa de cada capacidad y la existencia de la prueba se confirmarán antes de cerrar su tarea.

| Capacidad | Requisito | Escenario | Prueba prevista |
|---|---|---|---|
| `gestion-espacios` | Administrators can maintain academic spaces | Administrator creates a valid space | `spaces/tests.py::test_admin_creates_valid_space` |
| `gestion-espacios` | Administrators can maintain academic spaces | Space has invalid capacity | `spaces/tests.py::test_space_rejects_non_positive_capacity` |
| `gestion-espacios` | Requesters can find active spaces | Catalog lists an active space | `spaces/tests.py::test_requester_sees_active_space_details` |
| `gestion-espacios` | Requesters can find active spaces | Inactive space is excluded from catalog | `spaces/tests.py::test_inactive_space_is_not_available_in_catalog` |
| `usuarios` | Administrators can manage user accounts | Administrator creates an account | `accounts/tests.py::test_admin_creates_user_account` |
| `usuarios` | Administrators can manage user accounts | Administrator deactivates an account | `accounts/tests.py::test_deactivated_user_cannot_sign_in` |
| `usuarios` | Active users can authenticate | Active user signs in with valid credentials | `accounts/tests.py::test_active_user_signs_in` |
| `usuarios` | Active users can authenticate | Inactive user attempts to sign in | `accounts/tests.py::test_inactive_user_sign_in_is_rejected` |
| `usuarios` | Active users can authenticate | Authenticated user signs out | `accounts/tests.py::test_authenticated_user_signs_out` |
| `roles-permisos` | Users have an assigned system role | User account receives a role | `accounts/tests.py::test_admin_assigns_valid_role` |
| `roles-permisos` | Users have an assigned system role | Account has no valid role | `accounts/tests.py::test_account_without_valid_role_is_rejected` |
| `roles-permisos` | Requesters are limited to requester operations | Requester attempts an administrative action | `accounts/tests.py::test_requester_cannot_perform_administrative_actions` |
| `roles-permisos` | Requesters are limited to requester operations | Requester views another user's reservation | `reservations/tests.py::test_requester_cannot_view_another_users_reservation` |
| `roles-permisos` | Administrators can perform administrative operations | Administrator performs a protected operation | `accounts/tests.py::test_admin_can_perform_protected_operations` |
| `roles-permisos` | Administrators can perform administrative operations | Unauthenticated user attempts a protected operation | `accounts/tests.py::test_unauthenticated_user_cannot_perform_protected_operations` |
| `solicitud-reserva` | Requesters can submit reservation requests | Requester submits a valid reservation request | `reservations/tests.py::test_requester_creates_pending_reservation` |
| `solicitud-reserva` | Requesters can submit reservation requests | Request omits required information | `reservations/tests.py::test_request_rejects_missing_required_fields` |
| `solicitud-reserva` | Reservation request periods must be valid | Request has an empty or reversed period | `reservations/tests.py::test_request_rejects_empty_or_reversed_period` |
| `solicitud-reserva` | Reservation request periods must be valid | Request targets an inactive space | `reservations/tests.py::test_request_rejects_inactive_or_missing_space` |
| `solicitud-reserva` | Requesters can review their own requests | Requester reviews a submitted request | `reservations/tests.py::test_requester_sees_own_request_details` |
| `validacion-disponibilidad` | Availability reflects blocking reservations | Pending request blocks availability | `reservations/tests.py::test_pending_request_blocks_overlapping_period` |
| `validacion-disponibilidad` | Availability reflects blocking reservations | Rejected or cancelled request does not block availability | `reservations/tests.py::test_rejected_and_cancelled_requests_do_not_block_period` |
| `validacion-disponibilidad` | Reservation intervals use half-open boundaries | Adjacent reservations do not overlap | `reservations/tests.py::test_adjacent_periods_do_not_overlap` |
| `validacion-disponibilidad` | Reservation intervals use half-open boundaries | Intersecting reservations overlap | `reservations/tests.py::test_intersecting_periods_overlap` |
| `validacion-disponibilidad` | Inactive spaces are unavailable | Availability checked for an inactive space | `reservations/tests.py::test_inactive_space_is_unavailable` |
| `prevencion-simultaneas` | Conflicting reservation requests are resolved atomically | Two simultaneous requests compete for an available period | `reservations/tests.py::test_concurrent_overlapping_requests_accept_at_most_one` |
| `prevencion-simultaneas` | Conflicting reservation requests are resolved atomically | A competing request arrives after a pending request is recorded | `reservations/tests.py::test_new_overlapping_request_is_rejected_when_pending_exists` |
| `prevencion-simultaneas` | Conflict rejection does not create a reservation | Request loses a conflict check | `reservations/tests.py::test_conflict_does_not_persist_second_request` |
| `aprobacion-rechazo` | Administrators can review pending requests | Administrator lists pending requests | `reservations/tests.py::test_admin_lists_pending_requests_with_review_details` |
| `aprobacion-rechazo` | Administrators can approve valid pending requests | Administrator approves a valid request | `reservations/tests.py::test_admin_approves_valid_request_excluding_itself_from_conflicts` |
| `aprobacion-rechazo` | Administrators can approve valid pending requests | Administrator attempts to approve a request for an inactive space | `reservations/tests.py::test_admin_cannot_approve_request_for_inactive_space` |
| `aprobacion-rechazo` | Administrators can reject pending requests | Administrator rejects a pending request | `reservations/tests.py::test_admin_rejects_pending_request` |
| `aprobacion-rechazo` | Review decisions apply only to pending requests | Administrator attempts a duplicate decision | `reservations/tests.py::test_admin_cannot_decide_non_pending_request` |
| `cancelacion-historial` | Requesters can cancel their own active requests | Requester cancels a pending request | `reservations/tests.py::test_requester_cancels_pending_request_and_releases_period` |
| `cancelacion-historial` | Requesters can cancel their own active requests | Requester cancels an approved reservation | `reservations/tests.py::test_requester_cancels_approved_reservation_and_releases_period` |
| `cancelacion-historial` | Requesters can cancel their own active requests | Requester attempts to cancel another user's reservation | `reservations/tests.py::test_requester_cannot_cancel_another_users_reservation` |
| `cancelacion-historial` | Requesters can cancel their own active requests | Requester attempts to cancel a terminal reservation | `reservations/tests.py::test_requester_cannot_cancel_terminal_reservation` |
| `cancelacion-historial` | Reservation state changes are traceable | Reservation status changes | `reservations/tests.py::test_status_changes_record_actor_and_timestamp` |
| `cancelacion-historial` | Reservation state changes are traceable | Authorized viewer reviews reservation history | `reservations/tests.py::test_authorized_viewer_sees_chronological_history` |

## Convenciones de verificación

- Las pruebas de cuentas y roles comprueban autenticación por sesión y autorización en los puntos de entrada protegidos.
- Las pruebas de reservas verifican tanto las respuestas observables de API como los cambios persistidos de estado e historial.
- La prueba de concurrencia se ejecuta con conexiones independientes contra SQLite y comprueba que exactamente una solicitud solapada queda pendiente; errores de base de datos no cuentan como una respuesta de conflicto válida.
- Cada referencia se confirmará contra una prueba ejecutable al completar la implementación de su capacidad.
