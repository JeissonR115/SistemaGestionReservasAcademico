# Spec Delta

## Purpose

Defines the user accounts and authentication behavior needed to identify people who request, review, and manage academic-space reservations.

## ADDED Requirements

### Requirement: Administrators can manage user accounts
The system SHALL allow an authorized administrator to create and update user accounts and to deactivate accounts that must no longer access the system.

#### Scenario: Administrator creates an account
- **GIVEN** an authorized administrator is managing user accounts
- **WHEN** an authorized administrator submits the required account details for a new user
- **THEN** the system SHALL create an account that can be assigned a role

#### Scenario: Administrator deactivates an account
- **GIVEN** an active user account exists
- **WHEN** an authorized administrator deactivates an active account
- **THEN** the system SHALL prevent that account from starting a new authenticated session

### Requirement: Active users can authenticate
The system SHALL allow an active user to establish and end an authenticated session, and SHALL reject authentication when the credentials are invalid or the account is inactive.

#### Scenario: Active user signs in with valid credentials
- **GIVEN** a user account is active
- **WHEN** an active user submits valid credentials
- **THEN** the system SHALL establish an authenticated session associated with that user

#### Scenario: Inactive user attempts to sign in
- **GIVEN** a user account is inactive
- **WHEN** an inactive user submits credentials that would otherwise be valid
- **THEN** the system SHALL reject the sign-in and SHALL NOT establish an authenticated session

#### Scenario: Authenticated user signs out
- **GIVEN** a user has an authenticated session
- **WHEN** an authenticated user signs out
- **THEN** the system SHALL end that user's authenticated session
