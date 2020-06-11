from flask_jsonform import BaseForm
from jsonform.fields import EnumField, SetField, StringField

from models import Dep


class Search(BaseForm):
    deps = SetField(EnumField(Dep), optinal=True)
    pink_id = StringField(optional=True)
