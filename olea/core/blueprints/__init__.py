def register_blueprints(app):
    from werkzeug.utils import find_modules, import_string

    for module_str in find_modules(__name__, include_packages=True):
        module = import_string(module_str)
        if not hasattr(module, 'bp'):
            continue

        import_string(f'{module_str}.views')
        app.register_blueprint(module.bp)
