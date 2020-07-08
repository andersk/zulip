# Generated by Django 2.2.13 on 2020-06-09 09:37

import bitfield.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("zerver", "0282_remove_zoom_video_chat"),
    ]

    operations = [
        migrations.AlterField(
            model_name="realm",
            name="authentication_methods",
            field=bitfield.models.BitField(
                ["Google", "Email", "GitHub", "LDAP", "Dev", "RemoteUser", "AzureAD", "SAML", "GitLab", "Apple"],
                default=2147483647,
            ),
        ),
    ]
