# Generated by Django 1.11.6 on 2018-05-12 04:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0168_stream_is_web_public"),
    ]

    operations = [
        migrations.AddField(
            model_name="stream", name="is_announcement_only", field=models.BooleanField(default=False),
        ),
    ]
