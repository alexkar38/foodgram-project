# Generated by Django 3.2.5 on 2022-08-08 11:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='favorite',
            name='added',
        ),
    ]