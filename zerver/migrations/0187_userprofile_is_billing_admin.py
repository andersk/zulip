# Generated by Django 1.11.14 on 2018-08-22 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zerver', '0186_userprofile_starred_message_counts'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_billing_admin',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
