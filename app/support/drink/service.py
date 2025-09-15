# app.support.drink.service.py
from typing import Optional, Type

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repositories.sqlalchemy_repository import Repository
from app.core.services.service import ModelType, Service
from app.core.utils.alchemy_utils import model_to_dict
from app.core.utils.common_utils import flatten_dict
from app.support.category.router import (Category, CategoryRepository, CategoryService)
from app.support.color.router import Color, ColorRepository, ColorService
from app.support.country.router import Country, CountryRepository, CountryService
from app.support.drink.drink_food_repo import DrinkFoodRepository
from app.support.drink.drink_varietal_repo import DrinkVarietalRepository
from app.support.drink.router import Drink, DrinkCreate, DrinkCreateRelations, DrinkRead, DrinkRepository
from app.support.food.router import (Food, FoodRepository, FoodService)
from app.support.region.router import (Region, RegionCreate, RegionRepository, RegionService)
from app.support.subregion.router import (Subregion, SubregionCreate, SubregionRepository, SubregionService)
from app.support.sweetness.router import (Sweetness, SweetnessRepository, SweetnessService)
from app.support.varietal.router import (Varietal, VarietalRepository, VarietalService)


class DrinkService(Service):
    """ переписываем методы для обрабоки manytomany relationships """

    @classmethod
    async def get_by_id(cls, id: int, repository: Type[Repository],
                        model: ModelType, session: AsyncSession) -> Optional[ModelType]:
        result = await super().get_by_id(id, repository, model, session)
        subresult = model_to_dict(result)
        flatresult = flatten_dict(subresult, ['name', 'name_ru'])
        for key, val in subresult.items():
            pass
            # print(f'    {key}: {val}')
        for key, val in flatresult.items():
            pass
            # print(f'    {key}: {val}')
        return result

    @classmethod
    async def create_relation(cls, data: DrinkCreateRelations,
                              repository: DrinkRepository, model: Drink,
                              session: AsyncSession) -> DrinkRead:
        # pydantic model -> dict
        drink_data: dict = data.model_dump(exclude={'subregion', 'category', 'color',
                                                    'sweetness', 'varietals', 'foods'},
                                           exclude_unset=True)
        if data.subregion:
            subregion_data: dict = data.subregion.model_dump(exclude={'region'}, exclude_unset=True)
            if data.subregion.region:
                region_data: dict = data.subregion.region.model_dump(exclude={'country'}, exclude_unset=True)
                if data.subregion.region.country:
                    result = await CountryService.get_or_create(data.subregion.region.country,
                                                                CountryRepository, Country, session)
                    region_data['country_id'] = result.id
                    region = RegionCreate(**region_data)
                    result = await RegionService.get_or_create(region, RegionRepository, Region, session)
                    subregion_data['region_id'] = result.id
                    subregion = SubregionCreate(**subregion_data)
                    result = await SubregionService.get_or_create(subregion, SubregionRepository, Subregion, session)
                    drink_data['subregion_id'] = result.id
        if data.category:
            result = await CategoryService.get_or_create(data.category, CategoryRepository, Category, session)
            drink_data['category_id'] = result.id
        if data.color:
            result = await ColorService.get_or_create(data.color, ColorRepository, Color, session)
            drink_data['color_id'] = result.id
        if data.sweetness:
            result = await SweetnessService.get_or_create(data.sweetness, SweetnessRepository, Sweetness, session)
            drink_data['sweetness_id'] = result.id

        drink = DrinkCreate(**drink_data)
        drink_instance = await DrinkService.get_or_create(drink, DrinkRepository, Drink, session)
        drink_id = drink_instance.id
        # =============manytomany case==============
        if data.foods:
            food_ids = []
            # 1. get_or_create foods in Food
            for item in data.foods:
                result = await FoodService.get_or_create(item, FoodRepository, Food, session)
                food_ids.append(result.id)
            # 2. set drink_food
            await DrinkFoodRepository.set_drink_foods(drink_id, food_ids, session)
        if data.varietals:
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
                await DrinkVarietalRepository.update_percentage(drink_id, key, val, session)
        return drink_instance
