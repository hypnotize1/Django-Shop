# Generated by Django 5.0.7 on 2025-07-13 12:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_category_is_sub_category_sub_category_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='is_sub',
        ),
    ]
