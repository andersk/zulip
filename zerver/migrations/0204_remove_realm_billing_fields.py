# Generated by Django 1.11.18 on 2019-01-31 22:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0203_realm_message_content_allowed_in_email_notifications"),
    ]

    operations = [
        migrations.RemoveField(model_name="realm", name="has_seat_based_plan"),
        migrations.RemoveField(model_name="realm", name="seat_limit"),
    ]
