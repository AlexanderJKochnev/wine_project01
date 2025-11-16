from app.core.utils.alchemy_utils import JsonConverter
from app.core.utils.io_utils import get_filepath_from_dir_by_name
from app.mongodb.service import ImageService
from app.core.utils.common_utils import jprint


def test_jsonconverter():
    """ тестируем JsonConverter
        data_2.json 149
        data.json   148
        data_old.json 139
    """
    # error_list: list = []
    # image_list = await image_service.get_images_list_after_date()
    filepath = get_filepath_from_dir_by_name('data_2.json')
    # получаем список кортежей (image_name, image_id)
    # загружаем json файл, конвертируем в формат relation и собираем в список:
    dataconv: list = list(JsonConverter(filepath)().values())
    for n, key in enumerate(dataconv):
        jprint(key)
        print(f'{n}--------------')
    assert False
