def portal(request):
    return {'portal_role': request.user.get_role_display() if request.user.is_authenticated else '', 'demo_data': True}
