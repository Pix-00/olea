from typing import List

from flask import g

from models import Dep, Pink, Pit, Proj, Role
from core.base import BaseMgr
from core.dep_graph import DepGraph
from core.errors import (AccessDenied, DuplicatedRecord, NotQualifiedToPick, ProjMetaLocked,
                         RoleIsTaken)
from core.singleton import db, redis

from .info_builder import build_info

_dep_graph = DepGraph()


class ProjMgr(BaseMgr):
    model = Proj

    @classmethod
    def create(cls, base: str, cat, suff, leader_id):
        title, source, words_count = build_info(base=base, cat=cat)
        if proj := cls.model.query.filter_by(source=source, cat=cat, suff=suff):
            if proj.status == Proj.S.freezed:
                proj.status = Proj.S.pre
                proj.start_at = g.now
                proj.leader_id = leader_id
                proj.add_track(info=Proj.T.re_open, now=g.now, by=g.pink_id)

            else:
                raise DuplicatedRecord(obj=proj)

        else:
            proj = cls.model(id=cls.gen_id(),
                             title=title,
                             cat=cat,
                             source=source,
                             suff=suff,
                             leader_id=leader_id,
                             words_count=words_count,
                             start_at=g.now)
        db.session.add(proj)

        return proj

    def modify_roles(self, add: list, remove: set):
        if g.pink_id != self.o.leader_id:
            raise AccessDenied(obj=self.o)
        if self.o.status != Proj.S.pre:
            raise ProjMetaLocked(status=self.o.status)

        # merge role info, so only need to check once per department
        roles = dict()
        for role_info in add:
            try:
                roles[role_info.dep].add(role_info.name)
            except KeyError:
                roles[role_info.dep] = {role_info.name}

        fails = list()
        for dep, names in roles.items():
            exists = Role.query.filter_by(proj_id=self.o.id). \
                filter_by(dep=dep). \
                filter(Role.name.in_(names)). \
                all()
            fails = [(role.dep, role.name) for role in exists]

        # add first, to prevent conflicts
        for role_info in add:
            if (role_info.dep, role_info.name) in fails:
                continue

            RoleMgr.create(self.o.id, role_info.dep, role_info.name, role_info.note)

        if remove:
            RoleMgr.remove(remove)

        return (self.o.roles, fails)

    def start(self):
        if g.pink_id != self.o.leader_id:
            raise AccessDenied(obj=self.o)
        if self.o.status != Proj.S.pre:
            raise ProjMetaLocked(status=self.o.status)

        self.o.start_at = g.now
        self.o.status = Proj.S.working
        self.o.add_track(info=Proj.T.start, now=g.now)

        pits: List[Pit] = Pit.query.join(Role). \
            filter(Role.proj_id == self.o.id). \
            filter(Pit.status == Pit.S.init). \
            all()
        for pit in pits:
            pit.start_at = _dep_graph.get_start_time(cat=self.o.cat, base=g.now, dep=pit.role.dep)
            pit.due = pit.start_at + _dep_graph.get_duration(cat=self.o.cat, dep=pit.role.dep)
            pit.status = Pit.S.working if pit.start_at == g.now else Pit.S.pending

    def finish(self, url):
        self.o.finish_at = g.now
        self.o.status = Proj.S.fin
        self.o.url = url

        redis.delete(f'cAvbl-{self.o.id}', f'cPath-{self.o.id}', f'cLog-{self.o.id}')

    def freeze(self):
        self.o.status = Proj.S.freezed
        self.o.start_at = None
        self.o.add_track(info=Proj.T.freeze, now=g.now)


class RoleMgr(BaseMgr):
    model = Role

    @classmethod
    def create(cls, proj_id: str, dep: Dep, name: str, note: str):
        role = cls.model(id=cls.gen_id(), proj_id=proj_id, dep=dep, name=name, note=note)
        db.session.add(role)

        return role

    @classmethod
    def remove(cls, ids):
        cls.model.query.filter(Role.id.in_(ids)).delete()

    def full_pick(self, pink_id):
        if self.o.taken:
            raise RoleIsTaken(by=self.o.pit)

        self.o.taken = True
        pit = PitMgr.create(self.o, pink_id)
        if pink_id != g.pink_id:
            pit.add_track(info=Pit.T.pick_f, now=g.now, by=g.piT)

        return pit

    def pick(self):
        pink = Pink.query.get(g.pink_id)
        if self.o.proj.status != Proj.S.pre:
            raise ProjMetaLocked(status=Proj.S.pre)
        if self.o.dep not in pink.deps:
            raise NotQualifiedToPick(dep=self.o.dep)

        return self.full_pick(pink.id)


class PitMgr(BaseMgr):
    model = Pit

    @classmethod
    def create(cls, role, pink_id):
        pit = cls.model(id=cls.gen_id(), role=role, pink_id=pink_id, timestamp=g.now)
        db.session.add(pit)

        return pit
