# Generated by Django 5.2.1 on 2025-06-04 11:58

import django.core.validators
import uuid
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ChamaGroup',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('chama_type', models.CharField(choices=[('merry_go_round', 'Merry-Go-Round'), ('investment', 'Investment Group'), ('sacco', 'SACCO')], default='merry_go_round', max_length=20)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('completed', 'Completed'), ('suspended', 'Suspended')], default='active', max_length=20)),
                ('contribution_amount', models.DecimalField(decimal_places=2, help_text='Monthly contribution amount in AVAX', max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('contribution_frequency', models.CharField(choices=[('weekly', 'Weekly'), ('monthly', 'Monthly'), ('quarterly', 'Quarterly')], default='monthly', max_length=20)),
                ('max_members', models.PositiveIntegerField(default=12)),
                ('minimum_members', models.PositiveIntegerField(default=3)),
                ('contract_address', models.CharField(blank=True, max_length=42, null=True)),
                ('contract_deployed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Chama Group',
                'verbose_name_plural': 'Chama Groups',
                'db_table': 'chama_groups',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Contribution',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('expected_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transaction_hash', models.CharField(blank=True, max_length=66, null=True, unique=True)),
                ('block_number', models.PositiveIntegerField(blank=True, null=True)),
                ('gas_used', models.PositiveIntegerField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('contribution_date', models.DateTimeField(auto_now_add=True)),
                ('due_date', models.DateField()),
                ('confirmed_at', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('late_fee', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
            ],
            options={
                'verbose_name': 'Contribution',
                'verbose_name_plural': 'Contributions',
                'db_table': 'contributions',
                'ordering': ['-contribution_date'],
            },
        ),
        migrations.CreateModel(
            name='GroupMembership',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('role', models.CharField(choices=[('admin', 'Administrator'), ('treasurer', 'Treasurer'), ('secretary', 'Secretary'), ('member', 'Member')], default='member', max_length=20)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('suspended', 'Suspended'), ('left', 'Left Group')], default='active', max_length=20)),
                ('payout_position', models.PositiveIntegerField(blank=True, null=True)),
                ('has_received_payout', models.BooleanField(default=False)),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('left_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Group Membership',
                'verbose_name_plural': 'Group Memberships',
                'db_table': 'group_memberships',
                'ordering': ['payout_position', 'joined_at'],
            },
        ),
        migrations.CreateModel(
            name='Payout',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transaction_hash', models.CharField(blank=True, max_length=66, null=True, unique=True)),
                ('block_number', models.PositiveIntegerField(blank=True, null=True)),
                ('gas_used', models.PositiveIntegerField(blank=True, null=True)),
                ('status', models.CharField(choices=[('scheduled', 'Scheduled'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='scheduled', max_length=20)),
                ('scheduled_date', models.DateField()),
                ('processed_at', models.DateTimeField(blank=True, null=True)),
                ('round_number', models.PositiveIntegerField()),
            ],
            options={
                'verbose_name': 'Payout',
                'verbose_name_plural': 'Payouts',
                'db_table': 'payouts',
                'ordering': ['-scheduled_date'],
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('transaction_hash', models.CharField(max_length=66, unique=True)),
                ('transaction_type', models.CharField(choices=[('contribution', 'Contribution'), ('payout', 'Payout'), ('contract_deployment', 'Contract Deployment'), ('other', 'Other')], max_length=20)),
                ('from_address', models.CharField(max_length=42)),
                ('to_address', models.CharField(max_length=42)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('gas_price', models.BigIntegerField()),
                ('gas_used', models.PositiveIntegerField(blank=True, null=True)),
                ('block_number', models.PositiveIntegerField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('confirmed_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Transaction',
                'verbose_name_plural': 'Transactions',
                'db_table': 'transactions',
                'ordering': ['-created_at'],
            },
        ),
    ]
