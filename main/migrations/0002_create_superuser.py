import os

from django.contrib.auth import get_user_model
from django.db import migrations
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    @staticmethod
    def create_superuser(apps, schema_editor):
        username = os.getenv('DJANGO_SU_USERNAME', 'admin')
        password = os.getenv('DJANGO_SU_PASSWORD', 'admin')
        email = os.getenv('DJANGO_SU_EMAIL', 'example@email.com')
        get_user_model().objects.create_superuser(
            username=username,
            password=password,
            email=email,
            last_login=timezone.now()
        )

    operations = [migrations.RunPython(create_superuser)]
