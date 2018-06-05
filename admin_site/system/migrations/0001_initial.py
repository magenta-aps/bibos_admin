# -*- coding: utf-8 -*-


from django.db import migrations, models
from django.conf import settings
import system.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
            ],
        ),
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ConfigurationEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=32)),
                ('value', models.CharField(max_length=4096)),
                ('owner_configuration', models.ForeignKey(related_name='entries', verbose_name='owner configuration', to='system.Configuration')),
            ],
        ),
        migrations.CreateModel(
            name='CustomPackages',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
            ],
        ),
        migrations.CreateModel(
            name='Distribution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('uid', models.CharField(max_length=255, verbose_name='uid')),
                ('configuration', models.ForeignKey(to='system.Configuration')),
            ],
        ),
        migrations.CreateModel(
            name='Input',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('value_type', models.CharField(max_length=10, verbose_name='value type', choices=[(b'STRING', 'String'), (b'INT', 'Integer'), (b'DATE', 'Date'), (b'FILE', 'File')])),
                ('position', models.IntegerField(verbose_name='position')),
                ('mandatory', models.BooleanField(default=True, verbose_name='mandatory')),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'NEW', max_length=10, choices=[(b'NEW', 'jobstatus:New'), (b'SUBMITTED', 'jobstatus:Submitted'), (b'RUNNING', 'jobstatus:Running'), (b'FAILED', 'jobstatus:Failed'), (b'DONE', 'jobstatus:Done'), (b'RESOLVED', 'jobstatus:Resolved')])),
                ('log_output', models.CharField(max_length=128000, verbose_name='log output', blank=True)),
                ('started', models.DateTimeField(null=True, verbose_name='started')),
                ('finished', models.DateTimeField(null=True, verbose_name='finished')),
                ('batch', models.ForeignKey(related_name='jobs', to='system.Batch')),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('version', models.CharField(max_length=255, verbose_name='version')),
                ('description', models.CharField(max_length=255, verbose_name='description')),
            ],
        ),
        migrations.CreateModel(
            name='PackageInstallInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('do_add', models.BooleanField(default=True)),
                ('custom_packages', models.ForeignKey(related_name='install_infos', to='system.CustomPackages')),
                ('package', models.ForeignKey(to='system.Package')),
            ],
        ),
        migrations.CreateModel(
            name='PackageList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
            ],
        ),
        migrations.CreateModel(
            name='PackageStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=255)),
                ('package', models.ForeignKey(to='system.Package')),
                ('package_list', models.ForeignKey(related_name='statuses', to='system.PackageList')),
            ],
        ),
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('string_value', models.CharField(max_length=4096, null=True, blank=True)),
                ('file_value', models.FileField(null=True, upload_to=system.models.upload_file_name, blank=True)),
                ('batch', models.ForeignKey(related_name='parameters', to='system.Batch')),
                ('input', models.ForeignKey(to='system.Input')),
            ],
        ),
        migrations.CreateModel(
            name='PC',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('uid', models.CharField(max_length=255, verbose_name='uid')),
                ('description', models.CharField(max_length=1024, verbose_name='description', blank=True)),
                ('is_active', models.BooleanField(default=False, verbose_name='active')),
                ('is_update_required', models.BooleanField(default=False, verbose_name='update required')),
                ('do_send_package_info', models.BooleanField(default=True, verbose_name='send package info')),
                ('creation_time', models.DateTimeField(auto_now_add=True, verbose_name='creation time')),
                ('last_seen', models.DateTimeField(null=True, verbose_name='last seen', blank=True)),
                ('configuration', models.ForeignKey(to='system.Configuration')),
                ('custom_packages', models.ForeignKey(blank=True, to='system.CustomPackages', null=True)),
                ('distribution', models.ForeignKey(to='system.Distribution')),
                ('package_list', models.ForeignKey(blank=True, to='system.PackageList', null=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='PCGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('uid', models.CharField(unique=True, max_length=255, verbose_name='id')),
                ('description', models.TextField(max_length=1024, null=True, verbose_name='description', blank=True)),
                ('configuration', models.ForeignKey(to='system.Configuration')),
                ('custom_packages', models.ForeignKey(to='system.CustomPackages')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Script',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('description', models.TextField(max_length=4096, verbose_name='description')),
                ('executable_code', models.FileField(upload_to=b'script_uploads', verbose_name='executable code')),
                ('is_security_script', models.BooleanField(default=False, verbose_name='security script')),
            ],
        ),
        migrations.CreateModel(
            name='SecurityEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ocurred_time', models.DateTimeField(verbose_name='occurred')),
                ('reported_time', models.DateTimeField(verbose_name='reported')),
                ('summary', models.CharField(max_length=4096)),
                ('complete_log', models.TextField(null=True, blank=True)),
                ('status', models.CharField(default=b'NEW', max_length=10, choices=[(b'NEW', 'eventstatus:New'), (b'ASSIGNED', 'eventstatus:Assigned'), (b'RESOLVED', 'eventstatus:Resolved')])),
                ('note', models.TextField(null=True, blank=True)),
                ('assigned_user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('pc', models.ForeignKey(to='system.PC')),
            ],
        ),
        migrations.CreateModel(
            name='SecurityProblem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('uid', models.SlugField(verbose_name='uid')),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('level', models.CharField(default=b'High', max_length=10, choices=[(b'Critical', 'securitylevel:Critical'), (b'High', 'securitylevel:High'), (b'Normal', 'securitylevel:Normal')])),
                ('alert_groups', models.ManyToManyField(related_name='security_problems', to='system.PCGroup', blank=True)),
                ('alert_users', models.ManyToManyField(related_name='security_problems', to=settings.AUTH_USER_MODEL, blank=True)),
                ('script', models.ForeignKey(related_name='security_problems', to='system.Script')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('uid', models.CharField(unique=True, max_length=255, verbose_name='uid')),
                ('configuration', models.ForeignKey(to='system.Configuration')),
                ('security_alerts', models.ManyToManyField(related_name='alert_sites', to='system.SecurityProblem', blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='securityproblem',
            name='site',
            field=models.ForeignKey(related_name='security_problems', to='system.Site'),
        ),
        migrations.AddField(
            model_name='securityevent',
            name='problem',
            field=models.ForeignKey(to='system.SecurityProblem'),
        ),
        migrations.AddField(
            model_name='script',
            name='site',
            field=models.ForeignKey(related_name='scripts', blank=True, to='system.Site', null=True),
        ),
        migrations.AddField(
            model_name='pcgroup',
            name='site',
            field=models.ForeignKey(related_name='groups', to='system.Site'),
        ),
        migrations.AddField(
            model_name='pc',
            name='pc_groups',
            field=models.ManyToManyField(related_name='pcs', to='system.PCGroup', blank=True),
        ),
        migrations.AddField(
            model_name='pc',
            name='site',
            field=models.ForeignKey(related_name='pcs', to='system.Site'),
        ),
        migrations.AddField(
            model_name='packagelist',
            name='packages',
            field=models.ManyToManyField(to='system.Package', through='system.PackageStatus', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='package',
            unique_together=set([('name', 'version')]),
        ),
        migrations.AddField(
            model_name='job',
            name='pc',
            field=models.ForeignKey(related_name='jobs', to='system.PC'),
        ),
        migrations.AddField(
            model_name='job',
            name='user',
            field=models.ForeignKey(related_name='job', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='input',
            name='script',
            field=models.ForeignKey(related_name='inputs', to='system.Script'),
        ),
        migrations.AddField(
            model_name='distribution',
            name='package_list',
            field=models.ForeignKey(to='system.PackageList'),
        ),
        migrations.AddField(
            model_name='custompackages',
            name='packages',
            field=models.ManyToManyField(to='system.Package', through='system.PackageInstallInfo', blank=True),
        ),
        migrations.AddField(
            model_name='batch',
            name='script',
            field=models.ForeignKey(to='system.Script'),
        ),
        migrations.AddField(
            model_name='batch',
            name='site',
            field=models.ForeignKey(related_name='batches', to='system.Site'),
        ),
        migrations.AlterUniqueTogether(
            name='securityproblem',
            unique_together=set([('uid', 'site')]),
        ),
        migrations.AlterUniqueTogether(
            name='pcgroup',
            unique_together=set([('uid', 'site')]),
        ),
    ]
