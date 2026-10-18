# UniSphere Product Requirements Document
Version 1.0 | 18 October 2026
Product owner Shri Vignarohan A/L S. Ramasamy
Status Proposed requirements for supervisor review

## 1 Product Overview
UniSphere is a demonstration university academic portal combining student services, lecturer workflows and administrative management with a contextual AI assistant. Users can complete all core academic tasks manually. The assistant opens from a floating bottom-right control and uses the same authorised records as the portal.
This document specifies the finished demonstration and separates the Project 1 vertical slice from later delivery. It is a build specification, not evidence that the application has been implemented, tested or approved.
### Goals
G1 Organise academic tasks in a coherent role-specific interface. G2 Connect publication, submission, feedback and progress records. G3 Help students recover missed lessons using actual resources. G4 Support personal practice and interactive class quizzes. G5 Track support requests and notifications. G6 enforce record access consistently through both pages and AI tools.
### Non goals
Production university integration, real payment collection, biometric attendance, automatic official grading, native apps and live video classes are excluded. Broad claims that AI replaces lecturers or predicts academic failure are excluded.
### Evidence and differentiation
The project begins from the owner's experience of a confusing portal and requires local validation. Edinburgh's LOUISA work supports investigating inconsistent assessment navigation; it does not prove the same findings locally. Moodle already supports quizzes, reusable questions and feedback. UniSphere should therefore be evaluated on integration and selected workflows rather than an unsupported claim of uniqueness.

## 2 Users and Access
Student accounts access their own records and enrolled resources. Lecturer accounts access their assigned offerings, enrolled students and relevant teaching records. Admin accounts have overall management authority for users and operational records. Private student AI conversations are not included in routine admin browsing; diagnostics use access-controlled event metadata.
| Resource | Student | Lecturer | Admin |
| --- | --- | --- | --- |
| Personal academic and finance records | Own only | Teaching records only and no finance | Manage with audit |
| Class materials | Enrolled and published | Assigned offerings | Manage |
| Submissions | Own versions | Assigned offering | Authorised oversight |
| Attendance | Own and correction requests | Assigned offering | Manage with reason |
| Marks | Own released marks | Enter and release for assigned offering | Controlled correction |
| Live quizzes | Join enrolled class | Host assigned class | Manage operational issues |
| Tickets | Participant only | Participant only | Support oversight and reassignment |
| User roles and enrolment | No | No | Manage |

## 3 Delivery Scope
P1 means the proposed Project 1 milestone. P2 means completion after that milestone. Both remain part of the finished demo unless changed through scope review.
P1 includes role selection and authentication, seeded users and enrolments, core dashboards, subject materials, assignments, attendance display, restricted AI pending-work retrieval and foundational security. P2 completes attendance editing, timetable and exams, results, finance, catch-up tutoring, practice, live quizzes, tickets, email and overall evaluation.
The representative dataset is 20 students, two lecturers, one admin and three current subject offerings. Historical released results support a meaningful CGPA demonstration. Content and payment records are fictional or authorised. All UI views must identify sample payments as simulated.

## 4 Functional Requirements
Each requirement below includes a minimum acceptance condition. The phase identifies delivery order, not optional status.
### FR01 Role entry and authentication
Delivery P1. Acceptance: Show Student and Lecturer choices and a smaller Admin option beneath. Valid credentials open the account role dashboard; role mismatch or invalid credentials grants no elevated access.

### FR02 Authorisation and session handling
Delivery P1. Acceptance: Unauthenticated requests cannot read protected pages or APIs. Student A cannot read Student B records by changing an identifier. Logout invalidates the session.

### FR03 Student dashboard
Delivery P1. Acceptance: Show today's classes, outstanding work, attendance, published GPA or an unavailable state, next exam and balance. Counts match detailed records; draft and cancelled items are excluded.

### FR04 Subject workspace
Delivery P1. Acceptance: An enrolled student sees published topics, materials and lecturer contacts for an offering. A non-enrolled student cannot download its private resources.

### FR05 Material publication
Delivery P1. Acceptance: An assigned lecturer uploads a permitted file, associates a lesson and publishes it. Students cannot see drafts. Replacing content retains version and uploader metadata.

### FR06 Assignment authoring
Delivery P1. Acceptance: A lecturer creates a draft with instructions, deadline, allowed formats, maximum score, late policy and optional rubric. Publication exposes it only to the selected offering.

### FR07 Assignment submission
Delivery P1. Acceptance: A permitted upload creates a versioned submission and receipt with server timestamp. Disallowed types and sizes are rejected. Failed uploads do not display success.

### FR08 Submission tracking and feedback
Delivery P1. Acceptance: Lists distinguish pending, submitted, submitted late, overdue and graded. A lecturer saves draft marks and releases feedback; students cannot see draft marks.

### FR09 Attendance display
Delivery P1. Acceptance: Display per-offering sessions and percentages from recorded statuses. Zero counted sessions displays not available. A missed session links to its lesson if one exists.

### FR10 Attendance recording and correction
Delivery P2. Acceptance: An assigned lecturer records present, absent, late or excused. Corrections require a reason and audit entry. Students can raise a correction request without editing the record.

### FR11 Timetable and examinations
Delivery P2. Acceptance: Show class and published exam date, time, venue and subject. Cancelled classes are labelled; server timestamps display in Asia/Kuala_Lumpur.

### FR12 Programme structure
Delivery P2. Acceptance: Show semesters, subjects, credits, prerequisites and completion state. Completed credits derive from qualifying published results, not lesson completion.

### FR13 Results and CGPA
Delivery P2. Acceptance: Display released results and credit-weighted semester GPA and CGPA using the configured policy. Missing grades are not zero. Scenario calculations do not modify records.

### FR14 Learning progress and catch up
Delivery P2. Acceptance: Track lesson activity and catch-up completion separately from attendance. A student completing a catch-up quiz does not become present in the original session.

### FR15 Finance and simulated payment
Delivery P2. Acceptance: Show student-owned fee items, due dates, instructions, balances and history. A labelled simulated success creates one receipt; a duplicate request creates no duplicate payment.

### FR16 Lecturer overview
Delivery P1. Acceptance: Show assigned offerings, upcoming classes, outstanding submissions and marking queue. Records from unrelated offerings are unavailable.

### FR17 Attention filters
Delivery P2. Acceptance: Filter attendance below threshold, overdue counts and released assessment performance. Display the trigger and relevant denominator; insufficient evidence is not a low-performance label.

### FR18 Admin management
Delivery P1. Acceptance: Admin manages active users, roles, offerings and enrolments. Deactivating a user blocks new access without deleting historical academic records.

### FR19 Admin records and policies
Delivery P2. Acceptance: Admin maintains programme structure, timetable, exams, grade policy, fees and ticket categories. Sensitive changes record actor, time and reason.

### FR20 Floating assistant and record queries
Delivery P1. Acceptance: Bottom-right control opens a keyboard-accessible chat panel. A pending-assignment query returns the signed-in student's actual records with links, after backend access checks.

### FR21 Learning material tutoring
Delivery P2. Acceptance: Retrieve published enrolled-resource excerpts and transcripts, explain a topic and cite page or resource links. A missing lesson yields an unavailable response rather than invented content.

### FR22 AI isolation and failure handling
Delivery P2. Acceptance: Requests for another student's records are denied. Instructions embedded in documents cannot grant privileges. Provider failure shows an error while manual workflows remain usable.

### FR23 Quiz Me
Delivery P2. Acceptance: Student chooses offering, topic, difficulty and question count. Practice shows a saved score, explanations, sources and retry. Practice attempts never enter official GPA.

### FR24 Quiz authoring
Delivery P2. Acceptance: Lecturer creates multiple-choice questions or reviews an AI draft. Every published question has one valid answer and points; AI drafts require explicit lecturer approval.

### FR25 Launch and invite
Delivery P2. Acceptance: Launching Quiz Your Students creates one waiting session and one portal invitation per active enrolled student. Students join using an authenticated link or code; outsiders are rejected.

### FR26 Live question lifecycle
Delivery P2. Acceptance: Host controls waiting, active question, review and finished states. The server determines deadlines. One accepted answer per student per question is scored server-side; late answers are rejected.

### FR27 Reconnect and results
Delivery P2. Acceptance: Reconnect reloads current state and saved answer without a fresh timer. Host sees participation and answer distributions. Results persist; optional leaderboards use aliases.

### FR28 Ticket routing
Delivery P2. Acceptance: All roles can choose an eligible recipient type and recipient, contextual category including Other, subject and description. The server validates recipient eligibility and related record access.

### FR29 Ticket conversation
Delivery P2. Acceptance: Submission creates a unique reference. Participants can reply with permitted attachments and view history. Open, in progress, awaiting response, resolved and closed transitions are recorded; unresolved issues may be reopened.

### FR30 Ticket notification and email
Delivery P2. Acceptance: Ticket creation and replies create portal notifications and queued email events for the other participant or assigned support recipient. Email includes a protected portal link and no sensitive attachment.

### FR31 Email delivery resilience
Delivery P2. Acceptance: Persist pending, accepted by provider, delivered when reported, failed and retry states. A failed email does not roll back a ticket. Retry uses bounded attempts and duplicate prevention.

### FR32 Admin ticket oversight
Delivery P2. Acceptance: Admin support inbox filters by category, status and assignee. Reassignment notifies the new receiver and retains history. Admin can initiate tickets to students and lecturers.

### FR33 Announcements search and notifications
Delivery P2. Acceptance: Publish offering or system announcements to eligible users. Search filters by authorisation before returning results. Notifications open the correct record and support read status.

### FR34 Protected files and audit
Delivery P1. Acceptance: Authorise every file download, store uploads privately and log important record changes. File names alone never determine download permission.

## 5 Business Rules
### Academic records
BR01 Subject offerings are semester-specific instances; student enrolment and lecturer assignment determine access. BR02 Draft materials, assignments and marks are not student-visible. BR03 Official results require explicit publication; assessment progress is not a final grade.
BR04 GPA equals sum of grade points multiplied by counted credit hours divided by counted credit hours. CGPA applies the same calculation across qualifying released results. The demo uses a documented sample grade scale and highest qualifying published attempt per repeated subject; this is a demo rule, not an asserted university policy. Excluded or ungraded subjects do not enter the denominator. Display rounding to two decimals occurs only after calculation.
BR05 Sample attendance policy counts present and late as attended, absent as not attended, and excludes excused and cancelled sessions from the denominator. Policy changes require explicit admin configuration and recalculation. Catch-up never changes attendance.
BR06 An assignment is pending before its effective deadline without submission and overdue after the deadline without submission. A student-specific approved extension changes that deadline. At or before the server deadline is on time. Submission timestamps use the final committed upload, and the receipt states this rule.
BR07 Academic performance flags use released evidence only. Report assessment coverage alongside any average. Unreleased assessments are not zeros. Learning-resource viewing is activity evidence rather than proof of understanding.
### Quiz and notification rules
BR08 Practice and class quiz scores are formative by default. Use fixed points per correct answer and no speed bonus initially. Equal scores share a rank. Only selected class enrolments receive invitations, not every university account.
BR09 Live quiz answer keys are withheld from student payloads until the review state. Server timestamps determine question closure. A unique session, question and student key prevents duplicate answers. Launching twice with the same operation key does not create duplicate sessions or invitations.
BR10 Ticket categories depend on recipient type. Students select assigned lecturers or Admin Support; lecturers select enrolled students or Admin Support; admins select active users or an admin colleague. Ticket content remains accessible only to participants and authorised support administrators.
BR11 Status changes and replies produce one event each. Email delivery is asynchronous. An SMTP acceptance is not proof of inbox delivery. Demo emails go only to explicitly configured test recipients; synthetic addresses must not receive mail.
BR12 Finance amounts use decimal currency values in MYR. Simulated payments use operation keys to prevent duplicate receipts. Lecturers have no finance access. A simulation cannot produce a real-payment confirmation.

## 6 User Journeys
### Student submission
Sign in, open pending assignments, review instructions, upload and confirm, receive receipt, later open released feedback. Missing file, disallowed type, expired deadline and network failure produce explicit recoverable states.
### Missed lesson recovery
Open missed session or ask the assistant about a date. Select the actual offering when several sessions match. Open notes and recording, request explanation, complete practice and record catch-up completion. If resources are absent, show that limitation and a lecturer-contact or ticket link.
### Lecturer hosted quiz
Choose assigned offering, prepare and review questions, launch waiting room, notify class, admit authorised students, start server-timed questions, review answers, finish and inspect results. Reconnection must preserve accepted answers and current state.
### Ticket and email
Sender selects recipient and category, submits description and receives reference. Receiver gets portal notification and email link, signs in and replies. Sender is notified. Resolution and reopening remain visible in the thread. A failed email appears in delivery history without losing the ticket.
### Admin management
Create or deactivate accounts, assign subject enrolments, publish exam records and maintain sample fees. Inspect a ticket queue and sensitive-change audit entries. No UI role switch bypasses authentication.

## 7 Screen Map and Interface Requirements
Entry page has two primary role cards and a smaller Admin option below. Each portal has grouped sidebar navigation, a top notification bell, global search and an account menu. The assistant floats bottom right and must not cover submission controls or mobile navigation.
Student groups are Overview, Academics, Learning, Assessments, Performance, Finance and Support. Lecturer groups are Overview, Teaching, Assessments, Attendance, Quizzes and Support. Admin groups are Users, Academic Setup, Schedules, Results, Finance, Tickets, Notifications and Activity.
All lists need filters, meaningful empty states, loading indicators and explicit errors. Display text labels alongside status colours. Destructive or record-changing actions require confirmation where appropriate. Mobile layouts must preserve upload and quiz usability. Attendance, grade and progress charts include accessible numeric summaries.

## 8 Architecture and Implementation Boundaries
[IMAGE architecture.png]
The proposed baseline uses a Django application and responsive server-rendered pages to limit frontend complexity, PostgreSQL for relational records, private file storage, a background outbox worker for email and a WebSocket-capable channel for live quiz events. Exact supported dependency versions are selected and locked during implementation.
The AI adapter exposes small functions such as get_my_pending_assignments, get_my_attendance, get_my_fee_balance and find_enrolled_lesson. The server derives identity from the session; the model cannot choose an arbitrary student identifier. Material retrieval filters eligible offerings and publication state before search. Responses carry record or excerpt identifiers for clickable citations.
Store prepared transcripts with lesson resources; automatic transcription is optional. A model-provider failure cannot disable assignment submission. Do not present canned fallback text as a successful live AI response. Email demonstration uses an authorised test mailbox or a labelled local email preview; only actual delivery counts as a delivered email.

## 9 Conceptual Data Model
The following schema groups identify entities and important fields. Implementation migrations will add indexes, constraints and policy versions.
| Group | Entities and important fields |
| --- | --- |
| Identity | users id email password_hash role active; student_profiles user_id programme_id; lecturer_profiles user_id contact |
| Academic setup | programmes; semesters; subjects code credits; programme_subjects semester_index prerequisite; offerings subject_id semester_id |
| Membership | enrolments student_id offering_id unique; teaching_assignments lecturer_id offering_id unique |
| Sessions | class_sessions offering_id starts_at ends_at venue cancelled; attendance session_id student_id status unique |
| Learning | lessons offering_id session_id topic; resources lesson_id private_path version published_at; chunks resource_id page text; transcripts lesson_id timestamp text |
| Assessment | assignments offering_id due_at late_policy max_score published_at; extensions assignment_id student_id deadline; submissions assignment_id student_id version committed_at file_id |
| Results | feedback submission_id mark released_at; grade_policies; published_results enrolment_id attempt grade_points credits status |
| Progress | lesson_progress student_id lesson_id completion_type completed_at; exam_events offering_id start end venue published_at |
| Finance | fees student_id amount due_at; simulated_payments fee_id operation_key amount status; receipts payment_id reference |
| Quizzes | quizzes offering_id mode status; questions quiz_id options answer_key points source; sessions quiz_id host_id state question_deadline; participants session_id student_id alias; answers session_id question_id student_id choice accepted_at |
| Support | ticket_categories recipient_type; tickets sender_id recipient_id team assignee_id category_id state related_record; replies ticket_id author_id body; ticket_events ticket_id actor_id action |
| Operations | announcements audience; notifications recipient_id event_key read_at; email_outbox event_key receiver state attempts; audit_logs actor_id action record_type record_id reason timestamp |
| AI | conversations owner_id; messages conversation_id role body; tool_events conversation_id tool_name outcome; resource_citations message_id resource_id location |
A student has many enrolments; an offering has many sessions, lessons and assignments. A session has many attendance records. A quiz has many questions and sessions; a session has many participants and answers. A ticket has many replies and events. Event keys and operation keys enforce idempotency. Historical records use archival or soft-deletion rules rather than unrestricted cascading deletion.

## 10 Proposed API Contract
Routes are illustrative contracts for implementation, not existing endpoints. Every object route enforces record permissions.
| Method and route | Purpose and boundary |
| --- | --- |
| POST /auth/login and /auth/logout | Session lifecycle and role validation |
| GET /api/me/dashboard | Authorised personal summary |
| GET /api/offerings/{id} | Enrolled or assigned offering workspace |
| POST /api/offerings/{id}/assignments | Assigned lecturer creates draft |
| POST /api/assignments/{id}/publish | Explicit lecturer publication |
| POST /api/assignments/{id}/submissions | Enrolled student commits upload |
| POST /api/submissions/{id}/feedback | Assigned lecturer stores or releases feedback |
| GET or POST /api/sessions/{id}/attendance | Self view or assigned lecturer record |
| GET /api/me/results and /api/me/fees | Own published academic or finance records |
| POST /api/fees/{id}/simulate-payment | Own fee and idempotent simulation |
| POST /api/assistant/messages | Session-scoped query and cited response |
| POST /api/practice | Own enrolled-resource practice attempt |
| POST /api/quizzes/{id}/launch | Host-controlled session creation |
| POST /api/quiz-sessions/{id}/join | Authenticated enrolled participant |
| POST /api/quiz-sessions/{id}/answers | Server validates state and answer deadline |
| POST /api/quiz-sessions/{id}/advance | Host only |
| GET /api/quiz-sessions/{id}/state | Authorised reconnect snapshot |
| POST /api/tickets | Validated recipient and category |
| POST /api/tickets/{id}/replies | Participant reply and notification event |
| PATCH /api/tickets/{id}/status | Authorised state transition |
| GET /api/notifications | Current user's notifications |
| GET /api/files/{id}/download | Authorised private resource or submission |
Live events include quiz.invited, participant.joined, question.opened, question.closed, session.finished and notification.created. Student snapshots exclude unreleased answer keys. Mutating HTTP operations require CSRF protection for cookie sessions. Validation failures return actionable messages; access failures reveal no private record details.

## 11 Nonfunctional Requirements
All numbers below are proposed acceptance targets, not measured results. Record hardware, dataset, network and provider conditions with test evidence.
| ID | Target | Verification |
| --- | --- | --- |
| NFR01 | Ordinary non-AI page response p95 under 2 seconds for 20 active demo clients | Timed representative requests on declared test machine |
| NFR02 | Quiz state propagation p95 under 1 second after server transition on demo LAN | Compare server event time and client receipt across clients |
| NFR03 | AI request shows progress immediately and times out by 30 seconds | Slow and unavailable provider tests |
| NFR04 | Portal ticket notification appears within 5 seconds; first email send attempt within 60 seconds | Compare stored event, notification and outbox timestamps |
| NFR05 | All negative access tests deny cross-student and unrelated-lecturer access | Direct API, download and AI-tool tests |
| NFR06 | Passwords are securely hashed and provider secrets stay server-side | Configuration and storage review |
| NFR07 | Representative pages usable at 375 and 1440 pixel widths with keyboard navigation | Manual task tests and focus review |
| NFR08 | At least 80 percent of a small exploratory user sample completes core tasks without help | Record task completion and errors; report sample size |
| NFR09 | Restart preserves accepted submissions, quiz answers and tickets | Restart and restore tests with saved fixtures |
| NFR10 | No critical calculation mismatch against fixed GPA, attendance and payment fixtures | Automated expected-value checks |
Security requirements include safe template rendering, request validation, upload type and size validation, non-executable private storage, rate limits on login and AI, short-lived reset tokens, secret exclusion from version control and server-side authorisation on live connections. Deactivation and session expiry must also end live access. Hosting outside localhost requires transport encryption.

## 12 Evaluation and Acceptance Tests
| Test | Requirements | Expected evidence |
| --- | --- | --- |
| T01 | FR01 FR02 FR18 | Correct role login and denied privilege changes |
| T02 | FR04 FR05 FR34 | Draft and non-enrolled downloads denied |
| T03 | FR06 FR07 FR08 | Publish, submit, receive receipt and release feedback |
| T04 | FR07 BR06 | Before, at and after deadline; extension; failed upload |
| T05 | FR09 FR10 BR05 | Known attendance totals, zero sessions and audited correction |
| T06 | FR11 FR12 FR13 | Timetable, programme credits and GPA fixtures |
| T07 | FR13 BR04 | Repeat, excluded and ungraded subjects plus display rounding |
| T08 | FR14 FR21 | Correct missed lesson and unchanged original attendance |
| T09 | FR15 BR12 | Simulated success, failure and duplicate request |
| T10 | FR16 FR17 | Filter exact seeded students and exclude insufficient evidence |
| T11 | FR20 FR21 FR22 | 20 record queries and 10 material questions checked against fixtures |
| T12 | FR22 FR34 | Cross-student requests and malicious document instructions denied |
| T13 | FR23 FR24 | Practice explanations and lecturer-reviewed question publication |
| T14 | FR25 FR26 FR27 | Multiple clients, outsider rejection, late answer, duplicate answer and reconnect |
| T15 | FR28 FR29 FR32 | Each supported sender route, invalid recipient and full ticket lifecycle |
| T16 | FR30 FR31 | Receiver portal notification and authorised test-mailbox evidence |
| T17 | FR31 | Provider outage, retry cap and duplicate-event prevention |
| T18 | FR19 FR33 FR34 | Admin correction audit, scoped search and notification link |
| T19 | NFR01 NFR02 NFR07 | Response timings and desktop/mobile keyboard task records |
| T20 | NFR08 NFR09 | Exploratory usability tasks and restart preservation |
AI evaluation records question, expected records, returned records, source validity, factual errors and unauthorised disclosure. Structured record answers target 100 percent correctness on the fixed test set; grounded teaching targets at least 90 percent supported answers under a documented manual rubric. Any unauthorised disclosure blocks acceptance. These targets do not establish accuracy on all future queries.
For usability, recruit approximately 5 to 8 students and 2 lecturers if available. Compare matched tasks on a lawful baseline or a neutral baseline mock-up and UniSphere, counterbalancing task order where possible. Measure time, success, errors and perceived ease. Report limitations of the small convenience sample and do not fabricate participant outcomes.

## 13 Milestones and Definition of Done
Project 1 is complete when the documented requirements and diagrams agree, all three roles authenticate, a lecturer publishes an assignment, an enrolled student submits it and receives a receipt, attendance is visible and the assistant correctly retrieves personal pending work. Relevant access and workflow tests must pass. This milestone is proposed until confirmed against the course rubric.
The finished demo adds all P2 requirements, three-client minimum live quiz evidence, actual authorised email-delivery evidence or a clearly disclosed preview limitation, source-grounded missed-class assistance, and repeatable seed data. Implementation status must be tracked honestly in README and test records.
No milestone is labelled approved or passed until the supervisor or test evidence supports it.

## 14 Risks Dependencies and Open Decisions
| Item | Planned response |
| --- | --- |
| Scope pressure | Complete vertical workflows and defer optional extras before reducing quality |
| Model access and cost | Configurable adapter, request budgets and manual fallback |
| Email configuration | Authorised test mailbox, durable outbox and visible errors |
| Learning content quality | Three prepared lessons with checked transcripts and sources |
| Concurrent quiz state | Server-controlled deadlines, reconnect snapshots and unique answers |
| Academic policy ambiguity | Version sample rules and obtain supervisor review |
| Missing personal details | Complete student ID, university metadata and supervisor before submission |
Confirm the Project 1 rubric and dates, accepted citation style, sample grade scale and repeat policy, late-submission policy, model provider, test email recipients, deployment environment and budget. Actual expenditure will be recorded after providers are selected; no current price estimate is asserted.

## 15 References and Structural Sources
Highton, M. (2025, May 5). Spotlight on LOUISA Improving assessment and feedback in the Learn VLE. University of Edinburgh. https://blogs.ed.ac.uk/teaching-matters/spotlight-on-louisa-improving-assessment-and-feedback-in-the-learn-vle/
Moodle. (n.d.). Quiz activity. MoodleDocs. Accessed 18 October 2026. https://docs.moodle.org/en/Quiz_activity
IoT Guardian supplied proposal and public PRD and README were structural references only. https://github.com/Legendinho7/IoT-Guardian-Project-1
