# Generated by Django 4.2 on 2024-08-28 12:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Наименование')),
                ('city', models.CharField(choices=[('Almaty', 'Алматы'), ('Astana', 'Астана'), ('Karaganda', 'Караганда'), ('Shymkent', 'Шымкент')], verbose_name='Город')),
                ('address', models.CharField(max_length=256, verbose_name='Адрес')),
                ('available', models.BooleanField(default=True, verbose_name='Доступна')),
            ],
            options={
                'verbose_name': 'Площадка',
                'verbose_name_plural': 'Площадки',
                'db_table': 'areas',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Наименование')),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
                'db_table': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Наименование')),
                ('start_at', models.DateTimeField(verbose_name='Дата и время начала')),
                ('end_at', models.DateTimeField(verbose_name='Дата и время окончания')),
                ('age_limit', models.IntegerField(choices=[(0, 'Без ограничений'), (6, 'от 6 лет'), (12, 'от 12 лет'), (16, 'от 16 лет'), (18, 'от 18 лет'), (21, 'от 21 года')], verbose_name='Возрастное огранчиение')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('schema', models.ImageField(blank=True, null=True, upload_to='schemas', verbose_name='Схема площадки')),
                ('quantity', models.PositiveIntegerField(verbose_name='Количество доступных мест')),
                ('min_price', models.PositiveIntegerField(default=0, verbose_name='Минимальная цена')),
                ('canceled', models.BooleanField(default=False, verbose_name='Отменено')),
                ('slug', models.SlugField(blank=True, max_length=200, unique_for_date='start_at', verbose_name='Слаг')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время добавления')),
                ('area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='events.area', verbose_name='Площадка')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='events.category', verbose_name='Категория')),
            ],
            options={
                'verbose_name': 'Мероприятие',
                'verbose_name_plural': 'Мероприятия',
                'db_table': 'events',
            },
        ),
        migrations.CreateModel(
            name='Landing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section', models.CharField(blank=True, max_length=64, null=True, verbose_name='Секция')),
                ('row', models.CharField(blank=True, max_length=64, null=True, verbose_name='Ряд')),
                ('quantity', models.PositiveIntegerField(verbose_name='Количество мест')),
                ('price', models.DecimalField(decimal_places=2, max_digits=7, verbose_name='Цена за место')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='landings', to='events.event', verbose_name='Мероприятие')),
            ],
            options={
                'verbose_name': 'Посадка',
                'verbose_name_plural': 'Посадки',
                'db_table': 'landings',
                'unique_together': {('event', 'section', 'row')},
            },
        ),
    ]
