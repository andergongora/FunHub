# Generated by Django 4.2.1 on 2023-05-15 12:39

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0013_alter_favorites_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertag',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Created Date'),
            preserve_default=False,
        ),
    ]
