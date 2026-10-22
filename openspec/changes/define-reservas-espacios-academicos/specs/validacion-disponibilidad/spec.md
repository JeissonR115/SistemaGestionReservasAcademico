# Spec Delta

## Purpose

Defines how the system reports whether an academic space can be requested for a given period, including conflicts and interval boundaries.

## ADDED Requirements

### Requirement: Availability reflects blocking reservations
The system SHALL report a space as unavailable for a requested period when that space has an overlapping pending or approved reservation, and SHALL treat rejected and cancelled reservations as non-blocking.

#### Scenario: Pending request blocks availability
- **GIVEN** a pending request exists for a space and period
- **WHEN** availability is checked for a period that overlaps a pending request for the same space
- **THEN** the system SHALL report the space as unavailable for that period

#### Scenario: Rejected or cancelled request does not block availability
- **GIVEN** rejected or cancelled requests overlap the checked period for a space
- **WHEN** availability is checked for a period that overlaps only rejected or cancelled requests for the same space
- **THEN** the system SHALL report the space as available for that period

### Requirement: Reservation intervals use half-open boundaries
The system SHALL interpret reservation periods as half-open intervals `[start, end)`, so two periods for the same space do not overlap when one ends exactly as the other begins.

#### Scenario: Adjacent reservations do not overlap
- **GIVEN** one reservation ends at the exact time another period begins for the same space
- **WHEN** one reservation ends at the exact time another reservation for the same space begins
- **THEN** the system SHALL treat the periods as non-overlapping and report the later period as available if no other conflict exists

#### Scenario: Intersecting reservations overlap
- **GIVEN** a pending or approved reservation exists for a space
- **WHEN** a requested period shares any time after its start and before its end with a pending or approved reservation for the same space
- **THEN** the system SHALL report the requested period as unavailable

### Requirement: Inactive spaces are unavailable
The system SHALL report an inactive space as unavailable for a new reservation regardless of whether it has overlapping reservations.

#### Scenario: Availability checked for an inactive space
- **GIVEN** a space is inactive
- **WHEN** availability is checked for a period on an inactive space
- **THEN** the system SHALL report that space as unavailable for new reservations
