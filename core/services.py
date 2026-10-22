from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Sum
from django.utils import timezone

from .models import Assignment, Attendance, Offering, Submission


def visible_offerings(user):
    if user.role == 'admin':
        return Offering.objects.all()
    if user.role == 'lecturer':
        return Offering.objects.filter(lecturers=user)
    return Offering.objects.filter(enrolments__student=user)


def attendance_summary(user, offering=None):
    records = Attendance.objects.filter(student=user, session__cancelled=False, session__starts_at__lte=timezone.now())
    if offering:
        records = records.filter(session__offering=offering)
    counted = records.exclude(status=Attendance.Status.EXCUSED).count()
    attended = records.filter(status__in=[Attendance.Status.PRESENT, Attendance.Status.LATE]).count()
    return {'attended': attended, 'counted': counted, 'percent': round(attended * 100 / counted) if counted else None}


def cgpa(user):
    results = list(user.results.all())
    credits = sum(r.credits for r in results)
    if not credits:
        return None
    points = sum((r.grade_points * r.credits for r in results), Decimal(0))
    return (points / credits).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)


def assignment_rows(user, offerings=None):
    offerings = offerings if offerings is not None else visible_offerings(user)
    assignments = Assignment.objects.filter(offering__in=offerings).select_related('offering')
    if user.role == 'student':
        assignments = assignments.filter(published_at__lte=timezone.now())
    submissions = {}
    if user.role == 'student':
        for item in Submission.objects.filter(student=user, assignment__in=assignments).select_related('feedback').order_by('version'):
            submissions[item.assignment_id] = item
    rows = []
    for assignment in assignments:
        sub = submissions.get(assignment.pk)
        feedback = getattr(sub, 'feedback', None) if sub else None
        if not assignment.published:
            status = 'Draft'
        elif user.role != 'student':
            status = 'Published'
        elif sub:
            status = 'Graded' if feedback and feedback.released_at and feedback.released_at <= timezone.now() else ('Submitted late' if sub.late else 'Submitted')
        else:
            status = 'Overdue' if assignment.due_at < timezone.now() else 'Pending'
        rows.append({'assignment': assignment, 'submission': sub, 'status': status, 'status_class': status.lower().replace(' ', '-')})
    return rows


def balance(user):
    return user.fees.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
