# Spec Delta

## Purpose

Defines the administrator review workflow that resolves pending academic-space reservation requests through approval or rejection.

## ADDED Requirements

### Requirement: Administrators can review pending requests
The system SHALL let an administrator view pending reservation requests with their requester, space, purpose, and requested period.

#### Scenario: Administrator lists pending requests
- **GIVEN** one or more reservation requests are pending
- **WHEN** an administrator views requests awaiting review
- **THEN** the system SHALL show each pending request's requester, space, purpose, and requested period

### Requirement: Administrators can approve valid pending requests
The system SHALL allow an administrator to approve a pending request only while its space is active and the request remains valid and non-conflicting.

#### Scenario: Administrator approves a valid request
- **GIVEN** a pending request is for an active space and its requested period remains valid and available
- **WHEN** an administrator approves a pending request for an active space whose requested period remains valid and available
- **THEN** the system SHALL change the request status to approved and record the state change

#### Scenario: Administrator attempts to approve a request for an inactive space
- **GIVEN** a pending request is for an inactive space
- **WHEN** an administrator attempts to approve a pending request whose space is inactive
- **THEN** the system SHALL reject the transition and preserve the request as pending

### Requirement: Administrators can reject pending requests
The system SHALL allow an administrator to reject a pending request and SHALL record the state change.

#### Scenario: Administrator rejects a pending request
- **GIVEN** a reservation request is pending
- **WHEN** an administrator rejects a pending request
- **THEN** the system SHALL change the request status to rejected and record the state change

### Requirement: Review decisions apply only to pending requests
The system SHALL reject approval or rejection attempts for requests that are no longer pending and SHALL preserve their current status.

#### Scenario: Administrator attempts a duplicate decision
- **GIVEN** a request has already been approved or rejected
- **WHEN** an administrator attempts to approve or reject an already approved or rejected request
- **THEN** the system SHALL reject the transition and SHALL NOT alter the request status or its existing decision history
