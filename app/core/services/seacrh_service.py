# app/core/service/search_service.py
# services/search_service.py
from typing import List, Dict, Any, Type
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repositories.search_repository import SearchRepository, BaseModel
from app.core.schemas.search_model import TextSearchRequest
from app.core.exceptions import DatabaseException, ValidationException, NotFoundException


class SearchService:
    def __init__(self, db_session: AsyncSession):
        self.repository = SearchRepository(db_session)
    
    async def search_records(
            self, model: Type[BaseModel], search_request: TextSearchRequest
            ) -> Dict[str, Any]:
        """
        Поиск записей по текстовым полям

        Args:
            model: Модель для поиска
            search_request: Параметры поиска

        Returns:
            Dict с результатами поиска

        Raises:
            ValidationException: Ошибки валидации
            DatabaseException: Ошибки БД
            NotFoundException: Записи не найдены
        """
        try:
            # Поиск записей
            records = await self.repository.text_search(
                    model = model, search_fields = search_request.search_fields,
                    search_type = search_request.search_type, case_sensitive = search_request.case_sensitive,
                    limit = search_request.limit, offset = search_request.offset
                    )
            
            # Если записей не найдено
            if not records:
                raise NotFoundException(
                        message = "Записи по указанным критериям не найдены",
                        details = {"search_criteria": search_request.dict(), "model": model.__name__},
                        suggestion = "Попробуйте изменить параметры поиска или использовать другой тип поиска"
                        )
            
            # Подсчет общего количества для пагинации
            total_count = await self.repository.count_text_search(
                    model = model, search_fields = search_request.search_fields,
                    search_type = search_request.search_type, case_sensitive = search_request.case_sensitive
                    )
            
            # Формирование ответа
            return self._format_response(records, total_count, search_request)
        
        except (ValidationException, DatabaseException, NotFoundException):
            raise
        except Exception as e:
            raise DatabaseException(
                    message = "Неожиданная ошибка при выполнении поиска",
                    details = {"error_type": type(e).__name__, "model": model.__name__}
                    )
    
    def _format_response(self, records: List[BaseModel], total_count: int, search_request: TextSearchRequest) -> Dict[
        str, Any]:
        """Форматирование ответа"""
        # Конвертация записей в словари
        records_data = []
        for record in records:
            record_dict = {}
            for column in record.__table__.columns:
                record_dict[column.name] = getattr(record, column.name)
            records_data.append(record_dict)
        
        # Информация о пагинации
        pagination = None
        if search_request.limit is not None:
            pagination = {"limit": search_request.limit, "offset": search_request.offset or 0, "total": total_count,
                    "has_more": (search_request.offset or 0) + len(records) < total_count}
        
        return {"data": records_data, "total": total_count, "pagination": pagination}
