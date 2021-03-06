__all__ = ['OneDrive']

from .graph_api import Graph
from .index import Index


class OneDrive():
    app = None

    def __init__(self, app=None):
        self.app = None
        self.api = None
        self.drive_id = ''
        self.folders = dict()

        if app is not None:
            self.init_app(app)

    def init_app(self, app) -> None:
        self.app = app
        config = app.config.get_namespace('ONEDRIVE_')
        self.api = Graph(config)
        self.index = Index(config, self.api)

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['onedrive'] = self

    def get_shared_item_info(self, share_id):
        r = self.api.get(f'/shares/{share_id}/driveItem')

        i = dict()
        i['id'] = r['id']
        i['drive_id'] = r['parentReference']['driveId']
        i['name'] = r['name'].lower()
        i['mime'] = r['file']['mimeType']
        i['sha1'] = r['file']['hashes']['sha1Hash']
        i['last_modify'] = r['fileSystemInfo']['lastModifiedDateTime']

        if 'image' in r:
            i['metainfo'] = r['image'].copy()
        elif 'audio' in r:
            i['metainfo'] = r['audio'].copy()
        elif 'video' in r:
            i['metainfo'] = r['video'].copy()

        return i

    def copy_from_share(self, drive_id, item_id, name):
        r = self.api.post(
            req=f'/drives/{drive_id}/items/{item_id}/copy',
            data={
                'parentReference': self.index.get_folder_ref(name),
                'name': name
            },
        )
        r = self.api.get(f'/me/drive/root:/{self.index.get_folder(name)}/{name}')
        return r['id']

    def share(self, item_id: str) -> str:
        r = self.api.post(req=f'/me/drive/items/{item_id}/createLink',
                          data={
                              'type': 'view',
                              'scope': 'anonymous'
                          })
        return r['shareId']

    def delete(self, item_id: str) -> bool:
        self.api.delete(f'/me/drive/items/{item_id}')
        return True
