from websockets.sync.client import ClientConnection, connect as ws_connect
import json


class MSG:
    def __init__(
        self,
        channel: int = None,
        id: int = None,
        target: str = None,
        cmd: str = None,
        data: object = None,
    ):
        """Hubs channel message.

        :param channel: Channel number
        :param id: Message index
        :param target: Channel target
        :param cmd: Command
        :param data: Payload body
        """
        self.channel = int(channel)
        self.id = int(id)
        self.target = target
        self.cmd = cmd
        self.data = data

    @classmethod
    def from_json(cls, json_str: str) -> "MSG":
        """Parse JSON message.

        :param json_str: JSON string
        :return: MSG
        """
        return cls(*json.loads(json_str))

    def to_json(self) -> str:
        """Convert to JSON string.

        :return: JSON string
        """
        return json.dumps(
            [str(self.ch), str(self.id), self.target, self.cmd, self.data]
        )

    __str__ = to_json


class HubsClient:
    def __init__(
        self,
        host: str,
        room_id: str,
        avatar_id: str = None,
        display_name: str = "API Client",
    ):
        """
        Hubs room client.
        :param host: The host of the room, e.g. "hubs.mozilla.com"
        :param room_id: The hub room ID code
        :param avatar_id: The avatar ID
        :param display_name: The display name for the avatar
        """
        self.host = host
        self.url = f"wss://{host}/socket/websocket?vsn=2.0.0"
        self.sock: ClientConnection = None
        self.mix: dict[int, int] = {}
        self.room_id = room_id
        self.display_name = display_name
        self.avatar_id = avatar_id
        self.sid: str = None
        self._join()

    def send_cmd(self, ch, tgt, cmd, body):
        """Send a command to a channel.

        :param ch: Channel number
        :param tgt: Channel target
        :param cmd: Command
        :param body: Payload body
        """
        # increment message index
        # hack to get around null, null
        self.mix[ch] = ch and (self.mix.get(ch, ch - 1) + 1)
        self.sock.send(MSG(ch, self.mix[ch], tgt, cmd, body).to_json())

    def send8(self, cmd: str, body: dict):
        """Send a command on channel 8, resource update.

        :param cmd: Command
        :param body: Payload body
        """
        self.send_cmd(8, f"hub:{self.roomID}", cmd, body)
    
    def sendHeartbeat(self):
        """Send a heartbeat."""
        self.send_cmd(0, "phoenix", "heartbeat", {})

    def _join(self):
        self.sock = ws_connect(self.url)
        # send first join msg
        self.send_cmd(5, "ret", "phx_join", {"hub_id": self.roomID})
        self.sid = MSG.from_json(self.sock.recv()).body["response"]["session_id"]
        # setup profile
        self.send8(
            "phx_join",
            {
                "profile": {
                    "avatarId": self.avatar_id,
                    "displayName": self.display_name,
                },
                "push_subscription_endpoint": None,
                "auth_token": None,
                "perms_token": None,
                "context": {"mobile": False, "embed": False, "hmd": False},
                "hub_invite_id": None,
            },
        )
        # enter room
        self.send8(
            "events:entered",
            {
                "isNewDaily": False,
                "isNewMonthly": False,
                "isNewDayWindow": False,
                "isNewMonthWindow": False,
                "initialOccupantCount": 0,
                "entryDisplayType": "Headless",
                "userAgent": "Python",
            },
        )

    def close(self):
        """Close the connection."""
        self.sock.close()
        self.sock = None
        self.mix = {}
