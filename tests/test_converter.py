from app.core.utils.converters import convert_dict1_to_dict2  # , convert_dict2_to_dict1
from app.core.utils.io_utils import get_filepath_from_dir_by_name, readJson
from app.core.utils.common_utils import jprint
from app.support.item.schemas import ItemCreateRelation, DrinkCreateRelation  # noqa: F401


def test_convers():
    filepath = get_filepath_from_dir_by_name('test.json')
    dict1 = readJson(filepath)
    assert isinstance(dict1, dict), type(dict1)
    convers = convert_dict1_to_dict2(dict1)
    assert isinstance(convers, dict), type(convers)
    # jprint(convers)
    # assert False
    for key, val in convers.items():
        try:
            model = ItemCreateRelation(**val)
            back_dict = model.model_dump()
            assert val == back_dict
        except Exception as e:
            jprint(val)
            print(e)
            assert False
