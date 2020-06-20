from flask import g

from models import Dep, Pit, Role
from olea.base import single_query
from olea.errors import AccessDenied


class PitQuery():
    @staticmethod
    def single(id_):
        return single_query(model=Pit,
                            id_or_obj=id_,
                            condiction=lambda obj: obj.pink_id == g.pink_id)

    @classmethod
    def checks(cls, deps):
        if not g.check_scopes(scopes=deps):
            raise AccessDenied(cls_=Pit)

        pits = Pit.query.join(Role). \
            filter(Pit.state == Pit.S.auditing). \
            filter(Role.dep.in_(deps)).all()

        return pits

    @classmethod
    def in_dep(cls, dep, status):
        if not g.check_scopes(scopes=dep):
            raise AccessDenied(cls_=Pit)

        pits = Pit.query.join(Role). \
            filter(Role.dep == dep). \
            filter(Pit.state.in_(status)).all()

        return pits

    @classmethod
    def search(cls, deps, states, pink_id=''):
        if (not pink_id or pink_id != g.pink_id) and not g.check_opt_duck(scopes=deps):
            raise AccessDenied(cls_=Pit)

        query = Pit.query.join(Role)
        if deps:
            query = query.filter(Role.dep.in_(deps))
        if states:
            query = query.filter(Pit.state.in_(states))
        if pink_id:
            query = query.filter(Pit.pink_id == pink_id)

        return query.all()
