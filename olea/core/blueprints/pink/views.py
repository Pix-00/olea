from flask import g
from flask_json import json_response

from core.auth import allow_anonymous, opt_perm, perm

from . import bp
from .forms import AlterDuck, AlterScopes, AssignToken, Search, SearchDuck, SignUp, UpdateInfo
from .query import DuckQuery, PinkQuery
from .services import DuckMgr, PinkMgr


@bp.route('/<id_>', methods=['GET'])
@opt_perm()
def get_id(id_):
    pink = PinkQuery.single(id_)
    return json_response(data_=pink)


@bp.route('/', methods=['GET'])
@opt_perm()
def search():
    form = Search()
    pinks = PinkQuery.search(deps=form.deps, name=form.name, qq=form.qq)
    return pinks


@bp.route('/update-info', methods=['POST'])
def update_info():
    form = UpdateInfo()
    PinkMgr(g.pink_id).update_info(qq=form.qq, other=form.other)
    return json_response()


@bp.route('/assign-token', methods=['POST'])
@perm()
def assign_token():
    form = AssignToken()
    tokens = PinkMgr.assign_token(deps=form.deps, amount=form.amount)
    return json_response(data_=tokens)


@bp.route('/sign-up', methods=['POST'])
@allow_anonymous
def sign_up():
    form = SignUp()
    pink = PinkMgr.sign_up(
        name=form.name,
        pwd=form.pwd,
        qq=form.qq,
        other=form.other,
        email_token=form.token_email,
        deps_token=form.token_dep,
    )
    return json_response(id=pink.id)


@bp.route('/<id_>/deactivate', methods=['POST'])
@perm()
def deactivate(id_):
    PinkMgr(id_).deactivate()
    return json_response()


@bp.route('/ducks/', methods=['GET'])
@opt_perm(node='auth.duck')
def list_ducks():
    form = SearchDuck()
    ducks = DuckQuery.ducks(pink_id=form.pink_id,
                            node=form.node,
                            nodes=form.nodes,
                            allow=form.allow)
    return json_response(data_=ducks)


@bp.route('/<id_>/ducks/alter', methods=['POST'])
@perm(node='auth.duck')
def alter_duck(id_):
    form = AlterDuck()
    ducks, conflicts = PinkMgr(id_).alter_ducks(add=form.add, remove=form.remove)
    return json_response(ducks=ducks, conflicts=conflicts)


@bp.route('/<id_>/ducks/<node>/alter', methods=['POST'])
@perm(node='auth.duck')
def alter_scopes(id_, node):
    form = AlterScopes()
    duck = DuckMgr(id_, node)
    if form.method == AlterScopes.Method.diff:
        duck.add_scopes(scopes=form.positive)
        final = duck.remove_scopes(scopes=form.negative)
    else:
        final = duck.modi_scopes(scopes=form.positive)
    return json_response(new_scopes=final)
