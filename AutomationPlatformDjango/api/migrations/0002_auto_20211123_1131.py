# Generated by Django 2.1.7 on 2021-11-23 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Robot',
            fields=[
                ('robot_id', models.AutoField(primary_key=True, serialize=False, verbose_name='主键')),
                ('group_name', models.CharField(default=None, max_length=200, verbose_name='组名称')),
                ('p_id', models.IntegerField(default=None, null=True, verbose_name='父id')),
                ('type', models.IntegerField(choices=[(1, '组'), (2, '机器人')], default=None, null=True)),
                ('robot_name', models.CharField(max_length=200, null=True, verbose_name='机器人名称')),
                ('keywordList', models.TextField(default=None, null=True, verbose_name='关键词列表')),
                ('web_hook', models.TextField(default=None, null=True, verbose_name='web_hook')),
                ('creator', models.CharField(max_length=50, null=True, verbose_name='创建人')),
                ('update_person', models.CharField(max_length=50, null=True, verbose_name='更新人')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.CharField(choices=[(0, '否'), (1, '是')], default=0, max_length=20, verbose_name='是否删除')),
            ],
            options={
                'db_table': 'config_robot',
            },
        ),
        migrations.AddField(
            model_name='project',
            name='robot_group_id',
            field=models.IntegerField(default=None, null=True, verbose_name='机器人群组id'),
        ),
    ]
