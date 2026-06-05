from django.apps import AppConfig
import sys
import os


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'Foydalanuvchilar'

    def ready(self):
        """Create an admin user on startup if ADMIN_USERNAME and ADMIN_PASSWORD are set.

        This is convenient for deploys but use with caution in production.
        Skip during management commands such as migrate/collectstatic/tests.
        """
        # Don't run during management commands that shouldn't hit the DB yet
        if len(sys.argv) > 1 and sys.argv[1] in (
            'migrate', 'makemigrations', 'collectstatic', 'shell', 'test'
        ):
            return

        from django.conf import settings
        from django.contrib.auth import get_user_model

        username = os.environ.get('ADMIN_USERNAME') or getattr(settings, 'ADMIN_USERNAME', '')
        password = os.environ.get('ADMIN_PASSWORD') or getattr(settings, 'ADMIN_PASSWORD', '')
        email = os.environ.get('ADMIN_EMAIL') or getattr(settings, 'ADMIN_EMAIL', '')

        if not username or not password:
            return

        User = get_user_model()
        try:
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(username=username, email=email or None, password=password)
        except Exception:
            # Avoid crashing startup for any unexpected DB/state issues
            pass
