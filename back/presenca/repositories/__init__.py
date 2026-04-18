from django.db import models
from typing import TypeVar, Type, Any

T = TypeVar('T', bound=models.Model)

class Repository[T: models.Model]:
    model: Type[T]

    @classmethod
    def get(cls, *args: Any, related: bool = False, **kwargs: Any) -> T:
        if related:
            return cls.model.objects.select_related().get(*args, **kwargs)

        return cls.model.objects.get(*args, **kwargs)

    @classmethod
    def get_all(cls) -> models.QuerySet[T]:
        return cls.model.objects.all()
