# Generated by Django 3.1 on 2024-06-20 13:02

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations


def compute_search_vector(apps, schema_editor):
    Post = apps.get_model("posts", "Post")
    Post.objects.update(
        search_vector=django.contrib.postgres.search.SearchVector(
            "title", "text", config="russian"
        )
    )


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0004_auto_20240619_1313"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="search_vector",
            field=django.contrib.postgres.search.SearchVectorField(null=True),
        ),
        migrations.AddIndex(
            model_name="post",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["search_vector"], name="posts_post_search__e0bb56_gin"
            ),
        ),
        migrations.RunPython(
            compute_search_vector, reverse_code=migrations.RunPython.noop
        ),
    ]
