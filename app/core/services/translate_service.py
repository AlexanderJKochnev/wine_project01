# app.core.services.translate_service.py
import asyncio
import itertools
import time
import re
from typing import Dict, Any, List, Tuple
from openai import AsyncOpenAI
from loguru import logger  # noqa: F401


class TranslationService:
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url='http://vllm-node:8000/v1/', api_key="token-not-needed"
        )
        # Имя модели должно совпадать с тем, как она примонтирована/названа в vLLM
        self.model_name = "/model"
        self.lang_map = {'ru': 'Russian', 'en': 'English', 'de': 'German', 'fr': 'French', 'es': 'Spanish',
                         'it': 'Italian', 'zh': 'Chinese', 'ja': 'Japanese'}

    def _build_messages(self, system_prompt: str, user_prompt: str, lang_code: str, phrase: str,
                        drink: str) -> list:
        """
        Формирует структурированный массив сообщений для Chat Completions API.
        vLLM автоматически применит к нему ChatML шаблоны для Qwen.
        """
        if len(lang_code) == 2:
            target_lang = self.lang_map.get(lang_code[:2], 'German')
        else:
            target_lang = lang_code

        system_content = system_prompt.format(lang=target_lang)
        user_content = user_prompt.format(lang=target_lang, phrase=phrase, drink=drink)

        return [{"role": "system", "content": system_content}, {"role": "user", "content": user_content}]

    def _prepare_params(self, **kwargs) -> Dict[str, Any]:
        """Подготавливает параметры для vLLM (Chat Completions)"""
        # Для точного перевода терминов виноделия рекомендую держать температуру 0.1-0.2
        params = {"model": self.model_name, "temperature": kwargs.get('temperature', 0.1),
                  "top_p": kwargs.get('top_p', 0.85), "max_tokens": kwargs.get('max_tokens', 2048),
                  "frequency_penalty": kwargs.get('frequency_penalty', 0.2),
                  "presence_penalty": kwargs.get('presence_penalty', 0.1), "seed": kwargs.get('seed', 42), }

        # extra_body для продвинутых параметров vLLM
        extra_body = {}

        if (top_k := kwargs.get('top_k', 50)) > 0:
            extra_body['top_k'] = top_k

        # Qwen хорошо реагирует на repetition_penalty (в OpenAI SDK это часто передается в extra_body)
        if (repetition_penalty := kwargs.get('repetition_penalty', kwargs.get('repeat_penalty', 1.1))) != 1.1:
            extra_body['repetition_penalty'] = repetition_penalty

        if (min_p := kwargs.get('min_p', 0.04)) != 0.04:
            extra_body['min_p'] = min_p

        if (typical_p := kwargs.get('typical_p', 0.92)) != 0.92:
            extra_body['typical_p'] = typical_p

        if kwargs.get('stop'):
            params['stop'] = kwargs['stop']

        if extra_body:
            params['extra_body'] = extra_body

        return params

    async def translate(
            self, phrase: str, system_prompt: str, user_prompt: str, lang: str,
            drink: str,
            **params
    ) -> Dict[str, Any]:
        """Основной метод перевода, адаптированный под Qwen (Chat API)"""
        start_ms = time.time() * 1000
        # упрощаем phrase
        # phrase = pre_process_wine_text(phrase)
        # Вместо текстовой строки генерируем массив ролей (System / User)
        messages = self._build_messages(system_prompt, user_prompt, lang, phrase, drink)
        request_params = self._prepare_params(**params)
        request_params["messages"] = messages

        gpu_start = time.time() * 1000

        # Вызываем chat.completions вместо completions
        response = await self.client.chat.completions.create(**request_params)

        gpu_end_ms = time.time() * 1000
        gpu_duration_sec = (gpu_end_ms - gpu_start) / 1000
        total_duration_sec = (gpu_end_ms - start_ms) / 1000

        completion_tokens = response.usage.completion_tokens

        return {"system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "original": phrase,  # Изменился парсинг ответа: теперь текст лежит в .message.content
                "content": response.choices[0].message.content.strip(),
                "performance": {"total_sec": total_duration_sec, "gpu_s": gpu_duration_sec, "tokens": completion_tokens,
                                "speed_tok_per_sec": round(
                                    completion_tokens / max(gpu_duration_sec, 0.001), 1
                                )},
                "params": params
                }

    async def _translate_single_task(
            self, semaphore: asyncio.Semaphore, p_id: int, phrase: str, s_id: int, s_prompt: str, u_id: int,
            u_prompt: str, lang: str, drink: str, single_params: dict
    ) -> Dict[str, Any]:
        """Обработка одной конкретной комбинации параметров и текстов"""
        messages = self._build_messages(s_prompt, u_prompt, lang, phrase, drink)
        request_params = self._prepare_params(**single_params)
        request_params["messages"] = messages
        try:
            async with semaphore:
                start_time = time.time()
                response = await self.client.chat.completions.create(**request_params)
                duration_s = time.time() - start_time
                content = response.choices[0].message.content.strip()
        except Exception as e:
            # Фиксируем ошибку, чтобы не ломать весь batch insert в БД
            content = f"ERROR: {str(e)}"
        return {'drink_id': p_id,
                'lang_origin': f'{drink=}',
                'lang_result': lang,
                'prompt_id': s_id,
                'writerrule_id': u_id,
                'proption_id': single_params.get('id'),
                'result': content,
                'duration': round(duration_s, 4)}

    async def translate_batch(
            self, phrases: List[Tuple[int, str]], system_prompts: List[Tuple[int, str]],
            user_prompts: List[Tuple[int, str]], params: List[dict], lang: str, drink: str,
            max_concurrent_requests: int = 128
    ) -> List[Dict[str, Any]]:
        """
        Метод группового перевода всех комбинаций (Декартово произведение).
        Порядок обхода: system_prompt -> param -> phrase -> user_prompt
        """
        semaphore = asyncio.Semaphore(max_concurrent_requests)
        results = []
        total_tasks = len(system_prompts) * len(params) * len(phrases) * len(user_prompts)
        remain_tasks = total_tasks
        logger.info(f"Запуск перевода. Всего комбинаций: {total_tasks}")
        start_time = time.time()
        for s_id, s_prompt in system_prompts:
            for single_params in params:
                # Для конкретного системного промпта и параметров собираем пачку задач
                group_tasks = []
                # Внутренние циклы выполняются конкурентно (у них общие s_prompt и params)
                for c, (p_id, phrase) in enumerate(phrases):
                    for u_id, u_prompt in user_prompts:
                        task = self._translate_single_task(
                            semaphore, p_id, phrase, s_id, s_prompt, u_id, u_prompt, lang, drink, single_params,
                        )
                        group_tasks.append(task)
                        remain_tasks -= 1
                # Ждем выполнение текущей группы. vLLM считает s_prompt ОДИН раз для всей группы
                group_results = await asyncio.gather(*group_tasks)
                duration_s = time.time() - start_time
                logger.info(f'обработано {total_tasks - remain_tasks} записей из {total_tasks} за {duration_s} сек')
                results.extend(group_results)
        logger.success(f"Перевод завершен. Успешно обработано {total_tasks} записей.")
        return results


def pre_process_wine_text(text):
    # Глобальный статический глоссарий "Мин и Калек"
    # Мы заменяем абстрактные идиомы на их простые английские аналоги ДУМАТЬ КАК 8B МОДЕЛЬ
    wine_glossary = {  # 1. Текстура и танины (Самый частый сбой моделей)
        r"\bmouthfeel\b": "texture", r"\bpalate\b": "taste structure",
        r"\bfine-grained tannins\b": "smooth fine tannins", r"\bvelveteen tannins\b": "velvety tannins",
        r"\btaut tannins\b": "firm strict tannins", r"\bchewy tannins\b": "dense heavy tannins",

        # 2. Фрукты и Специи (Защита от клюквы и яблок)
        r"\bPlummy\b": "Rich with notes of plum", r"\bplummy\b": "with notes of plum",
        r"\bblack cherry\b": "dark sweet cherry",  # Ликвидируем триггер слова Cherry
        r"\bBlack cherry\b": "Dark sweet cherry", r"\bstone fruits\b": "stone fruits like peaches",
        # Подсказка в скобках
        r"\bstone fruit\b": "stone fruit like peach", r"\bwild berries\b": "forest berries",
        r"\bkicks of pepper\b": "hints of pepper",

        # 3. Бочка, выдержка и дефекты перевода
        r"\bchar\b": "smoky oak notes",  # Защита от перевода "ЖАР"
        r"\bmaturation\b": "barrel aging", r"\bnew French oak\b": "new French oak barrels",
        r"\bcandied citrus\b": "sweet candied citrus",  # Защита от "вареного цитруса"
        r"\bfinish\b": "aftertaste",  # Намертво вырезаем "финал/finale"
        r"\bthis wine\b": "this high-quality wine", r"\bthis effort\b": "this wine production", }
    # Применяем автозамену с сохранением регистра (для начала предложений)
    for pattern, replacement in wine_glossary.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text
