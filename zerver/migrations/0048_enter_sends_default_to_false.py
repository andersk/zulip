# Generated by Django 1.10.4 on 2016-12-29 02:18
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zerver', '0047_realm_add_emoji_by_admins_only'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='enter_sends',
            field=models.NullBooleanField(default=False),
        ),
    ]
