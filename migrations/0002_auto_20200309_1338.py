# Generated by Django 3.0.3 on 2020-03-09 04:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compare', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='lr',
            field=models.PositiveSmallIntegerField(choices=[(0, ''), (1, '右'), (2, '左')]),
        ),
    ]
