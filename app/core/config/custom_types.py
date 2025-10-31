from typing import List, Any
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
import json


def ListField(delimiter: str = ',') -> Any:
    """
    Фабрика для создания кастомных типов списков с указанным разделителем
    """
    class DelimitedList(List[str]):
        @classmethod
        def __get_pydantic_core_schema__(
                cls, _source_type: Any, _handler: GetCoreSchemaHandler, ) -> core_schema.CoreSchema:
            def validate(value: Any) -> List[str]:
                if isinstance(value, list):
                    return value
                if isinstance(value, str):
                    if value.strip().startswith('[') and value.strip().endswith(']'):
                        try:
                            return json.loads(value)
                        except json.JSONDecodeError:
                            pass
                    return [item.strip() for item in value.split(delimiter) if item.strip()]
                # raise ValueError(f"Cannot parse {value} as list")

            return core_schema.list_schema()
    return DelimitedList
