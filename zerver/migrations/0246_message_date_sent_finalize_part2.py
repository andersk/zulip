# Generated by Django 1.11.23 on 2019-08-28 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0245_message_date_sent_finalize_part1"),
    ]

    operations = [
        # Until now, date_sent was in ArchivedMessage only for the sake of keeping the model
        # compatible with Message.
        #  We can now remove it, and rename pub_date to date_sent to have this column
        # set correctly for all existing rows.
        migrations.RemoveField(model_name="archivedmessage", name="date_sent"),
        migrations.RenameField(model_name="archivedmessage", old_name="pub_date", new_name="date_sent"),
        # All the below AlterField does is change verbose_name, which doesn't even generate any SQL,
        # it's just a purely-Django attribute.
        migrations.AlterField(
            model_name="archivedmessage",
            name="date_sent",
            field=models.DateTimeField(db_index=True, verbose_name="date sent"),
        ),
        # Django doesn't rename the index when renaming a column, which can be confusing
        # for someone inspecting the table in the future who's not aware of the old name.
        # We should rename appropriately here.
        migrations.RunSQL(
            """
        ALTER INDEX IF EXISTS zerver_archivedmessage_pub_date_509062c8 RENAME TO zerver_archivedmessage_date_sent_509062c8
        """,
        ),
        migrations.RemoveField(model_name="message", name="pub_date"),
    ]
