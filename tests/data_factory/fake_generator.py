# tests/data_factory/fake_generator.py
# flake8: noqa: E501
import random
from decimal import Decimal
from typing import Any, Dict, List, Union
from faker import Faker


class TestDataGenerator:
    def __init__(self):
        self.fake_en = Faker('en_US')
        self.fake_ru = Faker('ru_RU')
        self.fake_fr = Faker('fr_FR')

        # Языковые фейкеры
        self.fakers = {
            'en': self.fake_en,
            'ru': self.fake_ru,
            'fr': self.fake_fr,
        }

        # Цвета на разных языках
        self.colors = {
            'en': ['Red', 'White', 'Rosé', 'Orange', 'Sparkling Red', 'Dessert Wine', 'Fortified'],
            'ru': ['Красное', 'Белое', 'Розовое', 'Оранжевое', 'Игристое красное', 'Десертное', 'Креплёное'],
            'fr': ['Rouge', 'Blanc', 'Rosé', 'Orange', 'Rouge mousseux', 'Vin de dessert', 'Fortifié'],
        }

        # Страны, регионы, субрегионы (упрощённый справочник)
        self.geo_hierarchy = [
            {
                'country': {'en': 'France', 'ru': 'Франция', 'fr': 'France'},
                'regions': [
                    {
                        'name': {'en': 'Bordeaux', 'ru': 'Бордо', 'fr': 'Bordeaux'},
                        'subregions': [
                            {'en': 'Médoc', 'ru': 'Медок', 'fr': 'Médoc'},
                            {'en': 'Saint-Émilion', 'ru': 'Сент-Эмильон', 'fr': 'Saint-Émilion'},
                            {'en': 'Pomerol', 'ru': 'Помроль', 'fr': 'Pomerol'},
                        ]
                    },
                    {
                        'name': {'en': 'Burgundy', 'ru': 'Бургундия', 'fr': 'Bourgogne'},
                        'subregions': [
                            {'en': 'Côte de Nuits', 'ru': 'Кот-де-Нюи', 'fr': 'Côte de Nuits'},
                            {'en': 'Côte de Beaune', 'ru': 'Кот-де-Бон', 'fr': 'Côte de Beaune'},
                        ]
                    },
                ]
            },
            {
                'country': {'en': 'Italy', 'ru': 'Италия', 'fr': 'Italie'},
                'regions': [
                    {
                        'name': {'en': 'Tuscany', 'ru': 'Тоскана', 'fr': 'Toscane'},
                        'subregions': [
                            {'en': 'Chianti', 'ru': 'Кьянти', 'fr': 'Chianti'},
                            {'en': 'Montalcino', 'ru': 'Монтальчино', 'fr': 'Montalcino'},
                        ]
                    },
                    {
                        'name': {'en': 'Piedmont', 'ru': 'Пьемонт', 'fr': 'Piémont'},
                        'subregions': [
                            {'en': 'Barolo', 'ru': 'Бароло', 'fr': 'Barolo'},
                            {'en': 'Asti', 'ru': 'Асти', 'fr': 'Asti'},
                        ]
                    },
                ]
            },
            {
                'country': {'en': 'Spain', 'ru': 'Испания', 'fr': 'Espagne'},
                'regions': [
                    {
                        'name': {'en': 'Rioja', 'ru': 'Рибера-дель-Дуэро', 'fr': 'Rioja'},
                        'subregions': [
                            {'en': 'Alavesa', 'ru': 'Алавеса', 'fr': 'Alavesa'},
                            {'en': 'Baja', 'ru': 'Баха', 'fr': 'Baja'},
                        ]
                    },
                ]
            },
        ]

    def _generate_string(self, key: str) -> str:
        lang = 'en'
        if key.endswith('_ru'):
            lang = 'ru'
        elif key.endswith('_fr'):
            lang = 'fr'

        faker = self.fakers[lang]

        if 'name' in key and 'description' not in key:
            return faker.word().capitalize()
        elif 'description' in key:
            return " ".join(faker.sentences(nb=random.randint(5, 10)))
        elif 'subtitle' == key:
            return faker.sentence(nb_words=6)
        else:
            return faker.sentence(nb_words=4)

    def _generate_decimal(self) -> float:
        return round(round(random.uniform(5.0, 16.0), 2))

    def _generate_integer(self) -> int:
        return random.randint(6, 36)

    def _generate_bool(self) -> bool:
        return random.choice([True, False])

    def _generate_color(self, key: str) -> str:
        lang = 'en'
        if key.endswith('_ru'):
            lang = 'ru'
        elif key.endswith('_fr'):
            lang = 'fr'
        return random.choice(self.colors[lang])

    def _generate_geo_data(self) -> Dict[str, Any]:
        country_data = random.choice(self.geo_hierarchy)
        region_data = random.choice(country_data['regions'])
        subregion_name = random.choice(region_data['subregions'])

        return {
            'country': {
                'name': country_data['country']['en'],
                'name_ru': country_data['country']['ru'],
                'name_fr': country_data['country']['fr'],
                'description': f"{country_data['country']['en']} is a country in Europe known for wine.",
                'description_ru': f"{country_data['country']['ru']} — страна в Европе, известная своими винами.",
                'description_fr': f"{country_data['country']['fr']} est un pays d'Europe réputé pour son vin.",
            },
            'region': {
                'name': region_data['name']['en'],
                'name_ru': region_data['name']['ru'],
                'name_fr': region_data['name']['fr'],
                'description': f"{region_data['name']['en']} is a wine region in {country_data['country']['en']}.",
                'description_ru': f"{region_data['name']['ru']} — винный регион в {country_data['country']['ru']}.",
                'description_fr': f"{region_data['name']['fr']} est une région viticole en {country_data['country']['fr']}.",
            },
            'subregion': {
                'name': subregion_name['en'],
                'name_ru': subregion_name['ru'],
                'name_fr': subregion_name['fr'],
                'description': f"{subregion_name['en']} is a subregion of {region_data['name']['en']}.",
                'description_ru': f"{subregion_name['ru']} — субрегион {region_data['name']['ru']}.",
                'description_fr': f"{subregion_name['fr']} est un sous-région de {region_data['name']['fr']}.",
            }
        }

    def _generate_list(self, template_list: List[Dict], depth: int = 0) -> List[Dict]:
        count = random.randint(1, 3)
        result = []
        for _ in range(count):
            item = self._generate_from_template(template_list[0], depth + 1)
            result.append(item)
        return result

    def _generate_from_template(self, template: Union[Dict, str], depth: int = 0) -> Any:
        if isinstance(template, str):
            # Примитивный тип
            if template == 'string':
                key = 'field'
                return self._generate_string(key)
            elif template == 'decimal':
                return self._generate_decimal()
            elif template == 'integer':
                return self._generate_integer()
            elif isinstance(template, bool):
                return self._generate_bool()
            else:
                return None

        if isinstance(template, dict):
            result = {}
            for key, value in template.items():
                if key == 'color_id':
                    # Специальная обработка цвета
                    result[key] = {
                        'name': self._generate_color('name'),
                        'name_ru': self._generate_color('name_ru'),
                        'name_fr': self._generate_color('name_fr'),
                        'description': self._generate_string('description'),
                        'description_ru': self._generate_string('description_ru'),
                        'description_fr': self._generate_string('description_fr'),
                    }
                elif key == 'subregion_id':
                    geo_data = self._generate_geo_data()
                    result[key] = {
                        'region': {
                            'country': geo_data['country'],
                            'name': geo_data['region']['name'],
                            'name_ru': geo_data['region']['name_ru'],
                            'name_fr': geo_data['region']['name_fr'],
                            'description': geo_data['region']['description'],
                            'description_ru': geo_data['region']['description_ru'],
                            'description_fr': geo_data['region']['description_fr'],
                        },
                        'name': geo_data['subregion']['name'],
                        'name_ru': geo_data['subregion']['name_ru'],
                        'name_fr': geo_data['subregion']['name_fr'],
                        'description': geo_data['subregion']['description'],
                        'description_ru': geo_data['subregion']['description_ru'],
                        'description_fr': geo_data['subregion']['description_fr'],
                    }
                elif key in ['category_id', 'sweetness_id']:
                    # Общие справочники
                    name = self._generate_string('name')
                    result[key] = {
                        'name': name,
                        'name_ru': self._generate_string('name_ru'),
                        'name_fr': self._generate_string('name_fr'),
                        'description': self._generate_string('description'),
                        'description_ru': self._generate_string('description_ru'),
                        'description_fr': self._generate_string('description_fr'),
                    }
                elif key == 'foods' or key == 'varietals':
                    result[key] = self._generate_list(value, depth)
                elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                    result[key] = self._generate_list(value, depth)
                elif isinstance(value, dict):
                    result[key] = self._generate_from_template(value, depth)
                elif value is False:
                    result[key] = self._generate_bool()
                elif value == 'string':
                    result[key] = self._generate_string(key)
                elif value == 'decimal':
                    result[key] = self._generate_decimal()
                elif value == 'integer':
                    result[key] = self._generate_integer()
                else:
                    result[key] = None
            return result

        return None

    def generate(self, template: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
        result = []
        for _ in range(count):
            item = self._generate_from_template(template)
            # Убедимся, что description > 200 символов
            for lang_key in ['description', 'description_ru', 'description_fr']:
                if lang_key in item:
                    while len(item[lang_key]) < 200:
                        faker = self.fakers[lang_key.split('_')[1]]
                        item[lang_key] += " " + " ".join(faker.sentences(nb=3))
                    item[lang_key] = item[lang_key][:500]  # ограничим длину
            result.append(item)
        return result
