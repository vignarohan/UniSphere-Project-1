import io
import os
import shutil
import tempfile
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.core.cache import cache
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from core.models import Assignment, Attendance, ClassSession, Enrolment, Feedback, Offering, ReleasedResult, Resource, Submission, User
from core.services import assignment_rows, attendance_summary, cgpa

TEST_PASSWORD = 'Only-for-isolated-tests-42'


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class PortalTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.media = tempfile.mkdtemp(prefix='unisphere-test-media-')
        cls.media_override = override_settings(MEDIA_ROOT=cls.media)
        cls.media_override.enable()

    @classmethod
    def tearDownClass(cls):
        cls.media_override.disable()
        shutil.rmtree(cls.media, ignore_errors=True)
        super().tearDownClass()

    @classmethod
    def setUpTestData(cls):
        def user(name, role):
            return User.objects.create_user(username=name, password=TEST_PASSWORD, role=role, first_name=name.title(), is_staff=role == 'admin', is_superuser=role == 'admin')
        cls.student = user('alex', 'student')
        cls.other = user('taylor', 'student')
        cls.lecturer = user('maya', 'lecturer')
        cls.unrelated = user('adam', 'lecturer')
        cls.admin = user('jordan', 'admin')
        cls.offering = Offering.objects.create(code='DB101', title='Database Systems')
        cls.offering.lecturers.add(cls.lecturer)
        cls.outside = Offering.objects.create(code='NET101', title='Unrelated class')
        cls.outside.lecturers.add(cls.unrelated)
        for student in [cls.student, cls.other]:
            Enrolment.objects.create(student=student, offering=cls.offering)
        Enrolment.objects.create(student=cls.other, offering=cls.outside)
        cls.assignment = Assignment.objects.create(offering=cls.offering, title='Database design', instructions='Explain a schema.', due_at=timezone.now()+timedelta(days=3), published_at=timezone.now())
        cls.draft = Assignment.objects.create(offering=cls.offering, title='Confidential draft', instructions='Hidden', due_at=timezone.now()+timedelta(days=4))
        cls.foreign = Assignment.objects.create(offering=cls.outside, title='Outside work', instructions='Hidden from Alex', due_at=timezone.now()+timedelta(days=4), published_at=timezone.now())

    def setUp(self):
        cache.clear()

    def as_user(self, user):
        self.client.force_login(user)

    def upload(self, data=b'Original test work', name='answer.txt'):
        return SimpleUploadedFile(name, data)

    def submit(self):
        self.as_user(self.student)
        return self.client.post(reverse('assignment-detail', args=[self.assignment.pk]), {'file': self.upload()})

    def resource(self, offering=None, published_at=None):
        return Resource.objects.create(offering=offering or self.offering, title='Notes', file=ContentFile(b'Original notes', name='notes.txt'), original_name='notes.txt', uploaded_by=self.lecturer, published_at=published_at or timezone.now())

    def test_entry_has_all_three_roles(self):
        response = self.client.get('/')
        for role in ['student', 'lecturer', 'admin']:
            self.assertContains(response, f'/login/{role}/')

    def test_correct_role_login_opens_dashboard(self):
        response = self.client.post('/login/student/', {'username': 'alex', 'password': TEST_PASSWORD})
        self.assertRedirects(response, '/dashboard/')

    def test_role_selection_cannot_escalate_account(self):
        response = self.client.post('/login/admin/', {'username': 'alex', 'password': TEST_PASSWORD})
        self.assertContains(response, 'account details or selected portal are incorrect')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_failed_logins_are_throttled(self):
        for _ in range(8):
            self.client.post('/login/student/', {'username': 'alex', 'password': 'wrong'})
        self.assertEqual(self.client.post('/login/student/', {'username': 'alex', 'password': TEST_PASSWORD}).status_code, 429)

    def test_private_routes_require_login(self):
        for url in ['/dashboard/', '/assignments/', '/attendance/', '/helper/records/?topic=pending']:
            self.assertEqual(self.client.get(url).status_code, 302)

    def test_logout_is_post_only_and_invalidates_session(self):
        self.as_user(self.student)
        self.assertEqual(self.client.get('/logout/').status_code, 405)
        self.client.post('/logout/')
        self.assertEqual(self.client.get('/dashboard/').status_code, 302)

    def test_csrf_is_required_for_submission(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.student)
        response = client.post(reverse('assignment-detail', args=[self.assignment.pk]), {'file': self.upload()})
        self.assertEqual(response.status_code, 403)

    def test_deactivation_ends_existing_session_access(self):
        self.as_user(self.student)
        self.student.is_active = False
        self.student.save()
        self.assertEqual(self.client.get('/dashboard/').status_code, 302)

    def test_drafts_and_unenrolled_assignments_are_hidden(self):
        self.as_user(self.student)
        response = self.client.get('/assignments/')
        self.assertContains(response, 'Database design')
        self.assertNotContains(response, 'Confidential draft')
        for item in [self.draft, self.foreign]:
            self.assertEqual(self.client.get(reverse('assignment-detail', args=[item.pk])).status_code, 404)

    def test_private_resources_require_enrolment_and_publication(self):
        own = self.resource()
        foreign = self.resource(self.outside)
        draft = self.resource(published_at=timezone.now()+timedelta(days=2))
        self.as_user(self.student)
        self.assertEqual(self.client.get(reverse('resource-download', args=[own.pk])).status_code, 200)
        for item in [foreign, draft]:
            self.assertEqual(self.client.get(reverse('resource-download', args=[item.pk])).status_code, 404)
        self.client.logout()
        self.assertEqual(self.client.get(reverse('resource-download', args=[own.pk])).status_code, 302)

    def test_student_cannot_publish_or_create_assignments(self):
        self.as_user(self.student)
        self.assertEqual(self.client.get('/assignments/new/').status_code, 403)
        self.assertEqual(self.client.post(reverse('assignment-publish', args=[self.draft.pk])).status_code, 403)

    def test_lecturer_cannot_create_for_unassigned_offering(self):
        self.as_user(self.lecturer)
        response = self.client.post('/assignments/new/', {'offering': self.outside.pk, 'title': 'Invalid class', 'instructions': 'Test', 'due_at': '2030-10-25T12:00', 'max_score': 100, 'publish': 'on'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Assignment.objects.filter(title='Invalid class').exists())

    def test_lecturer_can_publish_to_assigned_class(self):
        self.as_user(self.lecturer)
        self.client.post(reverse('assignment-publish', args=[self.draft.pk]))
        self.as_user(self.student)
        self.assertContains(self.client.get('/assignments/'), 'Confidential draft')

    def test_lecturer_cannot_read_student_finance_or_results(self):
        self.as_user(self.lecturer)
        self.assertEqual(self.client.get('/fees/').status_code, 403)
        self.assertEqual(self.client.get('/results/').status_code, 403)

    def test_admin_site_requires_admin_role_even_for_staff(self):
        self.student.is_staff = True
        self.student.is_superuser = True
        self.student.save()
        self.as_user(self.student)
        self.assertEqual(self.client.get('/manage/').status_code, 302)
        self.as_user(self.admin)
        self.assertEqual(self.client.get('/manage/').status_code, 200)

    def test_submission_creates_receipt_and_private_file(self):
        self.assertEqual(self.submit().status_code, 302)
        sub = Submission.objects.get()
        self.assertEqual(sub.student, self.student)
        self.assertEqual(sub.version, 1)
        response = self.client.get(reverse('assignment-detail', args=[self.assignment.pk]))
        self.assertContains(response, str(sub.receipt))
        download = self.client.get(reverse('submission-download', args=[sub.pk]))
        self.assertEqual(b''.join(download.streaming_content), b'Original test work')
        self.assertIn('attachment', download['Content-Disposition'])
        self.assertIn('no-store', download['Cache-Control'])

    def test_repeated_uploads_create_distinct_versions(self):
        self.submit()
        self.client.post(reverse('assignment-detail', args=[self.assignment.pk]), {'file': self.upload(b'Revised work')})
        subs = list(Submission.objects.order_by('version'))
        self.assertEqual([s.version for s in subs], [1, 2])
        self.assertNotEqual(subs[0].receipt, subs[1].receipt)

    def test_student_cannot_download_another_students_submission(self):
        self.submit()
        sub = Submission.objects.get()
        self.as_user(self.other)
        self.assertEqual(self.client.get(reverse('submission-download', args=[sub.pk])).status_code, 404)
        self.assertNotContains(self.client.get(reverse('assignment-detail', args=[self.assignment.pk])), str(sub.receipt))

    def test_unrelated_lecturer_cannot_read_or_mark_submission(self):
        self.submit()
        sub = Submission.objects.get()
        self.as_user(self.unrelated)
        for route in ['submission-download', 'feedback-edit']:
            self.assertEqual(self.client.get(reverse(route, args=[sub.pk])).status_code, 404)

    def test_unsupported_and_disguised_files_create_no_receipts(self):
        self.as_user(self.student)
        for filename, data in [('malware.exe', b'bad'), ('not-a-pdf.pdf', b'bad'), ('binary.txt', b'\x00binary')]:
            response = self.client.post(reverse('assignment-detail', args=[self.assignment.pk]), {'file': self.upload(data, filename)})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Submission.objects.count(), 0)

    def test_oversized_upload_creates_no_submission(self):
        self.as_user(self.student)
        self.client.post(reverse('assignment-detail', args=[self.assignment.pk]), {'file': self.upload(b'a'*(5*1024*1024+1))})
        self.assertFalse(Submission.objects.exists())

    def test_closed_assignment_refuses_upload(self):
        self.assignment.due_at = timezone.now()-timedelta(hours=1)
        self.assignment.allow_late = False
        self.assignment.save()
        self.assertContains(self.submit(), 'does not accept late submissions')
        self.assertFalse(Submission.objects.exists())

    def test_accepted_late_submission_is_labelled(self):
        self.assignment.due_at = timezone.now()-timedelta(hours=1)
        self.assignment.save()
        self.submit()
        self.assertTrue(Submission.objects.get().late)
        self.assertEqual(assignment_rows(self.student)[0]['status'], 'Submitted late')

    def test_draft_feedback_is_hidden_until_released(self):
        self.submit()
        sub = Submission.objects.get()
        self.as_user(self.lecturer)
        url = reverse('feedback-edit', args=[sub.pk])
        self.client.post(url, {'mark': '85', 'comment': 'Specific private feedback'})
        self.as_user(self.student)
        self.assertNotContains(self.client.get(reverse('assignment-detail', args=[self.assignment.pk])), 'Specific private feedback')
        self.as_user(self.lecturer)
        self.client.post(url, {'mark': '85', 'comment': 'Specific private feedback', 'release': 'on'})
        self.as_user(self.student)
        self.assertContains(self.client.get(reverse('assignment-detail', args=[self.assignment.pk])), 'Specific private feedback')
        self.assertEqual(assignment_rows(self.student)[0]['status'], 'Graded')

    def test_mark_cannot_exceed_maximum(self):
        self.submit()
        self.as_user(self.lecturer)
        response = self.client.post(reverse('feedback-edit', args=[Submission.objects.get().pk]), {'mark': '101', 'comment': 'Invalid', 'release': 'on'})
        self.assertContains(response, 'exceeds this assignment')
        self.assertFalse(Feedback.objects.exists())

    def test_attendance_counts_late_and_excludes_excused_cancelled_future(self):
        for i, (status, cancelled, future) in enumerate([('present', False, False), ('late', False, False), ('absent', False, False), ('excused', False, False), ('present', True, False), ('present', False, True)]):
            session = ClassSession.objects.create(offering=self.offering, topic=f'Lesson {i}', starts_at=timezone.now()+timedelta(days=1 if future else -1), venue='B204', cancelled=cancelled)
            Attendance.objects.create(student=self.student, session=session, status=status)
        self.assertEqual(attendance_summary(self.student), {'attended': 2, 'counted': 3, 'percent': 67})

    def test_zero_attendance_is_unavailable_not_zero(self):
        self.assertIsNone(attendance_summary(self.student)['percent'])

    def test_cgpa_is_credit_weighted(self):
        for code, credits, points in [('A', 4, '3.67'), ('B', 5, '3.33')]:
            ReleasedResult.objects.create(student=self.student, code=code, subject=code, semester='Previous', credits=credits, grade='B', grade_points=Decimal(points))
        self.assertEqual(cgpa(self.student), Decimal('3.48'))
        self.assertIsNone(cgpa(self.other))

    def test_helper_uses_session_identity_and_rejects_wrong_role_lookup(self):
        self.as_user(self.student)
        response = self.client.get('/helper/records/', {'topic': 'pending', 'student_id': self.other.pk})
        self.assertEqual([i['title'] for i in response.json()['items']], ['Database design'])
        self.assertEqual(self.client.get('/helper/records/?topic=accounts').status_code, 400)

    def test_private_pages_are_not_cacheable(self):
        self.as_user(self.student)
        for url in ['/dashboard/', '/assignments/', '/helper/records/?topic=pending']:
            self.assertIn('no-store', self.client.get(url)['Cache-Control'])

    def test_offline_document_contains_no_account_details(self):
        self.as_user(self.student)
        response = self.client.get('/offline/')
        self.assertContains(response, 'You are offline')
        self.assertNotContains(response, 'Alex')
        self.assertNotContains(response, 'Sign out')
        self.assertNotContains(response, 'csrfmiddlewaretoken')

    def test_manifest_and_worker_are_served_from_root(self):
        manifest = self.client.get('/manifest.webmanifest').json()
        self.assertEqual(manifest['display'], 'standalone')
        self.assertEqual(manifest['start_url'], '/')
        worker = self.client.get('/service-worker.js')
        self.assertEqual(worker.status_code, 200)
        self.assertEqual(worker['Service-Worker-Allowed'], '/')
        self.assertNotIn('__CACHE_VERSION__', worker.content.decode())


@override_settings(DEBUG=True, PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class DemoSeedTests(TestCase):
    def test_seed_is_repeatable_and_preserves_passwords(self):
        with tempfile.TemporaryDirectory() as media, override_settings(MEDIA_ROOT=media), patch.dict(os.environ, {'UNISPHERE_DEMO_PASSWORD': TEST_PASSWORD}):
            call_command('seed_demo', stdout=io.StringIO())
            password = User.objects.get(username='student').password
            call_command('seed_demo', stdout=io.StringIO())
            self.assertEqual(User.objects.count(), 23)
            self.assertEqual(Offering.objects.count(), 3)
            self.assertEqual(Assignment.objects.count(), 3)
            self.assertEqual(Resource.objects.count(), 3)
            self.assertEqual(User.objects.get(username='student').password, password)
            alex = User.objects.get(username='student')
            self.assertEqual(attendance_summary(alex)['percent'], 88)
            self.assertEqual(cgpa(alex), Decimal('3.48'))
