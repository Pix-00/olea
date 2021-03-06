from flask import g

from models import Ann, Chat, Proj
from core.auth import check_scopes
from core.base import BaseMgr
from core.errors import AccessDenied, InvalidReply, ProjMetaLocked
from core.singleton import db, redis


class AnnMgr(BaseMgr):
    module = Ann

    @classmethod
    def post(cls, cat, deps, expiration, content):
        check_scopes(deps)
        ann = cls.model(id=cls.gen_id(),
                        cat=cat,
                        deps=deps,
                        expiration=expiration,
                        poster_id=g.pink_id,
                        content=content,
                        at=g.now)
        db.session.add(ann)

        return ann

    def edit(self, content):
        if self.o.poster_id != g.pink_id:
            raise AccessDenied(obj=self.o)

        self.o.update(now=g.now, content=content)

        return self.o

    def delete(self):
        if self.o.poster_id != g.pink_id:
            raise AccessDenied(obj=self.o)

        self.o.deleted = True


class ProjMgr(BaseMgr):
    def post_chat(self, reply_to_id, content):
        if self.o.status != Proj.S.working:
            raise ProjMetaLocked(status=self.o.status)

        # TODO: permission check
        return ChatMgr.post(self, reply_to_id, content)


class ChatMgr(BaseMgr):
    module = Chat

    @staticmethod
    def _is_visible(proj_id, id_):
        if not redis.sismember(f'cAvbl-{proj_id}', id_):
            raise InvalidReply()

    @staticmethod
    def _get_path(proj_id, id_):
        return redis.sscan(f'cPath-{proj_id}', f'*/{id_}')

    @classmethod
    def post(cls, proj, reply_to_id: str, content: str):
        if reply_to_id:
            cls._is_visible(proj.id, reply_to_id)
            path = cls._get_path(proj.id, reply_to_id)

        else:
            path = '/'

        chat = cls.model(id=cls.gen_id(),
                         proj_id=proj.id,
                         pink_id=g.pink_id,
                         reply_to_id=reply_to_id)
        chat.update(now=g.now, content=content)
        chat.set_order(proj_timestamp=proj.timestamp, now=g.now)
        db.session.add(chat)

        with redis.pipeline(transaction=True) as p:
            p.zadd(f'cLog-{proj.id}', f'+ {chat.id}')
            p.sadd(f'cAvbl-{proj.id}', chat.id)
            p.sadd(f'cPath-{proj.id}', path)

            p.execute()

        return chat

    def edit(self, content):
        if self.o.pink_id != g.pink_id:
            raise AccessDenied(obj=self.o)
        self._is_visible(self.o.proj_id, self.o.id)

        self.o.update(now=g.now, content=content)
        redis.zadd(f'cLog-{self.o.proj_id}', f'e {self.o.id}')

        return self.o

    def delete(self):
        self._is_visible(self.o.proj_id, self.o.id)

        self.o.delete = True

        path = self._get_path(self.o.proj_id, self.o.id)
        queue = [redis.sscan_iter(f'cPath-{self.o.proj_id}', f'{path}/*')]
        with redis.pipeline(transaction=True) as p:
            p.zadd(f'cLog-{self.o.proj_id}', f'- {self.o.id}')
            p.srem(f'cAvbl-{self.o.proj_id}', *[cpath.split('/')[-1] for cpath in queue])

            p.execute()

    def restore(self):
        self.o.delete = False

        path = self._get_path(self.o.proj_id, self.o.id)
        queue = [redis.sscan_iter(f'cPath-{self.o.proj_id}', f'{path}/*')]
        with redis.pipeline(transaction=True) as p:
            p.zadd(f'cLog-{self.o.proj_id}', f'r {self.o.id}')
            p.sadd(f'cAvbl-{self.o.proj_id}', *[cpath.split('/')[-1] for cpath in queue])

            p.execute()
