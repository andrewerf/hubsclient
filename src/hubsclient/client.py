from websockets.sync.client import ClientConnection, connect as ws_connect
import json
from .avatar import Avatar
from .naf import NAF
from .utils import dataclass, field


@dataclass
class MSG:
    channel: int | None = None
    id: int | None = None
    target: str = ""
    cmd: str = ""
    data: object = field(default_factory=dict)

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
            [str(self.channel), str(self.id), self.target, self.cmd, self.data], default=lambda o: o.to_obj()
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
        """Hubs room client.

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
        self.avatar = Avatar(avatar_url=f"https://{host}/api/v1/avatar/{avatar_id}")
        self.msg_buf: list[MSG] = []
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
        self.send_cmd(8, f"hub:{self.room_id}", cmd, body)

    def send_naf(self, naf: NAF):
        """Send a NAF update.

        :param naf: NAF object
        """
        self.send8("naf", {"dataType": "u", "data": naf.to_obj()})

    def get_message(self, wait: bool = False) -> MSG:
        """Get a message from the socket.

        :param wait: Whether to block until a message is received
        :return: MSG
        """
        try:
            msg = self.sock.recv(None if wait else 0)
            msg = MSG.from_json(msg)
            self.msg_buf.append(msg)
            return msg
        except TimeoutError:
            return None

    def sync(self):
        while self.get_message():
            ...
        self.send_naf(self.avatar)

    def send_heartbeat(self):
        """Send a heartbeat."""
        self.send_cmd(None, "phoenix", "heartbeat", {})

    def _join(self):
        self.sock = ws_connect(self.url)
        # send first join msg
        self.send_cmd(5, "ret", "phx_join", {"hub_id": self.room_id})
        self.sid = self.get_message(wait=True).data["response"]["session_id"]
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
        self.sessinfo = self.get_message(wait=True).data["response"]
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
        self.avatar.owner_id = self.sid
        self.sync()

    def close(self):
        """Close the connection."""
        self.sock.close()
        self.sock = None
        self.sid = None
        self.msg_buf = []
        self.mix = {}
