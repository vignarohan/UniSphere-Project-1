import uuid
from decimal import Decimal
from pathlib import Path

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        LECTURER = 'lecturer', 'Lecturer'
        ADMIN = 'admin', 'Admin'

    role = models.CharField(max_length=12, choices=Role.choices, default=Role.STUDENT)
    student_number = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.get_full_name() or self.username


class Offering(models.Model):
    code = models.CharField(max_length=20)
    title = models.CharField(max_length=120)
    semester = models.CharField(max_length=60, default='October 2026')
    credits = models.PositiveSmallIntegerField(default=3, validators=[MinValueValidator(1)])
    description = models.TextField(blank=True)
    lecturers = models.ManyToManyField(User, related_name='teaching', limit_choices_to={'role': User.Role.LECTURER})

    class Meta:
        ordering = ['pk']
        constraints = [models.UniqueConstraint(fields=['code', 'semester'], name='unique_offering_per_semester')]

    def __str__(self):
        return f'{self.code} {self.title}'


class Enrolment(models.Model):
    student = models.ForeignKey(User, on_delete=models.PROTECT, related_name='enrolments', limit_choices_to={'role': User.Role.STUDENT})
    offering = models.ForeignKey(Offering, on_delete=models.PROTECT, related_name='enrolments')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['student', 'offering'], name='one_enrolment_per_offering')]

    def clean(self):
        if self.student_id and self.student.role != User.Role.STUDENT:
            raise ValidationError({'student': 'Only student accounts can be enrolled.'})

    def __str__(self):
        return f'{self.student} — {self.offering.code}'


class ClassSession(models.Model):
    offering = models.ForeignKey(Offering, on_delete=models.PROTECT, related_name='sessions')
    topic = models.CharField(max_length=160)
    starts_at = models.DateTimeField()
    venue = models.CharField(max_length=80)
    cancelled = models.BooleanField(default=False)

    class Meta:
        ordering = ['starts_at']

    def __str__(self):
        return f'{self.offering.code}: {self.topic}'


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'present', 'Present'
        LATE = 'late', 'Late'
        ABSENT = 'absent', 'Absent'
        EXCUSED = 'excused', 'Excused'

    session = models.ForeignKey(ClassSession, on_delete=models.PROTECT, related_name='attendance')
    student = models.ForeignKey(User, on_delete=models.PROTECT, related_name='attendance_records')
    status = models.CharField(max_length=10, choices=Status.choices)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['session', 'student'], name='one_attendance_per_session')]
        ordering = ['-session__starts_at']

    def clean(self):
        if self.student_id and self.session_id and not Enrolment.objects.filter(student=self.student, offering=self.session.offering).exists():
            raise ValidationError('Attendance requires an enrolled student.')


class Assignment(models.Model):
    offering = models.ForeignKey(Offering, on_delete=models.PROTECT, related_name='assignments')
    title = models.CharField(max_length=160)
    instructions = models.TextField()
    due_at = models.DateTimeField()
    max_score = models.PositiveSmallIntegerField(default=100, validators=[MinValueValidator(1)])
    allow_late = models.BooleanField(default=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['due_at']

    @property
    def published(self):
        return self.published_at is not None and self.published_at <= timezone.now()

    def __str__(self):
        return self.title


def private_upload(instance, filename):
    suffix = Path(filename).suffix.lower()
    return f'{instance._meta.model_name}/{uuid.uuid4().hex}{suffix}'


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.PROTECT, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.PROTECT, related_name='submissions')
    file = models.FileField(upload_to=private_upload)
    original_name = models.CharField(max_length=180)
    version = models.PositiveIntegerField(default=1)
    submitted_at = models.DateTimeField(default=timezone.now, editable=False)
    receipt = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        ordering = ['-submitted_at', '-version']
        constraints = [models.UniqueConstraint(fields=['assignment', 'student', 'version'], name='unique_submission_version')]

    @property
    def late(self):
        return self.submitted_at > self.assignment.due_at


class Feedback(models.Model):
    submission = models.OneToOneField(Submission, on_delete=models.PROTECT, related_name='feedback')
    mark = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0)])
    comment = models.TextField(blank=True)
    released_at = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.submission_id and self.mark is not None and self.mark > self.submission.assignment.max_score:
            raise ValidationError({'mark': 'The mark exceeds this assignment’s maximum score.'})


class Resource(models.Model):
    offering = models.ForeignKey(Offering, on_delete=models.PROTECT, related_name='resources')
    title = models.CharField(max_length=160)
    file = models.FileField(upload_to=private_upload)
    original_name = models.CharField(max_length=180)
    published_at = models.DateTimeField(default=timezone.now)
    uploaded_by = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        ordering = ['-published_at']


class ReleasedResult(models.Model):
    student = models.ForeignKey(User, on_delete=models.PROTECT, related_name='results')
    code = models.CharField(max_length=20)
    subject = models.CharField(max_length=120)
    semester = models.CharField(max_length=60)
    credits = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    grade = models.CharField(max_length=5)
    grade_points = models.DecimalField(max_digits=3, decimal_places=2, validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('4'))])

    class Meta:
        constraints = [models.UniqueConstraint(fields=['student', 'code', 'semester'], name='unique_demo_result')]


class Fee(models.Model):
    student = models.ForeignKey(User, on_delete=models.PROTECT, related_name='fees')
    description = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=9, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    due_on = models.DateField()


class AuditEvent(models.Model):
    actor = models.ForeignKey(User, on_delete=models.PROTECT)
    action = models.CharField(max_length=80)
    record = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
