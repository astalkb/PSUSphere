# Generated by Django 5.1.2 on 2024-11-06 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studentorg', '0003_alter_student_college'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='lastname',
            field=models.CharField(max_length=25, verbose_name='Last Name'),
        ),
    ]