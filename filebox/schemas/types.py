from typing import Any, ClassVar

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


class BasePath(str):
    min_length: ClassVar[int] = 1
    max_length: ClassVar[int] = 96
    pattern: ClassVar[str] = ""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.general_after_validator_function(
            cls.validate,
            core_schema.str_schema(
                min_length=cls.min_length,
                max_length=cls.max_length,
                pattern=cls.pattern,
            ),
        )

    @classmethod
    def validate(cls, __input_value: str, _: core_schema.ValidationInfo) -> str:
        return cls(__input_value)


class FilePath(BasePath):
    min_length = 1
    max_length = 96


class FolderPath(BasePath):
    pattern = r"^(?:\/(?:[\w\s]+\/)*[\w\s]+|\/)$"
    min_length = 1
    max_length = 96
