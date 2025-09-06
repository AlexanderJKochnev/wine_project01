# app.support.drink.service.py
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.services.service import ModelType, Service
from app.core.utils.alchemy_utils import model_to_dict
from app.core.utils.common_utils import flatten_dict


class DrinkService(Service):
    """ переписываем методы для обрабоки manytomany relationships """

    async def get_by_id(self, id: int, session: AsyncSession) -> Optional[ModelType]:
        result = await super().get_by_id(id, session)
        subresult = model_to_dict(result)
        flatresult = flatten_dict(subresult, ['name', 'name_ru'])
        print(f'{subresult}')
        for key, val in subresult.items():
            print(f'    {key}: {val}')
        print('-------------------')
        for key, val in flatresult.items():
            print(f'    {key}: {val}')
        return result
