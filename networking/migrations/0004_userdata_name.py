# Generated by Django 5.0.6 on 2024-06-12 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("networking", "0003_friendrequest"),
    ]

    operations = [
        migrations.AddField(
            model_name="userdata",
            name="name",
            field=models.CharField(blank=True, max_length=150),
        ),
    ]