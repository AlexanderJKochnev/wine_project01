# app.support.drink.service.py
from typing import Optional, Type

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repositories.sqlalchemy_repository import Repository
from app.core.services.service import ModelType, Service
from app.core.utils.alchemy_utils import model_to_dict
from app.core.utils.common_utils import flatten_dict
# from app.support.color.router import Color, ColorRepository, ColorService
from app.support.drink.drink_food_repo import DrinkFoodRepository
from app.support.drink.drink_varietal_repo import DrinkVarietalRepository
from app.support.drink.router import Drink, DrinkCreate, DrinkCreateRelations, DrinkRead, DrinkRepository
from app.support.food.router import (Food, FoodRepository, FoodService)
from app.support.subcategory.router import (Subcategory, SubcategoryRepository, SubcategoryService)
from app.support.subregion.router import (Subregion, SubregionRepository, SubregionService)
from app.support.sweetness.router import (Sweetness, SweetnessRepository, SweetnessService)
from app.support.varietal.router import (Varietal, VarietalRepository, VarietalService)


class DrinkService(Service):
    """ переписываем методы для обрабоки manytomany relationships """

    @classmethod
    async def __get_by_id(cls, id: int, repository: Type[Repository],
                        model: ModelType, session: AsyncSession) -> Optional[ModelType]:
        result = await super().get_by_id(id, repository, model, session)
        return result
        try:
            subresult = model_to_dict(result)
            flatresult = flatten_dict(subresult, ['name', 'name_ru'])
            for key, val in subresult.items():
                print(f'    {key}: {val}')
            for key, val in flatresult.items():
                print(f'    {key}: {val}')
        except Exception as e:
            print(f'drink.service..get_by_id error {e}')
        finally:
            return result

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
            print(f'============subregion {result.id}')
        if data.subcategory:
            result = await SubcategoryService.create_relation(data.subcategory, SubcategoryRepository,
                                                              Subcategory, session)
            drink_data['subcategory_id'] = result.id
            print(f'============subcategory {result.id}')
        # if data.color:
        #     result = await ColorService.get_or_create(data.color, ColorRepository, Color, session)
        #     drink_data['color_id'] = result.id
        if data.sweetness:
            result = await SweetnessService.get_or_create(data.sweetness, SweetnessRepository, Sweetness, session)
            drink_data['sweetness_id'] = result.id
            print(f'============sweetness {result.id}')
        drink = DrinkCreate(**drink_data)
        drink_instance = await DrinkService.get_or_create(drink, DrinkRepository, Drink, session)
        drink_id = drink_instance.id
        # =============manytomany case==============
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
            print(f'======================={type(varietal_percentage)=}')
            for key, val in varietal_percentage.items():
                await DrinkVarietalRepository.update_percentage(drink_id, key, val, session)
        return drink_instance
