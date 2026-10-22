import hashlib
import logging
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db import DatabaseError, transaction
from django.db.models import Max
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .forms import AssignmentForm, FeedbackForm, ResourceForm, RoleLoginForm, SubmissionForm
from .models import Assignment, Attendance, AuditEvent, ClassSession, Feedback, Offering, Resource, Submission, User
from .services import assignment_rows, attendance_summary, balance, cgpa, visible_offerings

logger = logging.getLogger(__name__)


def require_role(user, *roles):
    if user.role not in roles:
        raise PermissionDenied


def accessible_assignment(user, pk):
    query = Assignment.objects.filter(offering__in=visible_offerings(user)).select_related('offering')
    if user.role == 'student':
        query = query.filter(published_at__lte=timezone.now())
    return get_object_or_404(query, pk=pk)


@require_GET
def entry(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/entry.html', {'title': 'Welcome to UniSphere'})


def sign_in(request, role):
    if role not in User.Role.values:
        raise Http404
    if request.user.is_authenticated:
        return redirect('dashboard')
    username = request.POST.get('username', '').strip().lower()
    # Local development throttle. A shared cache is required before multi-worker hosting.
    key = 'login:' + hashlib.sha256((username + '|' + request.META.get('REMOTE_ADDR', '')).encode()).hexdigest()
    form = RoleLoginForm(request=request, data=request.POST or None, role=role)
    status = 200
    if request.method == 'POST':
        if cache.get(key, 0) >= 8:
            form.add_error(None, 'Too many attempts. Please wait ten minutes before trying again.')
            status = 429
        elif form.is_valid():
            cache.delete(key)
            login(request, form.get_user())
            return redirect('dashboard')
        else:
            cache.set(key, cache.get(key, 0) + 1, 600)
    return render(request, 'core/login.html', {'form': form, 'role': role, 'role_name': User.Role(role).label, 'title': f'{User.Role(role).label} sign in'}, status=status)


@require_POST
@login_required
def sign_out(request):
    logout(request)
    return redirect('entry')


@login_required
@require_GET
def dashboard(request):
    user = request.user
    offerings = visible_offerings(user).prefetch_related('lecturers')
    context = {'title': 'Dashboard', 'active': 'dashboard', 'offerings': offerings}
    if user.role == 'student':
        rows = assignment_rows(user, offerings)
        context.update(attendance=attendance_summary(user), cgpa=cgpa(user), balance=balance(user),
                       pending=sum(r['status'] in {'Pending', 'Overdue'} for r in rows), rows=rows[:5],
                       next_class=ClassSession.objects.filter(offering__in=offerings, starts_at__gte=timezone.now(), cancelled=False).select_related('offering').first())
    elif user.role == 'lecturer':
        submissions = Submission.objects.filter(assignment__offering__in=offerings).select_related('student', 'assignment__offering', 'feedback')
        context['queue'] = submissions.filter(feedback__released_at__isnull=True)
        context['submission_count'] = submissions.count()
        context['assignment_count'] = Assignment.objects.filter(offering__in=offerings, published_at__lte=timezone.now()).count()
        attention = []
        students = User.objects.filter(role='student', enrolments__offering__in=offerings).distinct()
        for student in students:
            records = Attendance.objects.filter(student=student, session__offering__in=offerings, session__cancelled=False, session__starts_at__lte=timezone.now()).exclude(status='excused')
            counted = records.count()
            attended = records.filter(status__in=['present', 'late']).count()
            percent = round(attended * 100 / counted) if counted else None
            overdue = sum(r['status'] == 'Overdue' for r in assignment_rows(student, offerings))
            if (percent is not None and percent < 80) or overdue:
                attention.append({'student': student, 'attended': attended, 'counted': counted, 'percent': percent, 'overdue': overdue})
        context['attention'] = attention
        context['attendance_flag_count'] = sum(row['percent'] is not None and row['percent'] < 80 for row in attention)
    else:
        context.update(students=User.objects.filter(role='student', is_active=True).count(),
                       lecturers=User.objects.filter(role='lecturer', is_active=True).count(),
                       activity=AuditEvent.objects.select_related('actor')[:8],
                       account_count=User.objects.filter(is_active=True).count())
    return render(request, 'core/dashboard.html', context)


@login_required
@require_GET
def subjects(request):
    return render(request, 'core/subjects.html', {'title': 'My subjects' if request.user.role == 'student' else 'My classes', 'active': 'subjects', 'offerings': visible_offerings(request.user).prefetch_related('lecturers')})


@login_required
@require_GET
def subject_detail(request, pk):
    offering = get_object_or_404(visible_offerings(request.user).prefetch_related('lecturers'), pk=pk)
    resources = offering.resources.all()
    if request.user.role == 'student':
        resources = resources.filter(published_at__lte=timezone.now())
    return render(request, 'core/subject_detail.html', {'title': offering.title, 'active': 'subjects', 'offering': offering, 'resources': resources, 'rows': assignment_rows(request.user, Offering.objects.filter(pk=offering.pk))})


@login_required
def resource_new(request, pk):
    require_role(request.user, 'lecturer')
    offering = get_object_or_404(request.user.teaching.all(), pk=pk)
    form = ResourceForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        resource = form.save(commit=False)
        resource.offering = offering
        resource.uploaded_by = request.user
        resource.original_name = Path(form.cleaned_data['file'].name).name[:180]
        resource.save()
        AuditEvent.objects.create(actor=request.user, action='Published material', record=f'Resource {resource.pk}')
        messages.success(request, 'Material published to enrolled students.')
        return redirect('subject-detail', pk=pk)
    return render(request, 'core/form.html', {'title': 'Publish material', 'active': 'subjects', 'form': form, 'button': 'Publish material', 'back_url': reverse('subject-detail', args=[pk])})


@login_required
@require_GET
def assignments(request):
    return render(request, 'core/assignments.html', {'title': 'Assignments', 'active': 'assignments', 'rows': assignment_rows(request.user)})


@login_required
def assignment_new(request):
    require_role(request.user, 'lecturer')
    form = AssignmentForm(request.POST or None, user=request.user)
    if request.method == 'POST' and form.is_valid():
        assignment = form.save(commit=False)
        if form.cleaned_data['publish']:
            assignment.published_at = timezone.now()
        assignment.save()
        AuditEvent.objects.create(actor=request.user, action='Created assignment', record=f'Assignment {assignment.pk}')
        messages.success(request, 'Assignment published.' if assignment.published else 'Assignment saved as a draft.')
        return redirect('assignment-detail', pk=assignment.pk)
    return render(request, 'core/form.html', {'title': 'Create assignment', 'active': 'assignments', 'form': form, 'button': 'Save assignment', 'back_url': reverse('assignments')})


@login_required
def assignment_detail(request, pk):
    assignment = accessible_assignment(request.user, pk)
    form = SubmissionForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        require_role(request.user, 'student')
        if form.is_valid():
            submission = None
            try:
                with transaction.atomic():
                    assignment = Assignment.objects.select_for_update().get(pk=assignment.pk)
                    if not assignment.published:
                        raise PermissionDenied
                    if not assignment.allow_late and timezone.now() > assignment.due_at:
                        form.add_error(None, 'This assignment is closed and does not accept late submissions.')
                    else:
                        latest = assignment.submissions.filter(student=request.user).aggregate(v=Max('version'))['v'] or 0
                        submission = Submission(assignment=assignment, student=request.user, version=latest + 1,
                                                original_name=Path(form.cleaned_data['file'].name).name[:180])
                        submission.file.save(form.cleaned_data['file'].name, form.cleaned_data['file'], save=False)
                        submission.submitted_at = timezone.now()
                        if not assignment.allow_late and submission.submitted_at > assignment.due_at:
                            submission.file.delete(save=False)
                            form.add_error(None, 'The deadline passed before the upload completed. No submission was accepted.')
                        else:
                            submission.save()
                            AuditEvent.objects.create(actor=request.user, action='Submitted assignment', record=f'Submission {submission.pk}')
                            messages.success(request, 'Submission received. Your receipt is saved below.')
                            return redirect('assignment-detail', pk=pk)
            except (OSError, DatabaseError):
                if submission and submission.file:
                    submission.file.delete(save=False)
                logger.exception('Submission persistence failed')
                form.add_error(None, 'Your submission could not be saved. Please try again; no success receipt was issued.')
    submissions = assignment.submissions.select_related('student', 'feedback')
    if request.user.role == 'student':
        submissions = submissions.filter(student=request.user)
    return render(request, 'core/assignment_detail.html', {'title': assignment.title, 'active': 'assignments', 'assignment': assignment, 'form': form, 'submissions': submissions, 'now': timezone.now()})


@login_required
@require_POST
def assignment_publish(request, pk):
    require_role(request.user, 'lecturer')
    assignment = get_object_or_404(Assignment, pk=pk, offering__lecturers=request.user)
    if not assignment.published:
        assignment.published_at = timezone.now()
        assignment.save(update_fields=['published_at'])
        AuditEvent.objects.create(actor=request.user, action='Published assignment', record=f'Assignment {assignment.pk}')
    messages.success(request, 'Assignment is visible to enrolled students.')
    return redirect('assignment-detail', pk=pk)


@login_required
def feedback_edit(request, pk):
    require_role(request.user, 'lecturer')
    submission = get_object_or_404(Submission.objects.select_related('assignment__offering', 'student'), pk=pk, assignment__offering__lecturers=request.user)
    feedback = getattr(submission, 'feedback', None) or Feedback(submission=submission)
    form = FeedbackForm(request.POST or None, instance=feedback, initial={'release': bool(feedback.released_at)})
    if request.method == 'POST' and form.is_valid():
        feedback = form.save(commit=False)
        feedback.released_at = timezone.now() if form.cleaned_data['release'] else None
        feedback.save()
        AuditEvent.objects.create(actor=request.user, action='Released feedback' if feedback.released_at else 'Saved draft feedback', record=f'Submission {pk}')
        messages.success(request, 'Feedback released.' if feedback.released_at else 'Draft feedback saved; it is hidden from the student.')
        return redirect('assignment-detail', pk=submission.assignment_id)
    return render(request, 'core/form.html', {'title': f'Feedback for {submission.student}', 'active': 'assignments', 'form': form, 'button': 'Save feedback', 'back_url': reverse('assignment-detail', args=[submission.assignment_id]), 'description': f'{submission.assignment.title} · Maximum {submission.assignment.max_score} marks'})


def protected_file(field, filename):
    try:
        response = FileResponse(field.open('rb'), as_attachment=True, filename=filename)
    except (OSError, ValueError):
        raise Http404('This file is unavailable.')
    response['Cache-Control'] = 'private, no-store'
    return response


@login_required
@require_GET
def submission_download(request, pk):
    submissions = Submission.objects.filter(assignment__offering__in=visible_offerings(request.user))
    if request.user.role == 'student':
        submissions = submissions.filter(student=request.user)
    item = get_object_or_404(submissions, pk=pk)
    return protected_file(item.file, item.original_name)


@login_required
@require_GET
def resource_download(request, pk):
    resources = Resource.objects.filter(offering__in=visible_offerings(request.user))
    if request.user.role == 'student':
        resources = resources.filter(published_at__lte=timezone.now())
    item = get_object_or_404(resources, pk=pk)
    return protected_file(item.file, item.original_name)


@login_required
@require_GET
def attendance(request):
    require_role(request.user, 'student')
    records = request.user.attendance_records.select_related('session__offering').filter(session__starts_at__lte=timezone.now())
    return render(request, 'core/attendance.html', {'title': 'Attendance', 'active': 'attendance', 'attendance': attendance_summary(request.user), 'records': records})


@login_required
@require_GET
def timetable(request):
    sessions = ClassSession.objects.filter(offering__in=visible_offerings(request.user), starts_at__gte=timezone.now()).select_related('offering')
    return render(request, 'core/timetable.html', {'title': 'Timetable', 'active': 'timetable', 'sessions': sessions})


@login_required
@require_GET
def results(request):
    require_role(request.user, 'student')
    return render(request, 'core/results.html', {'title': 'Results', 'active': 'results', 'results': request.user.results.all(), 'cgpa': cgpa(request.user)})


@login_required
@require_GET
def fees(request):
    require_role(request.user, 'student')
    return render(request, 'core/fees.html', {'title': 'Fees', 'active': 'fees', 'fees': request.user.fees.all(), 'balance': balance(request.user)})


@login_required
@require_GET
def helper_records(request):
    user = request.user
    topic = request.GET.get('topic')
    items = []
    if topic == 'pending' and user.role == 'student':
        rows = [r for r in assignment_rows(user) if r['status'] in {'Pending', 'Overdue'}]
        items = [{'title': r['assignment'].title, 'detail': f"{r['status']} · Due {timezone.localtime(r['assignment'].due_at):%d %b %Y, %H:%M}", 'url': reverse('assignment-detail', args=[r['assignment'].pk])} for r in rows]
        heading = f'{len(items)} outstanding assignment' + ('s' if len(items) != 1 else '')
    elif topic == 'attendance' and user.role == 'student':
        s = attendance_summary(user)
        heading = f"{s['attended']} of {s['counted']} counted sessions attended"
        items = [{'title': 'View your attendance', 'detail': 'Catch-up does not change attendance.', 'url': reverse('attendance')}]
    elif topic == 'marking' and user.role == 'lecturer':
        queue = Submission.objects.filter(assignment__offering__lecturers=user, feedback__released_at__isnull=True).select_related('student', 'assignment')
        items = [{'title': f'{s.student} · {s.assignment.title}', 'detail': f'Version {s.version}', 'url': reverse('feedback-edit', args=[s.pk])} for s in queue]
        heading = f'{len(items)} submissions awaiting released feedback'
    elif topic == 'accounts' and user.role == 'admin':
        heading = f'{User.objects.filter(is_active=True).count()} active demo accounts'
    else:
        return JsonResponse({'error': 'That lookup is unavailable for this role.'}, status=400)
    return JsonResponse({'heading': heading, 'items': items, 'mode': 'record_lookup'})


@require_GET
def manifest(request):
    return JsonResponse({'id': '/', 'name': 'UniSphere', 'short_name': 'UniSphere', 'description': 'Your university academic portal', 'start_url': '/', 'scope': '/', 'display': 'standalone', 'background_color': '#f5f8fc', 'theme_color': '#142b40', 'icons': [
        {'src': '/static/icons/icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
        {'src': '/static/icons/icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any'},
        {'src': '/static/icons/icon-maskable.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'},
    ]}, content_type='application/manifest+json')


@require_GET
def service_worker(request):
    assets = [settings.BASE_DIR / path for path in ['static/css/app.css', 'static/js/app.js']]
    version = hashlib.sha256(b''.join(path.read_bytes() for path in assets)).hexdigest()[:12]
    script = (settings.BASE_DIR / 'static/js/service-worker.js').read_text().replace('__CACHE_VERSION__', version)
    response = HttpResponse(script, content_type='application/javascript')
    response['Cache-Control'] = 'no-cache'
    response['Service-Worker-Allowed'] = '/'
    return response


@require_GET
def offline(request):
    return render(request, 'core/offline.html', {'title': 'You are offline'})
