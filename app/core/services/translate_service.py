# app.core.services.translate_service.py
import time
from typing import Dict, Any
from openai import AsyncOpenAI


class TranslationService:
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url='http://vllm-node:8000/v1/', api_key="token-not-needed"
        )
        # Имя модели должно совпадать с тем, как она примонтирована/названа в vLLM
        self.model_name = "/model"
        self.lang_map = {'ru': 'Russian', 'en': 'English', 'de': 'German', 'fr': 'French', 'es': 'Spanish',
                         'it': 'Italian', 'zh': 'Chinese', 'ja': 'Japanese'}

    def _build_messages(self, system_prompt: str, user_prompt: str, lang_code: str, phrase: str) -> list:
        """
        Формирует структурированный массив сообщений для Chat Completions API.
        vLLM автоматически применит к нему ChatML шаблоны для Qwen.
        """
        target_lang = self.lang_map.get(lang_code[:2], 'German')

        system_content = system_prompt.format(lang=target_lang)
        user_content = user_prompt.format(lang=target_lang, phrase=phrase)

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
            self, phrase: str, system_prompt: str, user_prompt: str, lang_code: str, **params
    ) -> Dict[str, Any]:
        """Основной метод перевода, адаптированный под Qwen (Chat API)"""
        start_ms = time.time() * 1000

        # Вместо текстовой строки генерируем массив ролей (System / User)
        messages = self._build_messages(system_prompt, user_prompt, lang_code, phrase)
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
