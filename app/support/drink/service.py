# app.support.drink.service.py
from typing import Optional, Type

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repositories.sqlalchemy_repository import Repository
from app.core.services.service import ModelType, Service
from app.core.utils.alchemy_utils import model_to_dict
from app.core.utils.common_utils import flatten_dict

from app.support.drink.drink_food_repo import DrinkFoodRepository
from app.support.drink.drink_varietal_repo import DrinkVarietalRepository
from app.support.drink.model import Drink
from app.support.drink.schemas import DrinkCreate, DrinkCreateRelation, DrinkRead
from app.support.drink.repository import DrinkRepository

from app.support.food.service import FoodService
from app.support.food.repository import FoodRepository

from app.support.subcategory.model import Subcategory
from app.support.subcategory.repository import SubcategoryRepository
from app.support.subcategory.service import SubcategoryService

from app.support.subregion.model import Subregion
from app.support.subregion.repository import SubregionRepository
from app.support.subregion.service import SubregionService

from app.support.sweetness.model import Sweetness
from app.support.sweetness.repository import SweetnessRepository
from app.support.sweetness.service import SweetnessService


from app.support.varietal.model import Varietal
from app.support.varietal.repository import VarietalRepository
from app.support.varietal.service import VarietalService


class DrinkService(Service):
    """ переписываем методы для обрабоки manytomany relationships """
    __abstract__ = False
    default = ['title', 'subtitle']

    @classmethod
    async def get_dict_by_id(cls, id: int, repository: Type[Repository],
                             model: ModelType, session: AsyncSession) -> Optional[ModelType]:
        result = await super().get_by_id(id, repository, model, session)
        # return result

        try:
            subresult = model_to_dict(result)
            flatresult = flatten_dict(subresult, ['name', 'name_ru'])
            for key, val in subresult.items():
                pass
                # print(f'1.    {key}: {val}')
            for key, val in flatresult.items():
                pass
                # print(f'2.    {key}: {val}')
            return flatresult
        except Exception as e:
            print(f'drink.service..get_by_id error {e}')

    @classmethod
    async def create_relation(cls, data: DrinkCreateRelation,
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
            result, _ = await SweetnessService.get_or_create(data.sweetness, SweetnessRepository, Sweetness, session)
            drink_data['sweetness_id'] = result.id
        try:
            drink = DrinkCreate(**drink_data)
            drink_instance, _ = await cls.get_or_create(drink, DrinkRepository, Drink, session)
            drink_id = drink_instance.id
        except Exception as e:
            print(f'drink/service/create_relation:70 {e}==========================')
        if isinstance(data.foods, list):
            food_ids = []
            # 1. get_or_create foods in Food
            for item in data.foods:
                result = await FoodService.create_relation(item, FoodRepository, FoodService, session)
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
                result, _ = await VarietalService.get_or_create(item, VarietalRepository, Varietal, session)
                varietal_percentage[result.id] = percentage
                varietal_ids.append(result.id)
            # 2. set drink_varietal
            await DrinkVarietalRepository.set_drink_varietals(drink_id, varietal_ids, session)
            # 3. set up percentage
            for key, val in varietal_percentage.items():
                await DrinkVarietalRepository.update_percentage(drink_id, key, val, session)
        await session.refresh(drink_instance)
        return drink_instance
