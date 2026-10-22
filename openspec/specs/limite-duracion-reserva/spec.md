# limite-duracion-reserva Specification

## Purpose

Prevents any user from continuously reserving the same academic space for more than four hours. The limit applies when requests are created and when pending requests are approved, without changing existing reservations.

## Requirements

### Requirement: A reservation cannot exceed four hours
The system SHALL reject a new reservation whose requested duration is greater than four hours, regardless of the requester's role, and SHALL return HTTP 400 with a clear error message.

#### Scenario: Request duration is 3h59
- **GIVEN** an authenticated user of any role requests an available active space
- **WHEN** the requested duration is three hours and fifty-nine minutes
- **THEN** the system SHALL accept the request as pending

#### Scenario: Request duration is exactly four hours
- **GIVEN** an authenticated user of any role requests an available active space
- **WHEN** the requested duration is exactly four hours
- **THEN** the system SHALL accept the request as pending

#### Scenario: Request duration is 4h01
- **GIVEN** an authenticated user of any role requests an available active space
- **WHEN** the requested duration is four hours and one minute
- **THEN** the system SHALL reject the request with HTTP 400 and a clear duration-limit message

### Requirement: Contiguous reservations are limited per user and space
The system SHALL reject a new reservation when it would make the requester's continuous reservation period for the same space exceed four hours; only directly contiguous pending or approved reservations owned by that requester SHALL contribute to the period.

#### Scenario: Same user's contiguous pending reservation makes the total exceed four hours
- **GIVEN** the requester has a pending reservation for a space ending exactly when a new request begins
- **WHEN** the combined continuous period exceeds four hours
- **THEN** the system SHALL reject the new request with HTTP 400 and SHALL NOT create a reservation

#### Scenario: Same user's contiguous approved reservation makes the total exceed four hours
- **GIVEN** the requester has an approved reservation for a space ending exactly when a new request begins
- **WHEN** the combined continuous period exceeds four hours
- **THEN** the system SHALL reject the new request with HTTP 400 and SHALL NOT create a reservation

#### Scenario: Contiguous reservations total exactly four hours
- **GIVEN** the requester has a pending or approved reservation for a space ending exactly when a new request begins
- **WHEN** the combined continuous period is exactly four hours
- **THEN** the system SHALL accept the new request as pending

#### Scenario: Contiguous reservation belongs to a different user
- **GIVEN** another user has a pending or approved reservation for the same space ending exactly when the request begins
- **WHEN** the requester's own requested period does not exceed four hours
- **THEN** the system SHALL NOT count the other user's reservation toward the requester's duration limit

#### Scenario: A contiguous rejected reservation does not contribute
- **GIVEN** the requester has a rejected reservation for the same space ending exactly when a new request begins
- **WHEN** the new request's duration does not exceed four hours
- **THEN** the system SHALL NOT count the rejected reservation toward the requester's duration limit

#### Scenario: A contiguous cancelled reservation does not contribute
- **GIVEN** the requester has a cancelled reservation for the same space ending exactly when a new request begins
- **WHEN** the new request's duration does not exceed four hours
- **THEN** the system SHALL NOT count the cancelled reservation toward the requester's duration limit

### Requirement: Approval revalidates the duration limit
The system SHALL revalidate the four-hour limit before approving a pending reservation, evaluate it as the candidate period while excluding that reservation's own ID from neighboring-reservation lookup, and reject a violation with HTTP 400 while preserving its pending status.

#### Scenario: Approval would exceed four contiguous hours
- **GIVEN** a pending reservation and a directly contiguous pending or approved reservation for the same requester and space together exceed four hours
- **WHEN** an administrator approves the pending reservation
- **THEN** the system SHALL reject the approval with HTTP 400, preserve the request as pending, and exclude its own ID from the neighboring-reservation lookup
