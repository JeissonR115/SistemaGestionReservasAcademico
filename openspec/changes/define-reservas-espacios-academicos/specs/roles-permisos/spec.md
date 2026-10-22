# Spec Delta

## Purpose

Defines requester and administrator roles and the authorization boundaries that protect account, space, and reservation operations.

## ADDED Requirements

### Requirement: Users have an assigned system role
The system SHALL associate each user account with a requester or administrator role and SHALL use that role when authorizing protected actions.

#### Scenario: User account receives a role
- **GIVEN** an authorized administrator is managing a user account
- **WHEN** an authorized administrator creates or updates a user account with a valid role
- **THEN** the system SHALL associate that role with the account

#### Scenario: Account has no valid role
- **GIVEN** an authorized administrator is creating or updating an account
- **WHEN** an account is created or updated without a valid role
- **THEN** the system SHALL reject the change and SHALL NOT grant access to protected actions

### Requirement: Requesters are limited to requester operations
The system SHALL allow an authenticated requester to view the active space catalog, create reservation requests, and view or cancel only that requester's own reservations.

#### Scenario: Requester attempts an administrative action
- **GIVEN** a requester is authenticated
- **WHEN** a requester attempts to manage spaces, manage user accounts, or review another user's request
- **THEN** the system SHALL deny the action without changing system data

#### Scenario: Requester views another user's reservation
- **GIVEN** a reservation belongs to another user
- **WHEN** a requester requests access to a reservation owned by another user
- **THEN** the system SHALL deny access to that reservation

### Requirement: Administrators can perform administrative operations
The system SHALL allow an authenticated administrator to manage spaces and user accounts and to review reservation requests.

#### Scenario: Administrator performs a protected operation
- **GIVEN** an administrator is authenticated
- **WHEN** an administrator submits a valid space, account, or reservation-review operation
- **THEN** the system SHALL authorize the operation

#### Scenario: Unauthenticated user attempts a protected operation
- **GIVEN** a user has no authenticated session
- **WHEN** a user without an authenticated session attempts an operation restricted to authenticated users
- **THEN** the system SHALL deny the operation and SHALL NOT change system data
