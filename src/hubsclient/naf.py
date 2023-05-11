import json
import time


class NAF:
    def __init__(
        self,
        network_id,
        owner_id,
        creator_id=None,
        template=None,
        persistent=False,
        parent=None,
        components=[],
    ):
        self.network_id = network_id
        self.owner_id = owner_id
        self.creator_id = creator_id or owner_id
        self.last_owner_time = time.time()
        self.template = template
        self.persistent = persistent
        self.parent = parent
        self.components = components
        self.is_first_sync = True

    def to_json(self):
        self.last_owner_time = time.time()
        data = {
            "networkId": self.network_id,
            "owner": self.owner_id,
            "creator": self.creator_id,
            "lastOwnerTime": self.last_owner_time,
            "template": self.template,
            "persistent": self.persistent,
            "parent": self.parent,
            "components": self.components,
            "isFirstSync": self.is_first_sync,
        }
        self.is_first_sync = False
        return json.dumps(data)
