# Generated by Django 3.2.6 on 2022-11-21 15:05

from django.db import migrations, models
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20221031_1801'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billingproject',
            name='email_notification',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name='flavorprice',
            name='hourly_price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='flavorprice',
            name='monthly_price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='floatingipsprice',
            name='hourly_price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='floatingipsprice',
            name='monthly_price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='imageprice',
            name='hourly_price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='imageprice',
            name='monthly_price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='tax_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='total_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='invoicefloatingip',
            name='hourly_price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='invoicefloatingip',
            name='monthly_price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='invoiceimage',
            name='hourly_price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='invoiceimage',
            name='monthly_price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='invoiceinstance',
            name='hourly_price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='invoiceinstance',
            name='monthly_price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='invoicerouter',
            name='hourly_price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='invoicerouter',
            name='monthly_price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='invoicesnapshot',
            name='hourly_price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='invoicesnapshot',
            name='monthly_price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='invoicevolume',
            name='hourly_price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='invoicevolume',
            name='monthly_price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='routerprice',
            name='hourly_price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='routerprice',
            name='monthly_price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='snapshotprice',
            name='hourly_price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='snapshotprice',
            name='monthly_price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='volumeprice',
            name='hourly_price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='volumeprice',
            name='monthly_price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3),
        ),
    ]