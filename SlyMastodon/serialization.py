from dataclasses import fields, is_dataclass
from types import NoneType
from typing import TypeVar, cast
from types import UnionType
from enum import Enum
from datetime import datetime
import inspect

from SlyAPI.web import JsonType

T = TypeVar('T')

def dataclass_from_json(cls: type[T], value: JsonType, parent_types: list[type]|None=None) -> T:
    if not isinstance(value, dict):
        raise TypeError(F"Failed to convert {value} to {cls}")
    parents = (parent_types or []) + [cls]
    return cls(**{
        f.name: convert_from_json(f.type, value[f.name], parents)
        for f in fields(cls)
    })

def convert_from_json(cls: type[T], value: JsonType, parent_types: list[type]|None = None) -> T:
    """
    Convert a json to T instance.
    Will evaluate string annotations.
    May not round-trip, especially if a member of T is a union of multiple types with the same shallow json representation (e.g. set | list, dict | dataclass)
    Fails if representation was different than what was expected.
    Supported non-json types:
        - datetime.datetime
        - enum.Enum
        - set[T], tuple[T, ...]
        - dataclasses (assuming all members are convertable)
    """
    err = TypeError(F"Failed to convert {value} to {cls}")
    parents = (parent_types or []) + [cls]
    if cls in (int, str, bool, float, NoneType) and isinstance(value, cls):
        return value
    elif hasattr(cls, 'from_json'): # overridden deserialization
        return getattr(cls, 'from_json')(value)
    elif hasattr(cls, '__origin__'):
        origin = getattr(cls, '__origin__')
        if origin in (list, set):
            t, = getattr(cls, '__args__')
            if not isinstance(value, list):
                raise err
            return origin(convert_from_json(t, v, parents) for v in value)
        elif origin is tuple:
            ts = getattr(cls, '__args__')
            if not isinstance(value, list):
                raise err
            return tuple(convert_from_json(t, v, parents) for t, v in zip(ts, value)) # type: ignore - tuple args are T args
        elif origin is dict:
            _kt, vt = getattr(cls, '__args__')
            if not isinstance(value, dict):
                raise err
            return origin({
                k: convert_from_json(vt, v, parents)
                for k, v in value.items()
            })
        else:
            raise err
    elif type(cls) is UnionType:
        args = getattr(cls, '__args__')
        if type(value) in args:
            return value # type: ignore - value is already of the correct type
        for t in getattr(cls, '__args__'):
            try:
                return convert_from_json(t, value, parents)
            except TypeError:
                pass
        raise err
    elif is_dataclass(cls):
        return dataclass_from_json(cls, value, parents) # type: ignore - is_dataclass discards T
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
        return cast(T, cls(value))
    elif type(cls) is str: # delayed annotation
        parent_class_vars = {
            t.__name__: t 
            for t in parents
            if inspect.isclass(t)
        }
        print(parents)
        print(parent_class_vars)
        t = eval(cls, globals(), parent_class_vars)
        return convert_from_json(t, value, parents)
    else:
        raise TypeError(F"No known conversion from {value} to {cls}")

class DataclassJsonMixin:

    @classmethod
    def from_json(cls: type[T], value: JsonType) -> T:
        # print(value)
        return dataclass_from_json(cls, value, [cls])