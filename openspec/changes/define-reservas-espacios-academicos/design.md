# Design

## Context

See `proposal.md` - Why. The repository currently contains the engineering plan and OpenSpec configuration but no Django application code. The plan selects Python 3.12, Django 5, Django REST Framework, SQLite, session authentication, and a lightweight Django-template interface. The capability requirements are defined in `specs/`.

## Goals / Non-Goals

**Goals:**
- Keep the application straightforward to run locally and organize it into the planned Django apps.
- Keep reservation rules independently testable and ensure availability checks remain consistent with request creation and review.
- Make the task sequence traceable to the progressive stages in `PLAN_INGENIERIA.md`.

**Non-Goals:**
- Introduce a production deployment architecture, external identity provider, email delivery, recurring reservations, or a mobile application.
- Add implementation code or dependencies as part of this planning change.

## Decisions

### Use a layered Django monolith

Organize the application into `accounts`, `spaces`, `reservations`, and `web` Django apps, with models and persistence separated from reservation services and API or page views. Use Django REST Framework for the API and Django templates with JavaScript `fetch` for the same-origin web interface. This follows the project plan and avoids the operational overhead of microservices or a separate SPA.

### Keep reservation rules in a service layer

Put availability validation, state transitions, cancellation, and conflict prevention in reservation services, called by API and other entry points. This prevents views from becoming alternate sources of business rules and allows the same behavior to be exercised through unit and API tests. Django views with duplicated rules were rejected because they make consistency harder to maintain.

### Use SQLite and Django-managed persistence

Use SQLite through Django's ORM and versioned migrations, as selected for a low-configuration demonstration system. Do not add another database service for this scope. The known SQLite concurrency limitations are accepted for the planned scale and must be covered by explicit tests and documented in the final report.

### Use session authentication and explicit roles

Use Django session authentication for the same-origin interface and assign users requester or administrator roles. Apply role-based authorization at protected operations and verify both permitted and denied actions in API tests. JWT was rejected because it adds token lifecycle complexity without a separate client requirement.

### Treat reservation intervals as half-open and pending requests as blocking

Represent a reservation period as `[start, end)`, reject periods where `start >= end`, and consider two periods adjacent rather than overlapping when one ends exactly as the other begins. Pending and approved reservations occupy the period; rejected and cancelled reservations release it. The requester confirmed this pending-request policy. This gives availability checks, request creation, and approval one consistent conflict rule.

### Make conflict validation and creation atomic

Perform the final conflict check and persistence as one transaction-protected service operation; a pre-flight availability display is informational and is not sufficient to reserve a slot. If competing requests overlap, at most one may become pending and the other receives a conflict result. SQLite's locking behavior may limit throughput, but silently accepting overlapping reservations is not an acceptable fallback.

## Risks / Trade-offs

- [SQLite write contention can limit simultaneous reservation throughput] → Keep the project at the planned demonstration scale, perform the authoritative conflict check within a transaction, and test competing requests; document the concurrency limitation.
- [Availability can change after a requester views it] → Revalidate availability at request creation and again before approval; return an explicit conflict when a request loses the race.
- [Time-zone or daylight-saving mistakes can misrepresent requested periods] → Use timezone-aware date-time values consistently and configure Django's project time zone; test interval boundaries and time changes.
- [Authorization drift across UI and API entry points can expose administrative actions] → Enforce permissions at the operation boundary and test denied as well as successful requester and administrator actions.

## Migration Plan

No application data migration or deployment is part of this planning change. During implementation, create and migrate the Django schema through versioned migrations before exercising account, space, and reservation workflows. The initial local database can be recreated from migrations; production rollout and rollback are outside this project's scope.

## Open Questions

- Confirm the institution's configured time zone when setting up the Django project. The system will use timezone-aware values regardless of that configuration.
