"""Idempotent fictional records; never replace an existing account's password."""
import os
import secrets
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from core.models import Assignment, Attendance, ClassSession, Enrolment, Fee, Offering, ReleasedResult, Resource, User


class Command(BaseCommand):
    help = 'Create fictional demo records and print initial development login details.'

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Demo seeding is only available with DJANGO_DEBUG=1.')
        password = os.getenv('UNISPHERE_DEMO_PASSWORD') or secrets.token_urlsafe(18)
        if len(password) < 12:
            raise CommandError('UNISPHERE_DEMO_PASSWORD must contain at least 12 characters.')
        created_names = []

        def account(username, first, last, role):
            user, created = User.objects.get_or_create(username=username, defaults={
                'first_name': first, 'last_name': last, 'role': role,
                'email': f'{username}@unisphere.example.test',
                'student_number': f'DEMO-{username.upper()}' if role == 'student' else '',
                'is_staff': role == 'admin', 'is_superuser': role == 'admin',
            })
            if created:
                user.set_password(password)
                user.save()
                created_names.append(username)
            elif user.role != role:
                raise CommandError(f'Existing {username} is not a demo {role}; no data was changed.')
            return user

        maya = account('lecturer', 'Dr Maya', 'Chen', 'lecturer')
        adam = account('lecturer02', 'Dr Adam', 'Lee', 'lecturer')
        account('admin', 'Jordan', 'Taylor', 'admin')
        students = [account('student' if i == 1 else f'student{i:02}', 'Alex' if i == 1 else 'Demo', 'Morgan' if i == 1 else f'Student {i:02}', 'student') for i in range(1, 21)]
        offerings = []
        for code, title, desc in [
            ('BIT2103', 'Database Systems', 'Relational models, SQL, joins and practical database design.'),
            ('BIT1102', 'Programming Fundamentals', 'Variables, control flow, functions and problem solving.'),
            ('BIT2204', 'Computer Networks', 'Network layers, addressing, routing and communication.'),
        ]:
            offering, _ = Offering.objects.get_or_create(code=code, defaults={'title': title, 'description': desc})
            offering.lecturers.add(maya)
            offerings.append(offering)
        offerings[2].lecturers.add(adam)
        today = timezone.localdate()
        now = timezone.now()
        def local_at(day, hour=9, minute=0):
            return timezone.make_aware(datetime.combine(day, time(hour, minute)))

        for user in students:
            for offering in offerings:
                Enrolment.objects.get_or_create(student=user, offering=offering)
            for code, subject, credits, grade, points in [
                ('BIT1001', 'Computer Systems', 4, 'B+', '3.67'),
                ('BIT1002', 'Mathematics for Computing', 5, 'B', '3.33'),
            ]:
                ReleasedResult.objects.get_or_create(student=user, code=code, semester='Previous demo semester', defaults={'subject': subject, 'credits': credits, 'grade': grade, 'grade_points': Decimal(points)})
            Fee.objects.get_or_create(student=user, description='Sample semester balance', defaults={'amount': Decimal('250.00'), 'due_on': today + timedelta(days=20)})

        for i in range(25):
            offering = offerings[i % 3]
            session, _ = ClassSession.objects.get_or_create(offering=offering, topic=f'Demo lesson {i+1:02}', defaults={'starts_at': local_at(today-timedelta(days=26-i)), 'venue': 'Room B204'})
            for index, user in enumerate(students):
                attended = 22 if index == 0 else 18 if index == 1 else 19 if index == 2 else 24
                Attendance.objects.get_or_create(student=user, session=session, defaults={'status': 'present' if i < attended else 'absent'})
        for i, offering in enumerate(offerings):
            ClassSession.objects.get_or_create(offering=offering, topic='Next class', defaults={'starts_at': local_at(today+timedelta(days=i+1)), 'venue': 'Room B204' if i == 0 else 'Lab C102'})

        for i, title in enumerate(['Database design', 'Programming exercise']):
            Assignment.objects.get_or_create(offering=offerings[i], title=title, defaults={
                'instructions': 'Complete the exercise described in your subject notes. Explain your approach and submit a PDF or plain text document. This is a fictional demonstration assignment.',
                'due_at': local_at(today+timedelta(days=3+i*3), 23, 0), 'published_at': now,
            })
        Assignment.objects.get_or_create(offering=offerings[0], title='Draft assessment', defaults={'instructions': 'This draft must remain hidden from students.', 'due_at': local_at(today+timedelta(days=10), 23)})
        for offering, content in zip(offerings, [
            'Database Systems — Joins\n\nAn INNER JOIN returns matching rows from both tables. A LEFT JOIN retains every row from the left table, with NULL for missing right-side matches.\n\nPractice: explain why a class enrolment list may need a LEFT JOIN when some students have not submitted work.\n\nOriginal demonstration notes prepared for UniSphere.\n',
            'Programming Fundamentals — Functions\n\nA function groups a task behind a name and defined inputs. Return values make the result available to the caller.\n\nPractice: write a function that accepts credit hours and grade points and returns their product.\n\nOriginal demonstration notes prepared for UniSphere.\n',
            'Computer Networks — Addressing\n\nAn IP address identifies a network interface. A subnet prefix determines which addresses belong to the same network. A default gateway forwards traffic to other networks.\n\nPractice: explain the role of a gateway when a laptop contacts an external website.\n\nOriginal demonstration notes prepared for UniSphere.\n',
        ]):
            if not Resource.objects.filter(offering=offering, title='Introduction notes').exists():
                resource = Resource(offering=offering, title='Introduction notes', uploaded_by=maya, original_name=f'{offering.code}-notes.txt')
                resource.file.save(resource.original_name, ContentFile(content.encode()), save=True)
        self.stdout.write(self.style.SUCCESS('Demo records ready: 20 students, 2 lecturers, 1 admin, 3 offerings.'))
        if created_names:
            self.stdout.write('New development accounts: ' + ', '.join(created_names))
            self.stdout.write('Initial password for newly created accounts: ' + password)
        else:
            self.stdout.write('Existing records and passwords retained. No duplicate demo records created.')
