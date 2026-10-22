# Proposal

## Why

Academic-space reservations are currently handled through email and spreadsheets, leading to duplicate requests, scheduling conflicts, and poor traceability. This change establishes a verifiable behavioral contract for a centralized reservation system before implementation begins.

## What Changes

- Define requirements and testable Given/When/Then scenarios for spaces, users, roles and permissions, reservation requests, availability validation, concurrent booking prevention, approval and rejection, and cancellation and history.
- Capture the approved architectural and domain constraints: Django, Django REST Framework, SQLite, business rules in a service layer, and half-open reservation intervals `[start, end)`.
- Order implementation tasks according to the progressive development stages in `PLAN_INGENIERIA.md`.
- Create planning artifacts only; no application code or runtime behavior changes in this change.

## Capabilities

### New Capabilities
- `gestion-espacios`: Manage academic spaces, including their type, capacity, and availability status.
- `usuarios`: Identify users and support their account lifecycle for reservation workflows.
- `roles-permisos`: Define requester and administrator roles and their access rights.
- `solicitud-reserva`: Create reservation requests for a space and time range.
- `validacion-disponibilidad`: Validate requested time ranges against space availability and existing reservations.
- `prevencion-simultaneas`: Prevent conflicting reservations from being accepted when requests are processed concurrently.
- `aprobacion-rechazo`: Allow administrators to approve or reject reservation requests.
- `cancelacion-historial`: Allow appropriate cancellation and preserve the history of reservation state changes.

### Modified Capabilities

None. No existing capability specifications are present.

## Impact

This change adds OpenSpec planning artifacts only. It defines the contract for a future Django 5 and Django REST Framework monolith using SQLite, session authentication, and a lightweight Django-template interface; it does not add code, endpoints, dependencies, or database migrations. The future implementation will place reservation business rules in a service layer and use `[start, end)` time intervals.
