# Generated by Django 1.11.18 on 2019-02-06 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0206_stream_rendered_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="multiuseinvite", name="invited_as", field=models.PositiveSmallIntegerField(default=1),
        ),
    ]
