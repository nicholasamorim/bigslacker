# -*- coding: utf-8 -*-
import time
from slackclient import SlackClient


class BasePlugin(object):
    """Every plugin should inherit from this.
    """
    pass


class BigSlacker(object):
    """Main (and pretty much only) functional class. Instantiate it
    and start slacking around.

    If you want to use it with GEvent,  you just need to monkeypatch it.

    ```
    from gevent import monkey
    monkey.patch_all()
    ```

    """
    def __init__(self, token, ping_interval=3, client=None, **kwargs):
        """
        :param token: The slack API token.
        :param ping_interval: The interval in seconds we should ping Slack
        server to keep the connection alive.
        :param client: By default, BigSlacker uses Slack official Python
        client, but you can pass any other client here, provided it has
        the same interface.
        :param process_plugin_return: Defaults to True.
        This process the output (return) of a plugin function we call as a
        message to send. Therefore making it easy to "reply" to events.
        If the plugin method returns None we do nothing.
        Returning [(channel, message)] will make us send it. You can return one
        or more messages.
        :param sleeping_time: Every time we read data from the WebSocket we
        sleep 1 second by default. If you have a different need, you can
        override this setting.
        """

        self.client = client or SlackClient(token)
        self.ping_interval = ping_interval
        self.process_plugin_return = kwargs.get('process_plugin_return', True)
        self._injected_plugins = []
        self._last_call = None
        self._sleeping_time = kwargs.get('sleeping_time', 1)
        self._custom_callbacks = {}
        self._load_plugins()

    def _load_plugins(self):
        """Load plugin classes list by looking for subclasses of
        `BasePlugin`.
        """
        self._plugins = [cls() for cls in BasePlugin.__subclasses__()]

    def slack(self):
        """Starts slacking (listening).

        Does nothing but call the plugins and ping - what a slacker.

        It calls the plugin in a simple way. An event is received,
        let's suppose the event is channel_created. It will simply
        iterate over all plugins and look for a method
        called "channel_created" and call it passing the data.

        If the plugin has a "catch_all" method, every single event
        will be sent to it.
        """
        self.client.rtm_connect()
        while True:
            data = self.client.rtm_read()
            for event in data:
                event_type = event.get('type', None)
                for plugin in self._plugins:
                    if event_type and hasattr(plugin, event_type):
                        event_func = getattr(plugin, event_type)
                        self._callback_send(event_func(event))

                    catch_all_func = getattr(plugin, 'catch_all', None)
                    if catch_all_func is not None:
                        self._callback_send(catch_all_func(event))

            self.ping()
            time.sleep(1)

    def ping(self):
        """Pings the Slack server if needed. The interval is set
        at the variable ping_interval. Defaults to 3 seconds.
        """
        if self._last_call is None:
            self._last_call = time.time()
            return

        now = int(time.time())
        if now > (self._last_call + self.ping_interval):
            self.client.server.ping()
            self._last_call = now

    def send_message(self, channel, text):
        """Sends a message to the specified channel.

        :param channel: Channel ID. Name soon to be supported.
        :param text: The message to be sent.
        """
        return self.client.rtm_send_message(channel, text)

    def api_call(self, *args, **kwargs):
        """Exposes Slack Web API interface.
        """
        return self.client.api_call(*args, **kwargs)

    def _callback_send(self, messages):
        """Convenience function that deals with the return values
        of the plugin calls.

        :param messages: An iterable of messages following the format
        [(channel, message)].
        """
        if messages is None:
            return

        for channel, text in messages:
            self.send_message(channel, text)
