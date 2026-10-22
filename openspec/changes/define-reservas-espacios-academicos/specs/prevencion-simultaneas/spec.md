# Spec Delta

## Purpose

Ensures that simultaneous requests cannot both claim overlapping time on the same academic space, even when each request initially observes the space as available.

## ADDED Requirements

### Requirement: Conflicting reservation requests are resolved atomically
The system SHALL ensure that checking for a blocking reservation and recording a new pending reservation are an indivisible operation with respect to competing requests for the same space and overlapping period.

#### Scenario: Two simultaneous requests compete for an available period
- **GIVEN** a space and period are available and two requesters submit overlapping requests concurrently
- **WHEN** two requesters concurrently submit overlapping requests for the same available space
- **THEN** the system SHALL accept at most one request as pending and SHALL reject the other with a conflict outcome

#### Scenario: A competing request arrives after a pending request is recorded
- **GIVEN** a pending request has already been recorded for a space and period
- **WHEN** a requester submits a request that overlaps a previously recorded pending request for the same space
- **THEN** the system SHALL reject the new request and SHALL preserve the existing request

### Requirement: Conflict rejection does not create a reservation
The system SHALL NOT persist a reservation request as pending when a conflicting pending or approved reservation already occupies the requested period.

#### Scenario: Request loses a conflict check
- **GIVEN** a pending or approved reservation occupies part of the requested period
- **WHEN** a request is found to overlap a pending or approved reservation for the same space before it is recorded
- **THEN** the system SHALL return a conflict outcome and SHALL NOT create a second blocking reservation
