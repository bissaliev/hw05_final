# Generated by Django 5.1 on 2024-08-30 06:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0004_auto_20240830_0618"),
    ]

    operations = [
        migrations.AlterField(
            model_name="follow",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]