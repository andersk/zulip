# Generated by Django 1.11.14 on 2018-10-10 22:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0189_userprofile_add_some_emojisets"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pushdevicetoken",
            name="token",
            field=models.CharField(db_index=True, max_length=4096),
        ),
        migrations.AlterUniqueTogether(
            name="pushdevicetoken", unique_together={("user", "kind", "token")},
        ),
    ]
