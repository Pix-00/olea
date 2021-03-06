from typing import Any, Dict


class BaseCondition():
    def gen_schema(self, field_type, schema) -> Dict[str, Any]:
        pass


class AnyValue(BaseCondition):
    def gen_schema(self, field_type, schema):
        return schema


class Regex(BaseCondition):
    def __init__(self, pattern):
        self.pattern = pattern

    def gen_schema(self, field_type, schema):
        schema.update({'pattern': self.pattern})
        return schema


class MultipleOf(BaseCondition):
    def __init__(self, factor):
        self.factor = factor

    def gen_schema(self, field_type, schema):
        if field_type != 'number':
            raise Exception()

        schema.update({'multipleOf': self.factor})
        return schema


class In(BaseCondition):
    def __init__(self, *values):
        self.values = list(set(values))

    def gen_schema(self, field_type, schema):
        if field_type == 'string':
            schema.update({'enum': self.values})

        elif field_type == 'array':
            schema['items'].update({'enum': self.values})

        else:
            raise Exception()

        return schema


class InRange(BaseCondition):
    def __init__(self, min_val=None, max_val=None, min_inclusive=True, max_inclusive=True):
        self.min = min_val
        self.max = max_val
        self.min_inclusive = min_inclusive
        self.max_inclusive = max_inclusive

    def gen_schema(self, field_type, schema):
        result = dict()
        if field_type == 'number':
            if self.min:
                result['minimum'] = self.min
            if not self.min_inclusive:
                result['exclusiveMinimum'] = False
            if self.max:
                result['maximum'] = self.max
            if not self.max_inclusive:
                result['exclusiveMaximum'] = False

        elif field_type == 'string':
            if self.min:
                result['minLength'] = self.min
            if self.max:
                result['maxLength'] = self.max

        elif field_type == 'array':
            if self.min:
                result['minItems'] = self.min
            if self.max:
                result['maxItems'] = self.max

        schema.update(result)
        return schema


class Contains(BaseCondition):
    def __init__(self, condition):
        self.confition = condition

    def gen_schema(self, field_type, schema):
        return {'contains': self.confition.gen_schema(field_type, schema)}
