from dataclasses import fields, is_dataclass
import sys
from types import NoneType
from typing import TypeVar
from types import UnionType
from enum import Enum
from datetime import datetime
import inspect

from SlyAPI.web import JsonTypeCo

T = TypeVar('T')

def dataclass_from_json(cls: type[T], value: JsonTypeCo, typevars: dict[str, type]) -> T:
    if not isinstance(value, dict):
        raise TypeError(F"Failed to convert {value} to {cls}")
    return cls(**{
        f.name: convert_from_json(f.type, value[f.name], typevars, cls)
        for f in fields(cls)
    })

def convert_from_json(cls: type[T], value: JsonTypeCo, typevars_: dict[str, type]|None = None, parent: type|None = None) -> T:
    """
    Convert a json value to a T instance.
    `cls` must be trusted, since the type may contain string type annotations that are evaluated.
        - For instance, recursive data structures.
    May not round-trip, especially if a member of T is a union of multiple types with the same shallow json representation (e.g. set | list, dict | dataclass)
    Fails if representation was different than what was expected.
    Supported non-json types:
        - datetime.datetime
        - enum.Enum
        - set[T], tuple[T, ...]
        - dataclasses (assuming all members are convertable)
    """
    typevars = (typevars_ or {})
    if inspect.isabstract(cls):
        raise TypeError("Conversion type must be concrete")
    err = TypeError(F"Failed to convert {value} to {cls}")
    if cls in (int, str, bool, float, NoneType) and isinstance(value, cls):
        return value
    elif hasattr(cls, 'from_json'): # overridden deserialization
        return getattr(cls, 'from_json')(value)
    elif hasattr(cls, '__origin__'): # built-in generics
        origin: type = getattr(cls, '__origin__')
        if origin in (list, set):
            t, = getattr(cls, '__args__')
            if not isinstance(value, list):
                raise err
            return origin(convert_from_json(t, v, typevars, parent) for v in value)
        elif origin is tuple:
            ts = getattr(cls, '__args__')
            if not isinstance(value, list):
                raise err
            return tuple(convert_from_json(t, v, typevars, parent) for t, v in zip(ts, value)) # type: ignore - tuple args are T args
        elif origin is dict:
            _kt, vt = getattr(cls, '__args__')
            if not isinstance(value, dict):
                raise err
            return origin({
                k: convert_from_json(vt, v, typevars, parent)
                for k, v in value.items()
            })
        elif is_dataclass(origin):
            typeparams: list[TypeVar] = getattr(origin, '__parameters__')
            args: list[type] = getattr(cls, '__args__')
            newtypevars = {
                str(var): t # like ~T: int
                for var, t in zip(typeparams, args)
            }
            return dataclass_from_json(origin, value, typevars | newtypevars) # type: ignore - is_dataclass discards T
        else:
            raise err
    elif type(cls) is TypeVar:
        name = str(cls)
        if name not in typevars:
            raise ValueError(F"Unbound generic type variable {name} in {cls}")
        return convert_from_json(typevars[name], value, typevars, cls) # type: ignore
    elif type(cls) is UnionType:
        args = getattr(cls, '__args__')
        if type(value) in args:
            return value # type: ignore - value is already of the correct type
        for t in getattr(cls, '__args__'):
            try:
                return convert_from_json(t, value, typevars, parent)
            except TypeError:
                pass
        raise err
    elif is_dataclass(cls):
        return dataclass_from_json(cls, value, typevars) # type: ignore - is_dataclass discards T
    elif cls == datetime:
        if isinstance(value, str):
            return datetime.fromisoformat(value) # type: ignore
        elif isinstance(value, (int, float)):
            return datetime.fromtimestamp(value) # type: ignore
        else:
            raise err
    elif inspect.isclass(cls) and issubclass(cls, Enum):
        if not isinstance(value, (str, int)):
            raise err
        return cls(value) # type: ignore
    elif type(cls) is str: # delayed annotation
        if parent is not None:
            cls_globals = vars(sys.modules[parent.__module__])
        else:
            cls_globals = {}
        t = eval(cls, cls_globals)
        return convert_from_json(t, value, typevars, parent)
    else:
        raise TypeError(F"No known conversion from {value} to {cls}")

class DataclassJsonMixin:

    @classmethod
    def from_json(cls: type[T], value: JsonTypeCo) -> T:
        # print(value)
        return dataclass_from_json(cls, value, {})