from easyclasses import EasyClass, LightEasyClass
import time
from dataclasses import dataclass
from typing import Callable, NamedTuple
import attrs


def count(func: Callable[[], None]):
    a = time.perf_counter()
    func()
    b = time.perf_counter()
    print(f"{func.__name__} took {b - a} seconds")


@count
def easy_class():
    for _ in range(30000):

        class MyClass(EasyClass):
            a: str
            b: str
            c: str
            d: str = "d"

        MyClass("a", "b", "c", d="test")
        assert MyClass("a", "b", "c", d="test") == MyClass("a", "b", "c", d="test")


@count
def light_easy_class():
    for _ in range(30000):

        class MyClass(LightEasyClass):
            a: str
            b: str
            c: str
            d: str = "d"

        MyClass("a", "b", "c", d="test")
        assert (
            MyClass("a", "b", "c", d="test").__dict__
            == MyClass("a", "b", "c", d="test").__dict__
        )


@count
def data_class():
    for _ in range(30000):

        @dataclass
        class MyClass:
            a: str
            b: str
            c: str
            d: str = "d"

        MyClass("a", "b", "c", d="test")
        assert MyClass("a", "b", "c", d="test") == MyClass("a", "b", "c", d="test")


@count
def named_tuple():
    for _ in range(30000):

        class MyClass(NamedTuple):
            a: str
            b: str
            c: str
            d: str = "d"

        MyClass("a", "b", "c", d="test")
        assert MyClass("a", "b", "c", d="test") == MyClass("a", "b", "c", d="test")


@count
def attrs_dataclass():
    for _ in range(30000):

        @attrs.define
        class MyClass:
            a: str
            b: str
            c: str
            d: str = "d"

        MyClass("a", "b", "c", d="test")
        assert MyClass("a", "b", "c", d="test") == MyClass("a", "b", "c", d="test")
