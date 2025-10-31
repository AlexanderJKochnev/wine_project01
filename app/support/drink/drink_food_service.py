# app/support/drink/services/drink_food_service.py
from typing import List

from app.support.drink.drink_food_repo import DrinkFoodRepository


class DrinkFoodService:
    def __init__(self, repo: DrinkFoodRepository):
        self.repo = repo

    async def get_drink_foods_str(self, drink_id: int) -> List[str]:
        drink = await self.repo.get_drink_with_foods(drink_id)
        if not drink:
            return []
        return [food.__str__() for food in drink.foods]

    async def get_food_drinks_str(self, food_id: int) -> List[str]:
        food = await self.repo.get_food_with_drinks(food_id)
        if not food:
            return []
        return [drink.__str__() for drink in food.drinks]

    async def link_food_to_drink(self, drink_id: int, food_id: int, priority: int = 0):
        return await self.repo.add_food_to_drink(drink_id, food_id, priority)

    async def unlink_food_from_drink(self, drink_id: int, food_id: int):
        return await self.repo.remove_food_from_drink(drink_id, food_id)

    async def update_link_priority(self, drink_id: int, food_id: int, priority: int):
        return await self.repo.update_priority(drink_id, food_id, priority)

    async def set_drink_foods(self, drink_id: int, food_ids: List[int]):
        return await self.repo.set_drink_foods(drink_id, food_ids)
