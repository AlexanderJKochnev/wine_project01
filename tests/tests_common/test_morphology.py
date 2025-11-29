# tests/test_morphology.py
from app.core.utils.morphology import to_nominative


def test_to_nominative():
    data = ["с сухофруктами",
            "с блюдами на гриле",
            "из реки",
            "пирожками"]
    expected = ["сухофрукты",
                "блюда на гриле",
                "река",
                "пирожки"]
    for n, item in enumerate(data):
        result = to_nominative(item)
        print(result, '   ', expected[n])
        assert result == expected[n], f'{item} is not equal {expected[n]}'
