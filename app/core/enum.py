# app.core.enum.py
from enum import Enum
from sqlalchemy import select
from app.core.config.database.db_sync import SessionLocalSync
from app.support import Category
from app.support.ollama.model import Prompt, Proption, ISOLanguage, WriterRule


# 3. Синхронная функция для получения списка строк
def fetch_all_startup_data() -> dict:
    data = {}
    # session.query(LlmModel.name)
    with SessionLocalSync() as session:
        # Запрос 1: Модели
        # models = session.scalars(select(Ollama.model).order_by(Ollama.model.asc())).all()
        # models = session.execute(text("SELECT name FROM llm_models")).scalars().all()
        # data['models'] = [m for m in models] or ["qwen3:8b"]
        # Запрос 2: Prompt
        prompts = session.scalars(select(Prompt.role).order_by(Prompt.role.asc())).all()
        data['prompts'] = [pr for pr in prompts] or ["translator"]

        # Запрос 3: Preset
        presets = session.scalars(select(Proption.preset).order_by(Proption.preset.asc())).all()
        data['presets'] = [c for c in presets] or ["balanced"]

        # Запрос 4: Languages
        language = session.scalars(select(ISOLanguage.name_en, ISOLanguage.iso_639_1).order_by(ISOLanguage.name_en.asc())).all()
        print(f'{language=}')
        data['language'] = [c for c, a in language] or ["Russian"]
        data['lang2'] = [a for c, a in language]

        # Запрос 5: WriterRules
        writer = session.scalars(select(WriterRule.name).order_by(WriterRule.name.asc())).all()
        data['writer'] = [c for c in writer] or ["translate"]

        # Запрос 6: Categories
        category = session.scalars(select(Category.name).order_by(Category.name.asc())).all()
        data['category'] = [c for c in category] or ["wine"]
    return data


# data вызовется автоматически при импорте модулей в main.py
data = fetch_all_startup_data()

Categories = Enum("category", {v: v for v in data['category']}, type=str)
Preset = Enum("Preset", {v: v for v in data['presets']}, type=str)
# LLmodel = Enum("Llmodel", {v: v for v in data['models']}, type=str)
Prompts = Enum("Prompts", {v: v for v in data['prompts']}, type=str)
Languages = Enum("Languages", {v: v for v in data['language']}, type=str)
Lang2 = Enum("Lang2", {v: v for v in data['lang2']}, type=str)
Writers = Enum("writer", {v: v for v in data['writer']}, type=str)
CliSearchMode = Enum("mode", {v: v for v in ['auto', 'ranked', 'word',
                     'and', 'or', 'phrase', 'fuzzy', 'fuzzy2', 'like']}, type=str)

rag = {"wine", "whisky", "beer", "spirits", "vodka", "gin", "schnapps",
       "brandy", "rum", "tequila", "ready-to-drink", "baijiu",
       "sparkling wine", "red wine", "white wine", "rose wine",
       "sake", "port", "ice wine", "dessert wines", "non-alcoholic wine",
       "sherry", "madeira", "champagne", "marsala", "vermouth", "orange wine",
       "pedro ximenez", "zinfandel", "fortified wine", "fruit wine", "chianti blend",
       "cachaca", "sangria", "mezcal", "absinthe", "soju", "ouzo", "grain alcohol",
       "aquavit", "aguardiente", "other"}
Rag_category = Enum('category', {v: v for v in sorted(rag)
                                 }, type=str)
Alignment = Enum('alignment', {v: v for v in ('center', 'left', 'right')}, type=str)
COLORS = {
    "WHITE_WINE": "#C1B495",
    "ROSE_WINE": "#A97E7A",
    "RED_WINE": "#822943",
    "BEER": "#8B2F48",
    "PORTO": "#471814",
    "SHAMPAIN": "#BEB3A1",
    "COGNAC": "#6F3729",
    "WHISKEY": "#AD802F",
    "VODKA": "#D9DEE4",
    "OTHER": "#8D314A"}

EXTENDED_COLORS = {
    "WHITE": "#FFFFFF",
    "BLACK": "#000000",
    "GRAY": "#898989",
    "RED": "#FF0000",
    "ORANGE": "#FFA500",
    "YELLOW": "#FFFF00",
    "YELLOW_GREEN": "#ADFF2F",
    "GREEN": "#00FF00",
    "LIME_GREEN": "#32CD32",
    "MINT": "#98FB98",
    "TEAL": "#008080",
    "CYAN": "#00FFFF",
    "LIGHT_BLUE": "#ADD8E6",
    "BLUE": "#0000FF",
    "ROYAL_BLUE": "#4169E1",
    "INDIGO": "#4B0082",
    "PURPLE": "#800080",
    "VIOLET": "#EE82EE",
    "MAGENTA": "#FF00FF",
    "HOT_PINK": "#FF69B4",
    "PINK": "#FFC0CB",
    "BROWN": "#A52A2A",
    "MAROON": "#800000",
    "OLIVE": "#808000",
    "NAVY": "#000080"
}

Color = Enum('color', {color: color for color in COLORS.keys()})

HANDBOOKS = {'countries': 'География. Страны, континенты',
             'regions': 'География. Страны и другие административные единицы.',
             'subregions': ('географические указания, аппелласьоны и регионы происхождения '
                            'в рамках международных классификаторов алкогольной и безалкогольной индустрии'),
             'sites': ('географические указания, аппелласьоны и регионы происхождения, отдельные винградники и '
                       'винокурни в рамках международных классификаторов алкогольной и безалкогольной индустрии'),
             'subcategories': 'Категории алкогольного и безалкогольных напитков',
             'foods': 'Продукты питания',
             'varietals': 'Сорта винограда',
             'baseingredients': 'Ингридиенты для производтсва алкогольных и безалкогольных напитков',
             'bodies': 'Дегустация. Виноделие.',
             'scales': '',
             'tastingnotes': 'Дегустация. Сравнительные вкусовые характеристики. Переводи строго как прилагательное'
             }
Handbooks = Enum('handbook', {handbook: handbook for handbook in HANDBOOKS.keys()})
# текстовые поля drink для перевода
DRINK_FIELD = {'description': 'описание напитка',
               'title': 'наименование напитак',
               'subtitle': 'дополнение к наименованию напитка, может содержать дополнительные признаки',
               'recommendation': 'рекомендации к употреблению напитка',
               'madeof': 'сырье для производства напитка',
               'display_name': 'полное наименовение напитка, включает производителя, регион, аппеласьон'}
Drinkfield = Enum('fieldname', {fieldname: fieldname for fieldname in DRINK_FIELD.keys()})

# image processing
IMAGE_PROCESSING = {'PNG: формат без сжатия, большой размер файла. Не оптимальный': 1,
                    'WEBP: старый вариант WEBP не поддерживает прозрачный фон': 2,
                    'WEBP LOSSLESS: WEBP без потерь, подходит для thumbnail и графики': 3,
                    'WEBP LOSSY: WEBP со сжатием, подходит для фотографий': 4
                    }
ImageProcessing = Enum('fieldname', {fieldname: fieldname for fieldname in IMAGE_PROCESSING.keys()})
