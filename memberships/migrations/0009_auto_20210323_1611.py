# Generated by Django 3.1.7 on 2021-03-23 16:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("memberships", "0008_member_renewal_date"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="failedpayment",
            name="stripe_customer_id",
        ),
        migrations.AddField(
            model_name="failedpayment",
            name="member",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="memberships.member"
            ),
        ),
        migrations.AlterField(
            model_name="member",
            name="stripe_customer_id",
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
