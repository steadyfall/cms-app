# Generated by Django 4.2.4 on 2023-08-20 13:24

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("adminpanel", "0003_case_date_created_case_last_updated"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="case",
            options={"ordering": ["-amount"]},
        ),
    ]
