# app/support/drink/services/drink_varietal_service.py
from typing import List

from app.support.drink.drink_varietal_repo import DrinkVarietalRepository


class DrinkVarietalService:
    def __init__(self, repo: DrinkVarietalRepository):
        self.repo = repo

    async def get_drink_varietals_str(self, drink_id: int) -> List[str]:
        drink = await self.repo.get_drink_with_varietals(drink_id)
        if not drink:
            return []
        return [varietal.__str__() for varietal in drink.varietals]

    async def get_varietal_drinks_str(self, varietal_id: int) -> List[str]:
        varietal = await self.repo.get_varietal_with_drinks(varietal_id)
        if not varietal:
            return []
        return [drink.__str__() for drink in varietal.drinks]

    async def link_varietal_to_drink(self, drink_id: int, varietal_id: int, priority: int = 0):
        return await self.repo.add_varietal_to_drink(drink_id, varietal_id, priority)

    async def unlink_varietal_from_drink(self, drink_id: int, varietal_id: int):
        return await self.repo.remove_varietal_from_drink(drink_id, varietal_id)

    async def update_link_priority(self, drink_id: int, varietal_id: int, priority: int):
        return await self.repo.update_priority(drink_id, varietal_id, priority)

    async def set_drink_varietals(self, drink_id: int, varietal_ids: List[int]):
        return await self.repo.set_drink_varietals(drink_id, varietal_ids)
