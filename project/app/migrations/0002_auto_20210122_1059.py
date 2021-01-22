# Generated by Django 3.1.5 on 2021-01-22 17:59

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='school',
            name='description',
        ),
        migrations.RemoveField(
            model_name='school',
            name='kind',
        ),
        migrations.RemoveField(
            model_name='school',
            name='status',
        ),
        migrations.AddField(
            model_name='school',
            name='grades',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(choices=[(-1, 'Preschool'), (0, 'Kindergarten'), (1, 'First Grade'), (2, 'Second Grade'), (3, 'Third Grade'), (4, 'Fourth Grade'), (5, 'Fifth Grade'), (6, 'Sixth Grade'), (7, 'Seventh Grade'), (8, 'Eighth Grade'), (9, 'Ninth Grade'), (10, 'Tenth Grade'), (11, 'Eleventh Grade'), (12, 'Twelfth Grade')]), blank=True, null=True, size=None),
        ),
    ]
