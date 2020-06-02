from enum import Enum


class ContentType(Enum):
    EVENT = 'EVENT'
    TICKET = 'TICKET'
    PROFILE = 'PROFILE'
    CHAT = 'CHAT'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
