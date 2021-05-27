import attr
import cattr
import pandas as pd
from collections.abc import Mapping, MutableMapping
from collections import UserList
from typing import Union, get_origin, get_args
from itertools import product
from copy import deepcopy


def nest_dict(flat, sep='.'):
    def _nest_dict_rec(k, v, out, sep='.'):
        k, *rest = k.split(sep, 1)
        if rest:
            _nest_dict_rec(rest[0], v, out.setdefault(k, {}))
        else:
            out[k] = v

    result = {}
    for k, v in flat.items():
        _nest_dict_rec(k, v, result, sep=sep)
    return result

def flatten_dict(d, sep='.', parent_key=''):
    flat_d = {}
    for k, v in d.items():
        if parent_key: k = parent_key + sep + k
        if isinstance(v, MutableMapping):
            flat_d.update(flatten_dict(v, sep=sep, parent_key=k))
        else:
            flat_d[k] = v
    return flat_d

def default_value(default):
    return attr.ib(default=attr.Factory(lambda: default))


@attr.s(auto_attribs=True)
class DictDataClass(Mapping):
    """Allow dict-like access to attributes using ``[]`` operator in addition to dot-access."""

    def __iter__(self):
        return iter(vars(self))

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __len__(self):
        return len(vars(self))

    def to_dict(self):
        return attr.asdict(self)

    def to_flattened_dict(self, sep='.'):
        # _d = pd.json_normalize(attr.asdict(self), sep=sep).iloc[0].to_dict()
        _d  = flatten_dict(self.to_dict())

        # hack to fix tune.grid_search() values as they are themselves dicts
        d = {}
        for k, v in _d.items():
            if k.endswith('grid_search'):
                parts = k.split(sep)
                d[sep.join(parts[:-1])] = {'grid_search': v}
            else:
                d[k] = v
        return d

    @classmethod
    def from_flattened_dict(cls, d: dict):
        return cls.from_dict(nest_dict(d))

    @classmethod
    def from_dict(cls, d: dict):
        converter = cattr.Converter()

        disambiguators = cls.get_all_disambiguators()
        for union_type, func in disambiguators.items():
            converter.register_structure_hook(union_type, lambda o, t, hook=func: converter.structure(o, hook(o, t)))
        return converter.structure(d, cls)

    @classmethod
    def get_disambiguators(cls):
        return {}

    @classmethod
    def get_all_disambiguators(cls):
        disambiguators = cls.get_disambiguators()
        for _, t in cls.__annotations__.items():
            try:
                if issubclass(t, DictDataClass):
                    disambiguators.update(t.get_all_disambiguators())
            except TypeError as e:
                if str(e) == 'issubclass() arg 1 must be a class': # t is a generic type not a class
                    if get_origin(t) == Union:
                        for _t in get_args(t):
                            if issubclass(_t, DictDataClass):
                                disambiguators.update(_t.get_all_disambiguators())
        return disambiguators

class Settings(UserList):
    def __init__(self, data):
        super().__init__(data)

class Parameters(DictDataClass):
    def get_settings(self):
        keys = []
        value_lists = []
        for k, v in self.items():
            if isinstance(v, Parameters):
                value_lists.append(v.get_settings())
                keys.append(k)
            elif isinstance(v, Settings):
                if len(v) == 0:
                    raise ValueError(f"Empty settings list for {k}")
                if isinstance(v[0], Parameters):
                    value_lists.append([s for _v in v for s in _v.get_settings()])
                else:
                    value_lists.append(v)
                keys.append(k)
        _setting = deepcopy(self)
        settings = []
        for values in product(*value_lists):
            for k, v in zip(keys, values):
                setattr(_setting, k, v)
            settings.append(deepcopy(_setting))
        return settings
