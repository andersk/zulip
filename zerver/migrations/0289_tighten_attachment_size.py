# Generated by Django 2.2.13 on 2020-06-20 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0288_reaction_unique_on_emoji_code"),
    ]

    operations = [
        migrations.AlterField(
            model_name="archivedattachment",
            name="size",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="attachment", name="size", field=models.IntegerField(default=0), preserve_default=False,
        ),
    ]
