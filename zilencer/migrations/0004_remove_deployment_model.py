# Generated by Django 1.11.5 on 2017-10-12 06:27
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("zilencer", "0003_add_default_for_remotezulipserver_last_updated_field"),
    ]

    operations = [
        migrations.RemoveField(model_name="deployment", name="realms"),
        migrations.DeleteModel(name="Deployment"),
    ]
