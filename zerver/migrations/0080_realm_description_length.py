# Generated by Django 1.10.5 on 2017-05-11 20:27
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0079_remove_old_scheduled_jobs"),
    ]

    operations = [
        migrations.AlterField(
            model_name="realm", name="description", field=models.TextField(null=True),
        ),
    ]
