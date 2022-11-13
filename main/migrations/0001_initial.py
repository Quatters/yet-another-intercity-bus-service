# Generated by Django 4.1.3 on 2022-11-10 12:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bus_number', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='BusModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('seats_amount', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('departure_date', models.DateField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('bus', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='main.bus')),
            ],
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('route_number', models.CharField(max_length=5)),
                ('distance_km', models.IntegerField()),
                ('from_city', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='from_cities', to='main.city')),
                ('to_city', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='to_cities', to='main.city')),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seat_number', models.IntegerField()),
                ('customer_name', models.CharField(default=None, max_length=128, null=True)),
                ('flight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.flight')),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('departure_time', models.DateTimeField()),
                ('arrival_time', models.DateTimeField()),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.route')),
            ],
        ),
        migrations.AddField(
            model_name='flight',
            name='schedule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.schedule'),
        ),
        migrations.AddField(
            model_name='bus',
            name='model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='main.busmodel'),
        ),
    ]