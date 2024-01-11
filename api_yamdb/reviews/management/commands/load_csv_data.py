import csv
import os

from django.core.management import BaseCommand
from django.db import IntegrityError

from api_yamdb.settings import CSV_FILES_DIR
from reviews.models import (
    Category, Comment, Genre, GenreTitle, Review, Title
)
from users.models import User


MODELS = {
    'users': User,
    'category': Category,
    'genre': Genre,
    'titles': Title,
    'genre_title': GenreTitle,
    'review': Review,
    'comments': Comment
}

FIELDS = {
    'category': ('category', Category),
    'genre_id': ('genre', Genre),
    'title_id': ('title', Title),
    'author': ('author', User),
    'review_id': ('review', Review)
}


def open_csv_file(file_name):
    csv_file = file_name + '.csv'
    csv_path = os.path.join(CSV_FILES_DIR, csv_file)
    try:
        with (open(csv_path, encoding='utf-8')) as file:
            return list(csv.reader(file))
    except FileNotFoundError:
        print(f'Файл {csv_file} не найден')


def add_values(data_csv):
    csv_copy = data_csv.copy()
    for field_key, field_value in data_csv.items():
        if field_key in FIELDS.keys():
            field_key_index = FIELDS[field_key][0]
            csv_copy[field_key_index] = FIELDS[field_key][1].objects.get(
                pk=field_value)
    return csv_copy


def load_csv(file_name, class_name):
    data = open_csv_file(file_name)
    rows = data[1:]
    for row in rows:
        data_csv = dict(zip(data[0], row))
        data_csv = add_values(data_csv)
        try:
            table = class_name(**data_csv)
            table.save()
        except (ValueError, IntegrityError) as error:
            print(f'При загрузке произошла ошибка. {error}')


class Command(BaseCommand):

    def handle(self, *args, **options):
        for key, value in MODELS.items():
            load_csv(key, value)
        self.stdout.write(self.style.SUCCESS('Загрузка выполнена успешно'))
