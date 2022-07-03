from typing import (
    Dict,
    Any,
    Callable,
    Type,
    TypeVar,
    Optional,
    List,
    get_type_hints,
)
import copy

T = TypeVar("T")
Validator = Callable[[T], bool]

__all__ = (
    "LightEasyClass",
    "EasyClass",
    "factory",
    "validator",
)

FACTORY = "_ec_factory"
FACTORY_DEFAULT = "_ec_factory_default"
VALIDATOR = "_ec_validator"
DATA = "_ec_data"


def _base_eq(self: "EasyClass", v: Any):
    return self.__dict__ == v.__dict__


class LightEasyClass:
    """Base class for handling an easy data class."""

    _params: List[str]
    _defaults: Dict[str, Any]

    def __init__(self, *args, **kwargs):
        if self.__class__ is EasyClass:
            raise TypeError("cannot directly instantiate EasyClass")

        name: str = self.__class__.__name__
        validators: Dict[str, Validator] = {}

        for i in self._params:
            attr = getattr(self, i, None)
            if hasattr(attr, VALIDATOR):
                validators[i] = attr._ec_validator  # type: ignore

        for key, value in kwargs.items():
            if key not in self._params:
                raise TypeError(
                    f"{name}() got an unexpected keyword argument '{key}'",
                )

            setattr(
                self,
                key,
                value,
            )

        for i in zip(args, self._params):
            setattr(self, i[1], i[0])

        missing: list = []

        for i in self._params:
            if not hasattr(self, i):
                missing.append(i)

            attr = getattr(self, i, None)
            data = attr if not hasattr(attr, VALIDATOR) else attr._ec_data  # type: ignore

            if hasattr(data, FACTORY):
                default = getattr(data, FACTORY_DEFAULT, None)
                setattr(
                    self,
                    i,
                    (copy.deepcopy(default) if default else None) or data._ec_factory(),  # type: ignore
                )

            if i in validators:
                assert validators[i](getattr(self, i)), "validation failed"

        if missing:
            if len(missing) == 1:
                raise TypeError(
                    f"{name}() missing 1 required positional argument: '{missing[0]}'"  # noqa
                )

            count = len(missing)
            m_args = ", ".join(
                [
                    f"'{value}'" if not (index + 1) == count else f"and '{value}'"
                    for index, value in enumerate(missing)
                ]
            )
            raise TypeError(
                f"{name}() missing {count} required positional arguments: {m_args}"  # noqa
            )

    def __init_subclass__(cls) -> None:
        cls._params = [i for i in get_type_hints(cls) if not i.startswith("_")]
        cls._defaults = {}

        kw: bool = False

        for i in cls._params:
            if hasattr(cls, i):
                kw = True
                cls._defaults[i] = getattr(cls, i)
            elif kw:
                raise SyntaxError(
                    "non-default argument follows default argument",
                )

    def __repr__(self) -> str:
        attrs = [f"{i}={repr(getattr(self, i))}" for i in self._params]
        return f"{self.__class__.__name__}({', '.join(attrs)})"

    @property
    def __dict__(self):
        return {i: getattr(self, i) for i in self._params}


class EasyClass(LightEasyClass):
    """Class for handling an easy data class."""

    _immutable: bool = False
    _ready: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ready = True

    def __init_subclass__(
        cls,
        *,
        eq: bool = True,
        immutable: bool = False,
    ) -> None:
        super().__init_subclass__()

        if eq:
            cls.__eq__ = _base_eq  # type: ignore

        cls._immutable = immutable

    def __setattr__(self, name: str, value: Any) -> None:
        if self._immutable and self._ready:
            raise TypeError(f"{self.__class__.__name__}() is immutable")
        return super().__setattr__(name, value)


def validator(data: T, validator: Validator[T]) -> Any:
    """Create a validator for an argument."""
    return type(
        "validator",
        (),
        {
            DATA: data,
            VALIDATOR: validator,
        },
    )


def factory(
    typ: Type[T],
    default: Optional[T] = None,
) -> Any:
    """Create a factory for an argument."""

    return type(
        "factory",
        (),
        {
            FACTORY: typ,
            FACTORY_DEFAULT: default,
        },
    )
