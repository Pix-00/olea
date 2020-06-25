from flask import request
from flask_json import json_response

from olea.auth import opt_perm, perm

from . import bp
from .forms import ChatLogs, Edit, FetchAnn, FetchChat, PostAnn, PostChat
from .query import AnnQuery, ChatQuery
from .services import AnnMgr, ChatMgr, ProjMgr


@bp.route('/anns/', methods=['GET'])
def search():
    form = FetchAnn(data=request.args)
    anns = AnnQuery.search(deps=form.deps)
    return json_response(data_=anns)


@bp.route('/anns/post', methods=['POST'])
@perm
def post_():
    form = PostAnn()
    ann = AnnMgr.post(cat=form.cat,
                      deps=form.deps,
                      expiration=form.expiration,
                      content=form.content)
    return json_response(data_=ann)


@bp.route('/anns/<ann_id>/edit', methods=['POST'])
@perm
def edit(ann_id):
    form = Edit()
    ann = AnnMgr(ann_id).edit(content=form.content)
    return json_response()


@bp.route('/anns/<ann_id>/delete', methods=['Post'])
@perm
def delete_(ann_id):
    pits = AnnMgr(ann_id).delete()
    return json_response()


@bp.route('/chats/<proj_id>/', methods=['GET'])
def chats_index(proj_id):
    form = ChatLogs(data=request.args)
    index = ChatQuery.chat_logs(proj_id=proj_id, offset=form.offset)
    return json_response(data_=index)


@bp.route('/chats/', methods=['GET'])
def chats():
    form = FetchChat(data=request.args)
    chats = ChatQuery.chats(chats=form.chats)
    return json_response(data_=chats)


@bp.route('/chats/<proj_id>/post', methods=['POST'])
def post_chat(proj_id):
    form = PostChat()
    chat = ProjMgr(proj_id).post_chat(reply_to_id=form.reply_to_id, content=form.content)
    return json_response(data_=chat)


@bp.route('/chats/<chat_id>/edit', methods=['POST'])
def edit_chat(chat_id):
    form = Edit()
    chat = ChatMgr(chat_id).edit(content=form.content)
    return json_response()


@bp.route('/chats/<chat_id>/delete', methods=['POST'])
@opt_perm(node='chats.delete')
def delete_chat(chat_id):
    ChatMgr(chat_id).delete()
    return json_response()
