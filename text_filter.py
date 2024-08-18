from typing import List

from aiogram.filters import Filter
from aiogram.types import Message


class TextFilter(Filter):
    def __init__(self, texts: List[str]) -> None:
        self.texts = texts

    async def __call__(self, message: Message) -> bool:
        return message.text in self.texts
