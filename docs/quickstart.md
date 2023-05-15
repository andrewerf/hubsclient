# Quickstart

This quickstart guide will show you how to use the `hubsclient` library to interact
with a Hubs room. We assume that you have already installed the library with pip.

## Joining a room

To join a room, you need to know the room's url. If you haven't already, create a new
room on the public Hubs instance at
[https://hubs.mozilla.com/demo](https://hubs.mozilla.com/demo). Once you have created
a room, your URL will look something like this:
`https://hubs.mozilla.com/waycoA2/obedient-best-get-together`. The room id is the
part immediately after the domain name, in this case `waycoA2`.

In addition to the room id, you will need information about your avatar, such as the
name you want to use and the id of the avatar model. We'll explain how to get this
information in a later section, but for now, let's use the
[base bot](https://hubs.mozilla.com/api/v1/avatars/basebot) avatar. This avatar has
the id `basebot`. We can set our display name to something like `Python User`.

Now that we have our room id and our avatar info, we can instantiate a client and
join the room:

```python
from hubsclient import HubsClient

client = HubsClient(
    host="hubs.mozilla.com",
    room_id="waycoA2",
    avatar_id="basebot",
    display_name="Python User",
)
```

The client will automatically join the room and start listening for events.

## Moving around

Now that we have joined the room, we can move around by setting the `position` and
`rotation` attributes of the client.

Let's advance the client's position on the x-axis by 1 meter:

```python
client.position.x += 1
```

We can also rotate the client by 90 degrees:

```python
client.rotation.y = 90
```

In order to see the changes, we need to send the new position and rotation to the
server by calling the `sync` method:

```python
client.sync()
```

## More avatar features

The client has a number of other attributes that can be used to control the avatar.
For example, we adjust the position and rotation of the avatar's head:

```python
client.head_transform.position.y -= 0.1
client.head_transform.rotation.x = 20
client.sync()
```

We can also manipulate the avatar's hands:

Lets make the left hand visible and move it to the left of the avatar's head:

```python
client.left_hand.visible = True
client.left_hand.position.x = -0.5
client.sync()
```

Now, we can make it show a thumbs up:

```python
from hubsclient.avatar import HandPose
client.left_hand.gesture = HandPose.thumbsUp
client.sync()
```

## Sending messages

We can send messages to other users in the room by calling the `send_chat` method:

```python
client.send_chat("Hello everyone!")
```

## Leaving the room

When you are done, you can leave the room by calling the `close` method:

```python
client.close()
```

## Going further

Read the [API docs](apidocs/index) for more information about the library's features.
