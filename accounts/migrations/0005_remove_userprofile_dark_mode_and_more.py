# Generated by Django 5.2 on 2025-05-01 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_create_userprofiles'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='dark_mode',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='last_login_device',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='last_login_ip',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='show_in_leaderboard',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='first_name',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='last_name',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='role',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_complete',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_photo',
            field=models.ImageField(blank=True, null=True, upload_to='profile_photos/'),
        ),
    ]
