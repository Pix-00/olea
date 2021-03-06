from datetime import date, datetime, time
from typing import Any

from .conditions import AnyValue, In
from .logic_opt import Grouping


class CacheField(type):
    def __init__(self, *args, **kwargs):
        self.__instance = dict()
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        trait = list(args)
        trait.append(kwargs.get('required', True))
        trait.append(kwargs.get('nullable', False))

        key = tuple(trait)
        if key not in self.__instance:
            if 'condition' in kwargs or 'default' in kwargs:
                return super().__call__(*args, **kwargs)

            self.__instance[key] = super().__call__(*args, **kwargs)

        return self.__instance[key]


class BaseField(metaclass=CacheField):
    _type = ''
    _default: Any = None

    def __init__(self, required=True, nullable=False, condition=None, default=None):
        self._required = required if not default else False
        self._nullable = nullable
        self._condition = condition if condition else AnyValue()
        self._default = default if default else self._default

    def schema(self):
        result = {'type': self._type if not self._nullable else [self._type, None]}
        return self._condition.gen_schema(field_type=self._type, schema=result)

    def set_default(self):
        try:
            return self._default()
        except TypeError:
            return self._default

    def wrap_data(self, data, errors, extra):
        if errors:
            return None, errors
        if not data and self._nullable:
            return None, 'cannot be null'
        if extra:
            return (data, extra(data))

        return (data, errors)


class Boolean(BaseField):
    _type = 'boolean'
    _default = None


class String(BaseField):
    _type = 'string'
    _default = ''


class Enum(String):
    def __init__(self, enum_class, required=True, nullable=False, condition=None, default=None):
        self._enum_class = enum_class
        if default:
            default = default.name
        condition = Grouping(In(*[enum.name for enum in enum_class]))
        super().__init__(required=required, nullable=nullable, condition=condition, default=default)

    def wrap_data(self, data, errors, extra):
        data, errors = super().wrap_data(data, errors, extra)

        if data:
            return (self._enum_class[data], errors)
        return (data, errors)


class Email(String):
    def schema(self):
        result = super().schema()
        result.update({'format': 'email'})
        return result


class DateTime(String):
    def schema(self):
        result = super().schema()
        result.update({'format': 'date-time'})
        return result

    def wrap_data(self, data, errors, extra):
        data, errors = super().wrap_data(data, errors, extra)

        if data:
            return (datetime.fromisoformat(data), errors)
        return (data, errors)


class Date(String):
    def schema(self):
        result = super().schema()
        result.update({'format': 'date'})
        return result

    def wrap_data(self, data, errors, extra):
        data, errors = super().wrap_data(data, errors, extra)

        if data:
            return (date.fromisoformat(data), errors)
        return (data, errors)


class Time(String):
    def schema(self):
        result = super().schema()
        result.update({'format': 'time'})
        return result

    def wrap_data(self, data, errors, extra):
        data, errors = super().wrap_data(data, errors, extra)

        if data:
            return (time.fromisoformat(data), errors)
        return (data, errors)


class Number(BaseField):
    _type = 'number'
    _default = 0.0

    def wrap_data(self, data, errors, extra):
        data, errors = super().wrap_data(data, errors, extra)

        if data:
            return (float(data), errors)
        return (data, errors)


class Integer(BaseField):
    _type = 'integer'
    _default = 0

    def wrap_data(self, data, errors, extra):
        data, errors = super().wrap_data(data, errors, extra)

        if data:
            return (int(data), errors)
        return (data, errors)


class List(BaseField):
    _type = 'array'
    _default = list

    def __init__(self, sub_field, required=True, nullable=False, condition=None, default=None):
        if isinstance(sub_field, type):
            self._sub_field = sub_field()
        else:
            self._sub_field = sub_field
        super().__init__(required=required, nullable=nullable, condition=condition, default=default)

    def schema(self):
        result = super().schema()
        result.update({'items': self._sub_field.schema()})
        return result

    def wrap_data(self, data, errors, extra):
        if not data and self._nullable:
            return None, 'cannot be null'

        if isinstance(errors, str):
            return None, errors

        result = [
            self._sub_field.wrap_data(item, errors.get(i, None), None)
            for i, item in enumerate(data)
        ]
        return result, extra(result)


class Set(List):
    _default = set

    def schema(self):
        result = super().schema()
        result['uniqueItems'] = True
        return result

    def wrap_data(self, data, errors, extra):
        data, errors = super().wrap_data(data, errors, extra)

        if data:
            return (set(data), errors)
        return (data, errors)


class Tuple(BaseField):
    _type = 'array'
    _default = tuple

    def __init__(self, fields, required=True, nullable=False, condition=None, default=None):
        self._fields = list()
        for field in fields:
            if isinstance(field, type):
                self._fields.append(field())
            else:
                self._fields.append(field)
        super().__init__(required=required, nullable=nullable, condition=condition, default=default)

    def schema(self):
        result = super().schema()
        result.update({'items': [field.schema() for field in self._fields]})
        return result

    def wrap_data(self, data, errors, extra):
        if not data and self._nullable:
            return (None, 'cannot be null')

        if isinstance(errors, str):
            return (None, errors)

        result = tuple([
            field.wrap_data(item, errors.get(i, None))
            for field, i, item in zip(self._fields, range(len(data)), data)
        ])
        return (result, extra(result))
