# app/core/schemas/lang_schemas.py
from pydantic import computed_field
from app.core.schemas.base import ListView, DetailView
"""
    языковые pydantic модели для справочников
    добавлять по мере появления языков
"""


class ListViewEn(ListView):
    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        return self.name or self.name_ru or self.name_fr or ""


class DetailViewEn(DetailView):
    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        return self.name or self.name_ru or self.name_fr or ""

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_description(self) -> str:
        return self.description or self.description_ru or self.description_fr or ""


class ListViewRu(ListView):
    @computed_field(description='Наименование',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        return self.name_ru or self.name or self.name_fr or ""


class DetailViewRu(DetailView):
    @computed_field(description='Наименование',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        return self.name_ru or self.name or self.name_fr or ""

    @computed_field(description='Описание',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_description(self) -> str:
        return self.description_ru or self.description or self.description_fr or ""


class ListViewFr(ListView):
    @computed_field(description='Nom',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        return self.name_fr or self.name or self.name_ru or ""


class DetailViewFr(DetailView):
    @computed_field(description='Nom',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        return self.name_ru or self.name or self.name_fr or ""

    @computed_field(description='Description',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_description(self) -> str:
        return self.description_fr or self.description or self.description_ru or ""
