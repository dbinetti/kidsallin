# Generated by Django 3.1.5 on 2021-01-27 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20210127_1018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='email',
            name='charsets',
            field=models.TextField(blank=True, max_length=255, null=True, verbose_name='Charsets'),
        ),
        migrations.AlterField(
            model_name='email',
            name='spam_score',
            field=models.TextField(blank=True, null=True, verbose_name='Spam score'),
        ),
    ]
