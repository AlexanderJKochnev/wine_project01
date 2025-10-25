# tests/utility/assertion.py

def assertions(assertion: bool, failed_cases: list, router, prefix, text, *args) -> str:
    if assertion:
        error_message = f'{router.__name__}, ошибка {text}'
        failed_cases.append(error_message)
        return True
    return False
