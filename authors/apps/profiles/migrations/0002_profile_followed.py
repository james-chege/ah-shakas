# Generated by Django 2.1.2 on 2018-11-23 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='followed',
            field=models.ManyToManyField(to='profiles.Profile'),
        ),
    ]
