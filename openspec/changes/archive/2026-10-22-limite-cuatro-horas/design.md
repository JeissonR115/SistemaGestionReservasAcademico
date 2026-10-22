# Design

## Context

See `proposal.md` for motivation and `specs/limite-duracion-reserva/spec.md` for the behavioral contract. Reservation creation and approval currently perform their availability checks in `reservations/services.py`; the API maps domain errors to HTTP responses in `reservations/views.py`. The system uses timezone-aware datetimes, pending/approved reservations as blockers, and half-open intervals.

`PLAN_INGENIERIA.md` already assigns business rules to the reservation service layer and includes a Stage 7 task for adding a rule through OpenSpec. This change fits that planned work; no plan update or architectural change is needed.

## Goals / Non-Goals

**Goals:**
- Enforce the four-hour maximum consistently at request creation and approval.
- Count directly contiguous pending or approved reservations only when they belong to the same requester and space.
- Return a clear HTTP 400 response for duration-rule violations without changing the pending request or existing reservation records.

**Non-Goals:**
- Modify or migrate existing reservation records.
- Change overlap prevention, availability reporting, roles, or reservation states.
- Add a configurable duration limit or a new database dependency.

## Decisions

### Keep the rule in the reservation service

Add one reusable service-level validation used by both `create_reservation` and the approval transition. This keeps the API and UI from becoming alternate rule-enforcement paths. The create endpoint and approval action will map this validation failure to HTTP 400, while existing overlap and transition errors retain their current responses.

### Measure the candidate's full contiguous block

First reject a candidate whose own duration exceeds four hours. Then query pending and approved reservations for the same space and requester, excluding the candidate's ID when revalidating approval. Consider the candidate together with those intervals in chronological order and extend its continuous block only across exact end-to-start adjacency. Reject if the resulting block containing the candidate exceeds four hours. A different requester's reservation, a time gap, a rejected reservation, or a cancelled reservation does not extend that block.

This evaluates chains on either side of the candidate, not just a single preceding reservation. Counting all reservations for a space was rejected because the cap is per user; checking only the candidate's own duration was rejected because it would allow a user to exceed the cap through adjacent requests.

### Preserve atomicity and existing records

Run validation within the existing transaction and space-locking flow, after obtaining the authoritative space state. On approval, exclude the request under review from the neighbor query by its ID and use its start/end as the candidate exactly once. A violation leaves the reservation pending, creates no decision log entry, and does not modify any other record. Adding this rule to availability previews alone was rejected because creation and approval must remain authoritative.

### Keep the current project plan

Do not edit `PLAN_INGENIERIA.md`: it already places reservation rules in the service layer and explicitly calls for an OpenSpec-backed new rule in Stage 7. The new capability and regression tests fulfill that planned task without changing its scope or sequence.

## Risks / Trade-offs

- [Contiguous reservations can form chains of several records] → Sort all eligible intervals and evaluate the contiguous block containing the candidate rather than checking only one neighbor.
- [An existing pending reservation may violate the new limit] → Leave it unchanged as required, but revalidate it at approval and reject the approval with HTTP 400.
- [SQLite limits write concurrency] → Reuse the existing transaction and per-space serialization; do not weaken current conflict checks.

## Migration Plan

No schema migration is required. Deploy the service validation and API error mapping together. Existing reservations remain untouched. Rollback consists of reverting the application change; no data rollback is needed.

## Open Questions

None.
