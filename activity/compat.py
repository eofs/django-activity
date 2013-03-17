import django


if django.VERSION >= (1, 5):
    from django.conf import settings
    if hasattr(settings, 'AUTH_USER_MODEL'):
        User = settings.AUTH_USER_MODEL
    else:
        from django.contrib.auth.models import User
else:
    from django.contrib.auth.models import User
