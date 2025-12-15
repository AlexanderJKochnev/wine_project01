# app/core/utils/exception_handler.py
from app.core.utils.common_utils import jprint


def ValidationError_handler(exc):
    """
        обработка и вывод информации об ошибке
        ValidationError
    """
    result: dict = {}
    for error in exc.errors():
        result['head'] = "Ошибка валидации"
        result['Место ошибки (loc)'] = f"{error['loc']}"
        result['Сообщение (msg)'] = f"{error['loc']}"
        result['Тип ошибки (type)'] = f"{error['type']}"
        result['Некорректное значение (input_value)'] = "{error['input_value']}"
    jprint(result)
    return result