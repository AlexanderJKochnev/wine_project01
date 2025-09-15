# app.support.item.service.py
from app.core.services.service import Service
from app.support.item.router import Item, ItemCreate, ItemCreateRelations, ItemRepository, ItemRead, AsyncSession
from app.support.drink.router import DrinkService, DrinkRepository, Drink
from app.support.warehouse.router import Warehouse, WarehouseService, WarehouseRepository


class ItemService(Service):

    @classmethod
    async def create_relation(cls, data: ItemCreateRelations,
                              repository: ItemRepository, model: Item,
                              session: AsyncSession) -> ItemRead:

        item_data: dict = data.model_dump(exclude={'drink', 'warehouse'},
                                          exclude_unset=True)
        if data.drink:
            result = await DrinkService.create_relation(data.drink, DrinkRepository, Drink, session)
            item_data['drink_id'] = result.id
        if data.warehouse:
            result = await WarehouseService.create_relation(data.warehouse, WarehouseRepository,
                                                            Warehouse, session)
            item_data['warehouse_id'] = result.id
        item = ItemCreate(**item_data)
        item_instance = await ItemService.get_or_create(item, ItemRepository, Item, session)
        return item_instance
