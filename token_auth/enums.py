from enum import Enum


class Sex(Enum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    UNSURE = 'UNSURE'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
