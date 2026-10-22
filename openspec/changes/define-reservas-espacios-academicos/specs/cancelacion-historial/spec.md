# Spec Delta

## Purpose

Defines reservation cancellation and the history needed to trace status changes throughout the lifecycle of a request.

## ADDED Requirements

### Requirement: Requesters can cancel their own active requests
The system SHALL allow a requester to cancel that requester's pending or approved reservation and SHALL reject cancellation of another user's reservation or a reservation that is already rejected or cancelled.

#### Scenario: Requester cancels a pending request
- **GIVEN** a pending reservation belongs to the requester
- **WHEN** a requester cancels that requester's pending reservation
- **THEN** the system SHALL change its status to cancelled and release its period for new requests

#### Scenario: Requester cancels an approved reservation
- **GIVEN** an approved reservation belongs to the requester
- **WHEN** a requester cancels that requester's approved reservation
- **THEN** the system SHALL change its status to cancelled and release its period for new requests

#### Scenario: Requester attempts to cancel another user's reservation
- **GIVEN** a reservation belongs to another user
- **WHEN** a requester attempts to cancel a reservation owned by another user
- **THEN** the system SHALL deny the action and SHALL NOT change the reservation

#### Scenario: Requester attempts to cancel a terminal reservation
- **GIVEN** a reservation is rejected or already cancelled
- **WHEN** a requester attempts to cancel a rejected or already cancelled reservation
- **THEN** the system SHALL reject the transition and preserve the current status

### Requirement: Reservation state changes are traceable
The system SHALL record each reservation status change with the resulting status, the actor responsible, and the time of the change, and SHALL make the history available to an authorized viewer of that reservation.

#### Scenario: Reservation status changes
- **GIVEN** an actor is submitting, approving, rejecting, or cancelling a reservation
- **WHEN** a reservation is submitted, approved, rejected, or cancelled
- **THEN** the system SHALL append a history entry containing the new status, responsible actor, and change time

#### Scenario: Authorized viewer reviews reservation history
- **GIVEN** an authorized viewer can access a reservation
- **WHEN** an authorized viewer opens a reservation's history
- **THEN** the system SHALL show its status-change entries in chronological order
