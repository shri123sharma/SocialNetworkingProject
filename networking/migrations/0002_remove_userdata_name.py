# Generated by Django 5.0.6 on 2024-06-10 13:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("networking", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userdata",
            name="name",
        ),
    ]
