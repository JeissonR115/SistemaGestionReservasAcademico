# Proposal

## Why

The reservation system currently prevents overlapping bookings but does not limit how long one user can continuously occupy the same space. A four-hour cap will make reservation duration fairer while preserving the existing pending/approved blocking rules and all historical records.

## What Changes

- Limit every new reservation to at most four hours, regardless of whether the requester is an administrator or another role.
- Reject a request when its interval, combined with directly contiguous pending or approved reservations by the same user for the same space, creates a continuous block longer than four hours.
- Revalidate the same rule when approving a pending request, excluding that request by ID from the neighboring-reservation lookup.
- Return HTTP 400 with a clear message when the duration rule is violated; do not modify existing reservations.
- Add regression scenarios for 3h59, exactly 4h, 4h01, contiguous reservations by the same or a different user, and a contiguous rejected reservation.

## Capabilities

### New Capabilities

- `limite-duracion-reserva`: Enforce an individual and same-user contiguous reservation duration limit during request creation and approval.

### Modified Capabilities

None. The repository has no main specs yet (`openspec list --specs` returns no capabilities); this change introduces a dedicated capability rather than silently changing an unarchived delta.

## Impact

- Affects reservation validation in `reservations/services.py`, its API error handling in `reservations/views.py`, and regression tests in `reservations/tests.py`.
- Adds a spec-level rule for creation and approval; no model or migration change is expected.
- `PLAN_INGENIERIA.md` already places reservation business rules in the service layer and explicitly schedules a new OpenSpec rule in Stage 7. The rule fits that planned scope and does not require changing the plan's architecture, stages, or deliverables.
- Existing reservations remain unchanged; the rule applies to new requests and approval revalidation only.
