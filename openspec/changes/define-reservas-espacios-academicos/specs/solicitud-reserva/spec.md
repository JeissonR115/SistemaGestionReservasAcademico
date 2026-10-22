# Spec Delta

## Purpose

Defines how an authenticated requester submits a traceable request to reserve an active academic space for a specified period and purpose.

## ADDED Requirements

### Requirement: Requesters can submit reservation requests
The system SHALL allow an authenticated requester to submit a request for an active space with a purpose, start time, and end time, and SHALL record the requester as its owner.

#### Scenario: Requester submits a valid reservation request
- **GIVEN** an authenticated requester and an active space exist
- **WHEN** an authenticated requester submits an active space, a purpose, and a valid start and end time
- **THEN** the system SHALL create a pending request owned by that requester

#### Scenario: Request omits required information
- **GIVEN** an authenticated requester is submitting a reservation request
- **WHEN** a requester submits a request without a space, purpose, start time, or end time
- **THEN** the system SHALL reject the request and identify the missing information

### Requirement: Reservation request periods must be valid
The system SHALL require a reservation request's start time to precede its end time and SHALL reject requests for inactive or nonexistent spaces.

#### Scenario: Request has an empty or reversed period
- **GIVEN** an authenticated requester is submitting a reservation request
- **WHEN** a requester submits a request whose start time is equal to or later than its end time
- **THEN** the system SHALL reject the request and identify the invalid period

#### Scenario: Request targets an inactive space
- **GIVEN** an authenticated requester is submitting a reservation request
- **WHEN** a requester submits a request for an inactive or nonexistent space
- **THEN** the system SHALL reject the request without creating a reservation

### Requirement: Requesters can review their own requests
The system SHALL let an authenticated requester review the status and submitted details of that requester's reservation requests.

#### Scenario: Requester reviews a submitted request
- **GIVEN** the requester has submitted a reservation request
- **WHEN** a requester views one of that requester's reservation requests
- **THEN** the system SHALL show its space, purpose, requested period, and current status
