# UniSphere Project Proposal
## An Integrated University Academic Portal with an AI Assistant
Prepared by Shri Vignarohan A/L S. Ramasamy
Programme Bachelor of IT Honours Cyber Security
Student ID To be completed
University and faculty To be confirmed
Supervisor To be confirmed
Course Project 1
Date 18 October 2026
Version 1.0

## 1 Background of the Idea
University students need to move between learning resources, assessment instructions, attendance, schedules, results and administrative services. When these interfaces are difficult to navigate, finding the next action becomes an additional task. My starting observation is that my current student portal feels disorganised. This observation motivates the project; it does not establish that every student has the same experience.
The University of Edinburgh reported that student interviews identified difficulty finding assessment information organised differently across courses (Highton, 2025). This provides external context for investigating information organisation, rather than proof of a problem at my university. A short local survey and task-based interviews will establish which tasks students and lecturers find difficult.
UniSphere proposes a single academic workspace with role-specific navigation and an embedded assistant. Its focus is the connection between records and learning: a missed class should lead to its actual lesson resources, and a question about pending work should retrieve the correct assignments.

## 2 The Problem
Students may struggle to locate deadlines, distinguish pending from overdue work, recover missed lessons and understand their overall academic position. Lecturers may need to inspect multiple records to identify students with outstanding work or low attendance. Administrative enquiries may lack a visible status and response history when handled through disconnected messages.
The research question is whether an integrated portal with contextual assistance can improve completion of selected academic tasks compared with a baseline interface. This project will evaluate usability and record retrieval; it will not claim improved grades or reduced dropout without evidence.

## 3 Proposed Solution and Scope
UniSphere is a responsive web application with Student, Lecturer and Admin portals. A floating robot button opens a chat panel on the current page. Manual navigation remains available for every core task. The demonstration uses fictional users, sample records and authorised learning content. It does not connect to a university production system.
### Target users
Students manage their own learning and records. Lecturers manage assigned subject offerings and enrolled students. Administrators maintain users, enrolments, schedules, academic policies, finance records and support workflows.
### Objectives
- Build three authenticated role-specific portals backed by shared academic records.
- Demonstrate assignment publication, submission, marking and feedback as one connected workflow.
- Connect attendance sessions to lesson materials and catch-up learning without changing original attendance.
- Provide an assistant that retrieves authorised records and explains learning materials with source references.
- Provide independent Quiz Me practice and lecturer-hosted live class quizzes.
- Provide category-based tickets with in-portal notifications and email notification delivery tracking.
- Evaluate task completion, calculation correctness, permissions, AI grounding and quiz synchronisation.
### Student portal
Students view a dashboard, enrolled subjects, programme structure, timetable, examinations, lecturer contacts, assignments, attendance, results, CGPA, learning progress and finance. They download notes and slides, watch recordings, submit assignments, review feedback, practise with Quiz Me and join live quizzes.
### Lecturer portal
Lecturers upload and publish learning materials, create assignments, review submissions, release marks, record attendance and view teaching schedules. A filtered class overview highlights low attendance, outstanding work and low released assessment scores using visible rules. These flags indicate a need for review rather than a diagnosis of the student.
### Admin portal
A smaller Admin option appears below Student and Lecturer on the entry screen. Administrators manage accounts, academic structures, enrolments, schedules, results publication, simulated fee records, ticket categories and system activity. Changes to sensitive records require a reason and an audit entry.
### Quizzes and tickets
Quiz Me provides personal practice with explanations and source links. Quiz Your Students lets a lecturer review questions, launch a session, notify the selected class, admit authenticated participants and run timed multiple-choice questions. Scores and an optional alias-based leaderboard are saved separately from official grades.
All roles can submit tickets. The sender chooses recipient type, recipient, category, subject and description, with optional related record and attachment. Categories include marks, attendance, learning materials, payments, programme structure, enrolment, technical problems and Other. Recipients receive portal and email notifications; replies and status changes remain in the portal.
### Project 1 delivery
The proposed seven-week Project 1 milestone covers requirements, design and a functional vertical slice: three role logins, seeded enrolments, subject resources, assignment publication and submission, attendance display, and one working AI pending-assignment query. The full feature set remains documented. The course schedule and prototype proportion must be confirmed against the actual rubric.
### Project 2 delivery
Complete results and finance views, missed-lesson tutoring, independent practice, live quizzes, tickets with email, monitoring filters and full evaluation. These features are planned commitments for the completed demonstration, not claims of current implementation.
### Outside the demonstration
Real fee collection, integration with a production university portal, native mobile apps, live video conferencing, biometric attendance, automated final grading and full university enterprise operations are outside scope.

## 4 System Design
Browser interfaces communicate with an application backend that enforces roles, enrolments and ownership. The backend stores structured records in a relational database and files in private storage. A background notification worker sends email. A live session channel distributes quiz state. The AI receives only authorised records and relevant resource excerpts.
A practical baseline is Django with server-rendered responsive pages, PostgreSQL, private file storage and a WebSocket-capable quiz component. This is a proposed architecture rather than a claim that packages have been installed or verified. Exact dependency versions will be pinned during implementation.
AI teaching uses searchable text extracted from notes and prepared lecture transcripts. A short manually prepared transcript is sufficient for the demo. The assistant cannot infer a missing lesson or a nonexistent recording. External model and email services introduce internet and configuration dependencies; failures must be visible.
[IMAGE architecture.png]
Figure 1 Proposed UniSphere architecture
### Demonstration dataset
Use 20 fictional students, two lecturers, one administrator, three subject offerings in one current semester and a small prior-results history for CGPA. Seed present and absent sessions, submitted and overdue assignments, published and draft resources, fee balances, quiz questions and tickets. Include a student outside one lecturer's class to test permission boundaries.
### Data relationships
A subject is a catalogue entry; a subject offering is the taught instance in a semester. Enrolments and lecturer assignments reference offerings. Class sessions connect attendance to lessons. Assessments link to submissions and released scores. Programme rules and published results drive credit-weighted GPA and CGPA. Tickets, notifications and quiz sessions each maintain their own lifecycle.

## 5 Development Timeline
The schedule below is a proposed sequence, not a confirmed university deadline.
| Week | Main deliverable | Evidence of completion |
| --- | --- | --- |
| 1 | Problem and scope | Local task findings and supervisor review |
| 2 | Requirements | PRD and prioritised acceptance criteria |
| 3 | Design | Architecture, data model and screen map |
| 4 | Foundations | Role login, database migrations and seed records |
| 5 | Academic workflow | Publish, submit and review assignment |
| 6 | AI vertical slice | Authorised pending-assignment answer with links |
| 7 | Evaluation and proposal handoff | Test evidence, report and scripted prototype demo |
[IMAGE timeline.png]
Figure 2 Proposed Project 1 sequence
Project 2 proceeds through academic completion, AI catch-up, quizzes, tickets and email, then integrated evaluation. Its duration will be set after the course timetable is confirmed.

## 6 Software Engineer Questions and Answers
### Q1 Who uses the system
Students, lecturers and administrators. Each sees a role-specific workspace and only authorised records.
### Q2 What is distinctive about this idea
Academic portals and learning-management systems already exist. UniSphere's contribution is the evaluated combination of clear navigation, personal-record assistance, lesson recovery, practice, class quizzes and support tickets. It does not claim to invent these components.
### Q3 What does the AI actually do
It retrieves personal academic records through restricted backend functions and explains retrieved course material. It links to supporting records or resource pages and states when information is unavailable.
### Q4 Does catching up restore attendance
No. Attendance remains a historical class record. Catch-up completion records a separate learning activity.
### Q5 Are practice scores official marks
No. Practice and live quiz results are formative by default. Any future graded use needs an explicit assessment mapping and lecturer publication workflow.
### Q6 How does lecturer monitoring work
Deterministic filters use configured attendance thresholds, outstanding submission counts and released assessment results. Every flag shows its reason. Insufficient assessment evidence is displayed rather than converted into a low score.
### Q7 How do live quizzes stay consistent
The server controls the question state, deadline and scoring. A participant may submit one accepted answer per question. Reconnection reloads the current state instead of restarting the timer.
### Q8 How are tickets routed
Recipient type determines eligible recipients and categories. Replies, reassignments and status changes are recorded. Email directs the receiver to the authorised portal thread.
### Q9 What happens if AI or email fails
Manual academic features continue working. AI requests show a clear failure state. Email remains pending or failed with bounded retries; successful ticket creation is independent of email delivery.
### Q10 How is security part of the project
Server-enforced permissions, protected downloads, safe file handling, audit trails and AI data-isolation tests provide a meaningful security component. Assessment suitability for the Cyber Security programme still needs supervisor confirmation.
### Q11 How will success be measured
Use functional and negative permission tests, known-value calculation fixtures, multi-client quiz tests, AI retrieval questions and task-based user testing. Targets are specified in the PRD; no test results are claimed yet.
### Q12 What remains to be confirmed
Student ID, supervisor, faculty and institution naming, required report template, marking rubric, actual schedule, grading policy, model provider and email configuration.

## 7 Risks and Mitigations
| Risk | Effect | Response |
| --- | --- | --- |
| Scope exceeds solo capacity | Incomplete connected workflows | Stage delivery and freeze optional features |
| AI gives unsupported answers | Misleading academic guidance | Restricted retrieval, citations and unsupported-answer tests |
| Missing teaching content | Catch-up cannot work | Prepare a small complete lesson dataset early |
| Quiz desynchronisation | Unfair or inconsistent results | Server clock, idempotent answers and reconnect tests |
| Email provider unavailable | Recipient misses email | Persistent outbox, portal notifications and visible delivery state |
| Invalid access to records | Privacy breach within demo | Ownership and enrolment checks on every operation |
| Unconfirmed marking rules | Incorrect GPA or attendance | Publish the sample policy and test boundary cases |

## 8 References
Highton, M. (2025, May 5). Spotlight on LOUISA Improving assessment and feedback in the Learn VLE. University of Edinburgh Teaching Matters. https://blogs.ed.ac.uk/teaching-matters/spotlight-on-louisa-improving-assessment-and-feedback-in-the-learn-vle/
Moodle. (n.d.). Quiz activity. MoodleDocs. Accessed 18 October 2026. https://docs.moodle.org/en/Quiz_activity
The supplied IoT Guardian proposal and its PRD and README were reviewed as structural examples. UniSphere's scope and requirements are independently written from the project discussion. Reference repository https://github.com/Legendinho7/IoT-Guardian-Project-1
