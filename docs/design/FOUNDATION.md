# Red-and-white interface design

UniSphere's shared portal shell now uses the requested red-and-white palette with a white sidebar, rose selected navigation, rounded summary cards and a softly tinted next-class panel. Student, Lecturer and Admin dashboards and entry/sign-in pages share these tokens.

- Accent `#c92b43`, hover `#a51c33`, white surfaces, canvas `#fcf7f8`, ink `#20212c`, muted labels `#727581`, borders `#eeeaed`.
- Desktop sidebar 255px (225px on medium screens), primary heading 40px, summary values 32px, card radius 14–16px. Below 760px navigation becomes a drawer and summary cards use two columns.
- Tables retain actual records and scroll within their containers. Added Results & CGPA and Fees links use existing authorized student pages.
- PWA theme metadata and offline page use the red accent. The existing app icon assets remain unchanged.
- The floating helper remains explicitly labelled as a record lookup helper until model-backed tutoring is implemented.

## Concept adaptations

The generated red-and-white concept supplies the palette, white sidebar, summary cards, table panels and next-class treatment. Actual records, dates, row count, lecturer names and course codes are retained. No class end time is invented. Existing assignment and subject table columns and actions are preserved. The sidebar follows the implemented routes and existing icon family. The concept's generated illustrative academic content is not hardcoded.

## Verification

- All 33 existing Django tests pass on SQLite after the redesign.
- Compiled Tailwind stylesheet rebuilt successfully; git whitespace check passes.
- Browser visual verification is incomplete: the cloud browser cannot access the local application, and local Chromium cannot launch because Unix sockets are disallowed in the execution sandbox. Escalated execution was rejected by the environment approval policy.
- Do not claim pixel-perfect fidelity, completed mobile/browser interaction QA, or measured usability improvement for this revision. Desktop/mobile visual review remains required.
