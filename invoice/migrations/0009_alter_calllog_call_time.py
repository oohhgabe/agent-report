# Generated by Django 4.1.5 on 2023-02-06 02:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("invoice", "0008_alter_calllog_callid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="calllog",
            name="Call_Time",
            field=models.CharField(
                blank=True, max_length=255, verbose_name="Call Time"
            ),
        ),
    ]