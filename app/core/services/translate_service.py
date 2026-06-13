# app.core.services.translate_service.py
import time
from typing import Dict, Any
from openai import AsyncOpenAI


class TranslationService:
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url='http://vllm-node:8000/v1/', api_key="token-not-needed"
        )
        self.model_name = "/model"
        self.lang_map = {'ru': 'Russian', 'en': 'English', 'de': 'German', 'fr': 'French', 'es': 'Spanish',
                         'it': 'Italian', 'zh': 'Chinese', 'ja': 'Japanese'}

    def _build_prompt(self, system_prompt: str, user_prompt: str, lang_code: str, phrase: str) -> str:
        """Собирает промпт в формате Mistral"""
        target_lang = self.lang_map.get(lang_code[:2], 'German')
        system = system_prompt.format(lang=target_lang)
        user = user_prompt.format(lang=target_lang, phrase=phrase)
        return f"[INST] {system}\n\n{user} [/INST]"

    def _prepare_params(self, **kwargs) -> Dict[str, Any]:
        """Подготавливает параметры для vLLM"""
        params = {"model": self.model_name, "temperature": kwargs.get('temperature', 0.1),
                  "top_p": kwargs.get('top_p', 0.85),
                  # "top_k": kwargs.get('top_k', 50) or None,
                  "max_tokens": kwargs.get('max_tokens', 2048),
                  "frequency_penalty": kwargs.get('frequency_penalty', 0.2),
                  "presence_penalty": kwargs.get('presence_penalty', 0.1),
                  "seed": kwargs.get('seed', 42),
                  # "stop": kwargs.get('stop', None) or None,
                  }

        # extra_body для параметров vLLM, которых нет в OpenAI SDK
        extra_body = {}

        if (top_k := kwargs.get('top_k', 50)) > 0:
            extra_body['top_k'] = top_k

        if (repeat_penalty := kwargs.get('repeat_penalty', 1.1)) != 1.1:
            extra_body['repeat_penalty'] = repeat_penalty

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
        """Основной метод перевода"""
        start_ms = time.time() * 1000

        prompt = self._build_prompt(system_prompt, user_prompt, lang_code, phrase)
        request_params = self._prepare_params(**params)
        request_params["prompt"] = prompt

        gpu_start = time.time() * 1000
        response = await self.client.completions.create(**request_params)

        return {"original": phrase,
                "content": response.choices[0].text.strip(),
                "performance": {"total_sec": (time.time() * 1000 - start_ms) / 1000,
                                "gpu_s": (time.time() * 1000 - gpu_start) / 1000, "tokens": response.usage.completion_tokens,
                                "speed_tok_per_sec": round(
                                response.usage.completion_tokens / max((time.time() * 1000 - gpu_start) / 1000, 0.001),
                                1
                )}}
