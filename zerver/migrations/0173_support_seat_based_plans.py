# Generated by Django 1.11.13 on 2018-06-28 01:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0172_add_user_type_of_custom_profile_field"),
    ]

    operations = [
        migrations.AddField(
            model_name="realm", name="has_seat_based_plan", field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="realmauditlog",
            name="requires_billing_update",
            field=models.BooleanField(default=False),
        ),
    ]
