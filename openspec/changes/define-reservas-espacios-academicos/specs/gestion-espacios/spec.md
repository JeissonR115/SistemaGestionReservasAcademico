# Spec Delta

## Purpose

Defines how academic spaces are described and maintained so requesters can find suitable spaces and administrators can keep the catalog accurate.

## ADDED Requirements

### Requirement: Administrators can maintain academic spaces
The system SHALL allow an authorized administrator to create and update a space's name, type, capacity, and active status, and SHALL reject a space with missing required values or a non-positive capacity.

#### Scenario: Administrator creates a valid space
- **GIVEN** an authorized administrator is managing the space catalog
- **WHEN** an authorized administrator submits a name, type, positive capacity, and active status
- **THEN** the system SHALL create the space and make its details available in the space catalog

#### Scenario: Space has invalid capacity
- **GIVEN** an administrator is managing the space catalog
- **WHEN** an administrator submits a space with a capacity of zero or less
- **THEN** the system SHALL reject the change and identify capacity as invalid

### Requirement: Requesters can find active spaces
The system SHALL let a requester view active spaces and their name, type, and capacity, and SHALL NOT present inactive spaces as available for new reservations.

#### Scenario: Catalog lists an active space
- **GIVEN** the space catalog contains an active space
- **WHEN** a requester views the space catalog containing an active space
- **THEN** the system SHALL show that space's name, type, and capacity

#### Scenario: Inactive space is excluded from catalog
- **GIVEN** the space catalog contains an inactive space
- **WHEN** a requester views the catalog and a space is inactive
- **THEN** the system SHALL NOT present that space as available for a new reservation
