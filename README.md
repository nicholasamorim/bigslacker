bigslacker - Slack big while having a bot
==========================================

Overview
---------

bigslacker tries to be faithful to its name. It is a Bot for Slack that allows you to plug plugins (!) the easiest possible way. All you have to do is define a class that inherits from BasePlugin and define methods for the events.

Supports Python 2 and 3.

Installation
---------------

#### Via PIP

    pip install bigslacker

#### Manual

    git clone https://github.com/nicholasamorim/bigslacker.git
    python setup.py install

So far it has only one dependency, which is the official [slackclient](https://github.com/slackhq/python-slackclient).

Example
---------

##### Creating a Bot with a plugin to listen on channel_created only

```python
from bigslacker import BigSlacker, BasePlugin

class ChannelAnnouncer(BasePlugin):
    def channel_created(self, data):
        print('I see a channel is created, gonna do something')

token = '1239182918sxxusus'
bs = BigSlacker(token)
bs.slack()
```

You don't have to do anything to register a plugin but inherit it from BasePlugin.


##### Sending a message back

We analyze every returned data from any Plugin we call. If you return None we do nothing.
However, if you reply with [(channel, message)], we will automatically send that message
to the specified channel.

```python
from bigslacker import BigSlacker, BasePlugin

class ChannelAnnouncer(BasePlugin):
    def channel_created(self, data):
        print('I see a channel is created, gonna reply')
        return [('C1K4BBY8L', 'Hey guys, a channel has been created...')]

token = '1239182918sxxusus'
bs = BigSlacker(token)
bs.slack()
```

Of course, if you add more elements to the list, we will also send those messages.


##### I want every event in a single function

Sure. Just define a `catch_all` method.

```python
from bigslacker import BigSlacker, BasePlugin

class ChannelAnnouncer(BasePlugin):
    def catch_all(self, data):
        print('gonna inspect that data...')

token = '1239182918sxxusus'
bs = BigSlacker(token)
bs.slack()
```


##### Can I use GEvent ?

Yes, all you have to do is monkey-patch it before on your application. Nothing else changes.


```python
from gevent import monkey
monkey.patch_all()
```

##### Can I call the Slack API from it?

Yes, we expose the interface. So just call api_call on it as usual.

```python
from bigslacker import BigSlacker

token = '1239182918sxxusus'
bs = BigSlacker(token)
bs.api_call("api.test")
bs.slack()
```
