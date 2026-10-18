# UniSphere Implementation Plan
## Suggested modules
accounts handles authentication and roles; academics handles programmes, subjects, offerings and enrolments; learning handles lessons, protected resources and transcripts; assessments handles assignments, submissions and marks; attendance handles sessions and corrections; results handles grade policies and published results; finance handles simulated fee records; quizzes handles practice and live sessions; support handles tickets; notifications handles portal events and email outbox; assistant handles authorised tools and material retrieval; audit handles sensitive record events.
## Proposed source organisation
Use a Django project with one application per domain or a reduced grouping where appropriate. Keep templates and static assets version-controlled, uploads outside the public source tree, tests beside each module, and documentation in docs. Add migrations, deterministic demo fixtures and an environment example with empty secret values during implementation.
## Delivery order
1. Confirm rubric, personal metadata and sample academic policy.
2. Implement identity, enrolments, protected resources and seed data.
3. Complete assignment publication, submission receipt and feedback.
4. Implement a restricted pending-work AI query and verify negative access cases.
5. Complete attendance, schedules, results, programme structure and simulated finance.
6. Add grounded tutoring and independent practice.
7. Implement live quizzes with server deadlines and reconnect state.
8. Implement ticket routing, portal notifications and email outbox.
9. Run the PRD test suite, usability tasks and final demonstration.
## Demo fixtures
Use 20 fictional students, two lecturers, one admin, three current offerings, prior published results, at least three complete lessons with transcripts, and deliberately varied submission and attendance states. Resetting fixtures must be explicit and must not silently delete user-created work.
## Package boundaries
This folder contains documentation and editable design sources, not application source code. Do not describe it as a completed portal. The proposed framework and exact supported dependency versions must be verified before creating an installable implementation.
