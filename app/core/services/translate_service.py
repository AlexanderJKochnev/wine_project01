# app.core.services.translate_service.py
import asyncio
import json
import time
from typing import Dict, Any, List, Tuple

import httpx
from openai import AsyncOpenAI
from loguru import logger  # noqa: F401

from app.core.utils.common_utils import jprint, replaceX
from app.support.vllm.dataclasses import DrinkTranslateData, HandbookTranslateData

from abc import ABC, abstractmethod
from typing import Optional


class BaseService(ABC):
    """Базовый класс для всех сервисов"""

    def __init__(self):
        self._closed = False
        self.http_client: Optional[httpx.AsyncClient] = None

    @abstractmethod
    async def initialize(self):
        """Инициализация сервиса (создание клиентов и т.д.)"""
        pass

    @abstractmethod
    async def close(self):
        """Закрытие ресурсов"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Проверка работоспособности сервиса"""
        pass

    def is_closed(self) -> bool:
        return self._closed


class TranslationService(BaseService):
    def __init__(self, config: dict = None):
        super().__init__()
        self.config = config or {}
        self.client = None
        self.model_name = self.config.get("model", "/model")
        self.lang_map = {'ru': 'Russian', 'en': 'English', 'de': 'German', 'fr': 'French', 'es': 'Spanish',
                         'it': 'Italian', 'zh': 'Chinese', 'ja': 'Japanese'}

    async def initialize(self):
        """Инициализация сервиса"""
        if self.http_client is None:
            self.http_client = httpx.AsyncClient(
                limits=httpx.Limits(
                    max_keepalive_connections=5, max_connections=10, keepalive_expiry=30.0
                ), timeout=httpx.Timeout(60.0, connect=10.0), http2=False
            )

        self.client = AsyncOpenAI(
            base_url=self.config.get("base_url", "http://vllm-node:8000/v1/"), api_key="token-not-needed",
            http_client=self.http_client, max_retries=0
        )
        return self

    async def close(self):
        """Закрытие ресурсов"""
        if not self._closed and self.http_client:
            await self.http_client.aclose()
            self._closed = True

    async def health_check(self) -> bool:
        """Проверка работоспособности"""
        try:
            # Простой пинг
            return self.client is not None
        except Exception:
            return False

    def _build_messages(self, system_prompt: str, user_prompt: str, lang_code: str, phrase: str,
                        drink: str = None, hints: dict = None) -> list:
        """
        Формирует структурированный массив сообщений для Chat Completions API.
        vLLM автоматически применит к нему ChatML шаблоны для Qwen.
        """
        hints_str = ""
        if hints:
            lines = []
            for word, translation_set in hints.items():
                # Превращаем {'вариант1', 'вариант2'} в строку "вариант1" или "вариант2"
                variants = ", ".join(f"'{t}'" for t in sorted(translation_set))
                # Формируем строчку по стилю вашего промпта
                lines.append(f"\n- Слово или фразу '{word.lower()}' переводи как {variants.lower()}.")

            # Склеиваем все найденные подсказки
            hints_str = "".join(lines)

        target_lang = lang_code
        system_prompt = system_prompt.format(lang=target_lang)
        user_prompt = user_prompt.format(lang=target_lang, phrase=phrase, drink=drink, translation_hints=hints_str)
        # ВНИМАНИЕ КОСТЫЛЬ - В КОНЦЕ user_prompt ДОПИСЫВАЕМ ВОЛШЕБНОЕ ЗАКЛИНАНИЕ (если оно есть)
        # if not user_prompt.endswith(self.hang):
        #     user_prompt = f'{user_prompt}. {self.hang}'
        return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

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
        logger.warning(f'{messages=}')
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
            u_prompt: str, lang: str, drink: str, single_params: dict, translation_hint: dict
    ) -> Dict[str, Any]:
        """Обработка одной конкретной комбинации параметров и текстов"""
        messages = self._build_messages(s_prompt, u_prompt, lang, phrase, drink, translation_hint)
        logger.warning(messages)
        request_params = self._prepare_params(**single_params)
        request_params["messages"] = messages
        try:
            async with semaphore:
                # start_time = time.time()
                response = await self.client.chat.completions.create(**request_params)
                # duration_s = time.time() - start_time
                content = response.choices[0].message.content.strip()
                # В КОНЦЕ user_prompt УБИРАЕМ ВОЛШЕБНОЕ ЗАКЛИНАНИЕ (если оно есть)
                if content.startswith(self.hang):
                    content = replaceX(content, self.hang)
                    # content = content.replace(self.hang, '', 1)
        except Exception as e:
            # Фиксируем ошибку, чтобы не ломать весь batch insert в БД
            content = f"ERROR: {str(e)}"
        return {'drink_id': p_id,
                'drink': f'{drink}',
                'lang_result': lang,
                'prompt_id': s_id,
                'writerrule_id': u_id,
                'proption_id': single_params.get('id'),
                'origin': phrase,
                'result': content,
                'hint': translation_hint
                # 'duration': round(duration_s, 4)
                }

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
        for s_id, s_prompt, _ in system_prompts:
            for single_params in params:
                # Для конкретного системного промпта и параметров собираем пачку задач
                group_tasks = []
                # Внутренние циклы выполняются конкурентно (у них общие s_prompt и params)
                for c, (p_id, phrase) in enumerate(phrases):
                    for u_id, u_prompt, _ in user_prompts:
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

    async def _evaluate_single_task_(
            self, semaphore: asyncio.Semaphore, row: dict,  # Принимает ваш словарь из памяти
            xcounter: list, total_tasks: int,
            system_prompt: str,
            user_prompt: str
    ) -> dict:
        """Оценка одного перевода моделью-критиком по вашей структуре полей"""
        target_lang = self.lang_map.get(row['lang_result'][:2], row['lang_result'])
        system_content = system_prompt.format(lang=target_lang)
        user_content = self.render_expert_user_prompt(user_prompt,
                                                      row['drink'],
                                                      row['origin'],
                                                      row['result'],
                                                      row['hint'])
        # Для экспертной оценки всегда используем температуру 0.0
        request_params = self._prepare_params(temperature=0.0)
        request_params["messages"] = [{"role": "system", "content": system_content},
                                      {"role": "user", "content": user_content}]
        logger.warning('request_params')
        jprint(f'{request_params}')

        try:
            async with semaphore:
                start_time = time.time()
                response = await self.client.chat.completions.create(**request_params)
                duration_s = time.time() - start_time

            # raw_content = response.choices.message.content.strip()
            raw_content = response.choices[0].message.content.strip()
            clean_json = raw_content.replace("```json", "").replace("```", "").strip()
            parsed_eval = json.loads(clean_json)
            logger.critical(1)
            jprint(parsed_eval)
            t_score = parsed_eval.get("translation_score", 0)
            text_score = parsed_eval.get("text_score", 0)
            reasoning = parsed_eval.get("reasoning", "")
            errors = parsed_eval.get("errors", "")

        except Exception as e:
            duration_s = 0
            t_score, text_score = 0, 0
            reasoning = f"ERROR: {str(e)}"
            logger.error(f"Ошибка при оценке drink_id={row['drink_id']}: {e}")
        finally:
            xcounter[0] += 1
            if xcounter[0] % 10 == 0:
                logger.info(f"Оценено {xcounter[0]} из {total_tasks} переводов")

        # Обогащаем исходный словарь оценками (удобно для сохранения всей строки в Postgres)
        evaluated_row = row.copy()
        evaluated_row.update(
            {'translation_score': t_score, 'text_score': text_score,
             'total_score': round((t_score + text_score) / 2, 2),  # Средний балл
             'expert_reasoning': reasoning, 'eval_duration': round(duration_s, 4),
             'errors': errors}
        )
        return evaluated_row

    async def evaluate_translations_batch(
            self, translated_records: list[dict],
            d: DrinkTranslateData | HandbookTranslateData,
            max_concurrent_requests: int = 128
    ) -> list[dict]:
        """Массовая оценка пула выполненных переводов"""
        semaphore = asyncio.Semaphore(max_concurrent_requests)
        total_tasks = len(translated_records)

        logger.info(f"Запуск процесса экспертизы. Всего записей на оценку: {total_tasks}")

        xcounter = [0]
        tasks = []
        system_prompt = d.expert_system_prompt[1]
        user_prompt = d.expert_user_prompt[1]
        for row in translated_records:
            task = self._evaluate_single_task_(semaphore, row, xcounter, total_tasks, system_prompt, user_prompt)
            tasks.append(task)

        return await asyncio.gather(*tasks)

    def rank_translation_configs(self, evaluated_records: list[dict]) -> list[dict]:
        """
        Ранжирование комбинаций настроек по среднему баллу всех фраз.
        Помогает выбрать лучший конфиг для заданной subcat.
        """
        configs = {}

        for row in evaluated_records:
            # Уникальный ключ комбинации настроек
            key = (row['prompt_id'], row['writerrule_id'], row['proption_id'])

            if key not in configs:
                configs[key] = {'scores': [], 'prompt_id': row['prompt_id'], 'writerrule_id': row['writerrule_id'],
                                'proption_id': row['proption_id']}

            configs[key]['scores'].append(row['total_score'])

        ranking = []
        for key, data in configs.items():
            avg_score = sum(data['scores']) / len(data['scores']) if data['scores'] else 0
            ranking.append(
                {'prompt_id': data['prompt_id'], 'writerrule_id': data['writerrule_id'],
                 'proption_id': data['proption_id'], 'avg_total_score': round(avg_score, 2),
                 'total_phrases_evaluated': len(data['scores'])}
            )

        # Сортируем: сверху самые высокие средние баллы
        ranking.sort(key=lambda x: x['avg_total_score'], reverse=True)
        return ranking

    def get_best_translations_for_phrase(self, evaluated_records: list[dict], drink_id: int) -> list[dict]:
        """
        Возвращает отранжированный список всех вариантов перевода для конкретной фразы (drink_id).
        Первый элемент списка [0] — самый идеальный кандидат для вставки в основную БД.
        """
        # Фильтруем только варианты для нужной фразы
        phrase_variants = [row for row in evaluated_records if row['drink_id'] == drink_id]

        # Сортируем по качеству (сначала лучшие)
        phrase_variants.sort(key=lambda x: x['total_score'], reverse=True)
        return phrase_variants

    def rank_translation_configs_v2(self, evaluated_records: list[dict]) -> list[dict]:
        """Ранжирование конфигураций с расчетом среднего, лучшего и худшего баллов"""
        configs = {}
        for row in evaluated_records:
            key = (row['prompt_id'], row['writerrule_id'], row['proption_id'])
            if key not in configs:
                configs[key] = {'scores': [], 'prompt_id': row['prompt_id'], 'writerrule_id': row['writerrule_id'],
                                'proption_id': row['proption_id']}
            configs[key]['scores'].append(row['total_score'])

        ranking = []
        for key, data in configs.items():
            scores = data['scores']
            ranking.append(
                {'prompt_id': data['prompt_id'], 'writerrule_id': data['writerrule_id'],
                 'proption_id': data['proption_id'],
                 'avg_score': round(sum(scores) / len(scores), 2) if scores else 0.0,
                 'min_score': min(scores) if scores else 0.0, 'max_score': max(scores) if scores else 0.0,
                 'total_phrases': len(scores)}
            )

        ranking.sort(key=lambda x: x['avg_score'], reverse=True)
        return ranking

    async def real_batch(
            self, phrases: List[Tuple[int, str]],
            d: HandbookTranslateData | DrinkTranslateData,
            # system_prompt: Tuple[int, str],
            # user_prompt: Tuple[int, str], param: dict, lang: str, drink: str,
            max_concurrent_requests: int = 128
    ) -> List[Dict[str, Any]]:
        """
        Метод группового перевода текстов.
        Порядок обхода: system_prompt -> param -> phrase -> user_prompt
        """
        semaphore = asyncio.Semaphore(max_concurrent_requests)
        results = []
        total_tasks = len(phrases)
        remain_tasks = total_tasks
        logger.info(f"Запуск перевода. Всего комбинаций: {total_tasks}")
        start_time = time.time()
        group_tasks = []
        for c, (p_id, phrase, translation_hint, descr1) in enumerate(phrases):
            # descr1 = subcategory_id for drink or d.descr for handbook
            u_id, u_prompt, _ = d.user_prompt
            s_id, s_prompt, _ = d.system_prompt
            single_params = d.params
            if isinstance(d.descr, str):
                descr = d.descr
            elif isinstance(d.descr, dict):
                descr = d.descr.get(descr1)
            task = self._translate_single_task(
                semaphore, p_id, phrase, s_id, s_prompt, u_id, u_prompt, d.language_destination,
                descr, single_params, translation_hint
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

    def render_expert_user_prompt(self, template: str, subject_info: str, origin: str, result: str, hints: dict) -> str:
        """
        Форматирует USER_PROMPT для эксперта, внедряя подсказки из второго бора в качестве глоссария.
        """
        hints_str = ""

        if hints:
            lines = ["\n"]
            for word, translation_set in hints.items():
                variants = ", ".join(f"'{t}'" for t in sorted(translation_set))
                # lines.append(f"- '{word}': can be translated as {variants}")
                lines.append(f"- '{word}': {variants}")
            hints_str = "\n".join(lines)

        return template.format(
            subject_info=subject_info, origin=origin, result=result, translation_hints=hints_str
        )
