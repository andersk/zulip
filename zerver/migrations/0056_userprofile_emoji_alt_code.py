# Generated by Django 1.10.5 on 2017-03-02 07:28
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zerver', '0055_attachment_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='emoji_alt_code',
            field=models.BooleanField(default=False),
        ),
    ]
