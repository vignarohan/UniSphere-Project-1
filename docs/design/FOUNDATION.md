# Foundation interface design

The student dashboard concept is the visual reference for this milestone. Student, Lecturer and Admin share typography, spacing, controls and accessible navigation.

- Canvas `#f5f8fc`, white content panels, navy navigation `#142b40`, teal actions `#087d83`.
- Desktop sidebar 255 px; main gutters 34 px; body 16 px; dashboard heading 44 px; metric values 40 px.
- Summary metrics use open columns. Assignments and subjects use tables; the next class uses a compact adjacent panel.
- Tables use light separators, restrained status colours and explicit text labels. Buttons have focus indicators and clear names.
- Below 760 px, navigation becomes a drawer, summary metrics use two columns and wide tables scroll within their panels.
- The helper is a keyboard-accessible dialog opened by the bottom-right robot button. It is labelled as a record helper until model-backed AI is implemented.

The concept's dates and displayed lecturer list are illustrative. Actual dates depend on seeding, co-teaching assignments display all assigned lecturers, and the implemented next-class panel includes its date to avoid ambiguity. These are deliberate data and usability adaptations.
