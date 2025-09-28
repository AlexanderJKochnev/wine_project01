# app.support.drink.service.py
from typing import Optional, Type

from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
from app.core.config.project_config import settings
from app.core.repositories.sqlalchemy_repository import Repository
from app.core.services.service import ModelType, Service
from app.core.utils.alchemy_utils import model_to_dict
from app.core.utils.common_utils import flatten_dict, get_path_to_root, jprint
from app.support.drink.drink_food_repo import DrinkFoodRepository
from app.support.drink.drink_varietal_repo import DrinkVarietalRepository
from app.support.drink.router import Drink, DrinkCreate, DrinkCreateRelations, DrinkRead, DrinkRepository
from app.support.food.router import (Food, FoodRepository, FoodService)
from app.support.subcategory.router import (Subcategory, SubcategoryRepository, SubcategoryService)
from app.support.subregion.router import (Subregion, SubregionRepository, SubregionService)
from app.support.sweetness.router import (Sweetness, SweetnessRepository, SweetnessService)
from app.support.varietal.router import (Varietal, VarietalRepository, VarietalService)
from app.core.utils.alchemy_utils import JsonConverter


class DrinkService(Service):
    """ переписываем методы для обрабоки manytomany relationships """

    @classmethod
    async def get_dict_by_id(cls, id: int, repository: Type[Repository],
                          model: ModelType, session: AsyncSession) -> Optional[ModelType]:
        result = await super().get_by_id(id, repository, model, session)
        # return result
        
        try:
            subresult = model_to_dict(result)
            flatresult = flatten_dict(subresult, ['name', 'name_ru'])
            for key, val in subresult.items():
                print(f'    {key}: {val}')
            for key, val in flatresult.items():
                print(f'    {key}: {val}')
            return flatresult
        except Exception as e:
            print(f'drink.service..get_by_id error {e}')
        # finally:
        #     return result
        

    @classmethod
    async def create_relation(cls, data: DrinkCreateRelations,
                              repository: DrinkRepository, model: Drink,
                              session: AsyncSession) -> DrinkRead:
        # pydantic model -> dict
        drink_data: dict = data.model_dump(exclude={'subregion', 'subcategory', 'color',
                                                    'sweetness', 'varietals', 'foods'},
                                           exclude_unset=True)
        if data.subregion:
            result = await SubregionService.create_relation(data.subregion, SubregionRepository,
                                                            Subregion, session)
            drink_data['subregion_id'] = result.id

        if data.subcategory:
            result = await SubcategoryService.create_relation(data.subcategory, SubcategoryRepository,
                                                              Subcategory, session)
            drink_data['subcategory_id'] = result.id

        if data.sweetness:
            result = await SweetnessService.get_or_create(data.sweetness, SweetnessRepository, Sweetness, session)
            drink_data['sweetness_id'] = result.id
        try:
            drink = DrinkCreate(**drink_data)
            drink_instance = await DrinkService.get_or_create(drink, DrinkRepository, Drink, session)
            drink_id = drink_instance.id
        except Exception as e:
            print(f'drink/service/create_relation:70 {e}==========================')
        if isinstance(data.foods, list):
            food_ids = []
            # 1. get_or_create foods in Food
            for item in data.foods:
                result = await FoodService.get_or_create(item, FoodRepository, Food, session)
                food_ids.append(result.id)
            # 2. set drink_food
            await DrinkFoodRepository.set_drink_foods(drink_id, food_ids, session)
        if isinstance(data.varietals, list):
            varietal_ids = []
            varietal_percentage = {}
            # 1. get_or_create varietals in Varietal
            # data.varietals is List[{varietal: VarietalCreateRelation
            #                         percentage: float}]
            for dvschema in data.varietals:
                item = dvschema.varietal
                percentage = dvschema.percentage
                result = await VarietalService.get_or_create(item, VarietalRepository, Varietal, session)
                varietal_percentage[result.id] = percentage
                varietal_ids.append(result.id)
            # 2. set drink_varietal
            await DrinkVarietalRepository.set_drink_varietals(drink_id, varietal_ids, session)
            # 3. set up percentage
            for key, val in varietal_percentage.items():
                pass
                await DrinkVarietalRepository.update_percentage(drink_id, key, val, session)
        return drink_instance

    @classmethod
    async def direct_upload(cls, filename:str, session: AsyncSession) -> dict:
        try:
            # получаем путь к файлу
            upload_dir = settings.UPLOAD_DIR
            dirpath: Path = get_path_to_root(upload_dir)
            filepath = dirpath / filename
            if not filepath.exists():
                raise Exception(f'file {filename} is not exists in {upload_dir}')
            # загружаем jsno файл, конвертируем в формат relation и собираем в список:
            dataconv: list = list(JsonConverter(filepath)().values())
            # проходим по списку и загружаем в postgresql
            for n, item in enumerate(dataconv):
                try:
                    data_model = DrinkCreateRelations(**item)
                    result = await cls.create_relation(data_model, DrinkRepository, Drink, session)
                except Exception as e:
                    raise Exception(f'data_model:: {e}')
            return {'filepath': len(dataconv)}
        except Exception as e:
            raise Exception(f'drink.service.direct_upload.error: {e}')
"""
    async def create_relation(cls, data: DrinkCreateRelations,
                              repository: DrinkRepository, model: Drink,
                              session: AsyncSession) -> DrinkRead:

"""