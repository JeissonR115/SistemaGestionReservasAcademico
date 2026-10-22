# Tasks

## 1. Reservation service rule

- [ ] 1.1 Implement the four-hour individual and contiguous same-user/same-space validation for new requests; verify service tests for 3h59, exactly 4h, 4h01, pending and approved neighbors, exact-four-hour chains, different users, rejected/cancelled neighbors, and multi-reservation chains.
- [ ] 1.2 Revalidate the duration rule during approval while excluding the request's own ID from neighbor lookup; verify a violating pre-existing pending request stays pending and gains no decision-history entry.

## 2. API and documentation

- [ ] 2.1 Map duration-rule violations to HTTP 400 with a clear message for request creation and approval; verify API tests for requester and administrator roles and that rejected attempts do not create or modify reservations.
- [ ] 2.2 Document the four-hour and contiguous-reservation rule, including HTTP 400 behavior, in the README; verify the documented API and browser behavior against the implementation tests.

## 3. Regression verification

- [ ] 3.1 Run the complete Django test suite, Django system check, migration consistency check, and JavaScript syntax check; verify all pass without changing existing reservation records or unrelated requirements.
