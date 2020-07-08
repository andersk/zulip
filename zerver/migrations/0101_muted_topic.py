# Generated by Django 1.11.4 on 2017-08-30 00:26
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0100_usermessage_remove_is_me_message"),
    ]

    operations = [
        migrations.CreateModel(
            name="MutedTopic",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID",
                    ),
                ),
                ("topic_name", models.CharField(max_length=60)),
                (
                    "recipient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="zerver.Recipient",
                    ),
                ),
                (
                    "stream",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="zerver.Stream",
                    ),
                ),
                (
                    "user_profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name="mutedtopic", unique_together={("user_profile", "stream", "topic_name")},
        ),
    ]
