# -*- coding: utf-8 -*-
"""Base IRC Bot that abstracts the boilerplate from the actual logic."""

import irc.client
import irc.bot as ircbot
import sys

import masterbot


CHAN = "#{chan}"

DEFAULT_PORT = 6667

NICK = "MasterBot"
WHOIS = "Mastermind Bot hosted by Traklon."


class IRCBot(ircbot.SingleServerIRCBot):
    """Connection to the IRC server. Receives and sends messages.

    The purpose of this class is to abstract some of the ircbot/lib framework
    into one place, like the updates of the server and the environement.

    This bot on itself doesn't do anything. To make it be useful, you have to
    create another class to put the logic in, implement the event functions
    (on_join, on_pubmsg...) and pass its instance to the IRCBot. This way, it
    can call the actual logic after dealing with the boilerplate.
    """

    def __init__(self, bot):
        """Connects to the server and initializes the internal state."""
        server = sys.argv[1]
        if len(sys.argv) == 3:
            port = DEFAULT_PORT
        else:
            port = sys.argv[3]

        ircbot.SingleServerIRCBot.__init__(self, [(server, port)], NICK, WHOIS)

        self._chan = CHAN.format(chan=sys.argv[2])

        self._serv = None
        self._ev = None

        self._bot = bot

    def _UpdateServAndEv(self, serv, ev):
        """Updates the global variables about connection and environment."""
        self._serv = serv
        self._ev = ev

    def GetAuthor(self):
        """Returns the nickname of the author of the latest message."""
        return irc.client.nm_to_n(self._ev.source())

    def GetMessage(self):
        """Returns the latest message."""
        return self._ev.arguments[0].lower()

    def SendMessage(self, message, message_to=None):
        """Sends a message to a specific user or to the whole chan."""
        message_to = message_to or self._chan
        self._serv.privmsg(message_to, message)

    def on_welcome(self, serv, ev):
        """Joins a chan."""
        self._UpdateServAndEv(serv, ev)
        self._serv.join(self._chan)

    def on_join(self, serv, ev):
        self._UpdateServAndEv(serv, ev)
        self._bot.on_join(self)

    def on_privmsg(self, serv, ev):
        self._UpdateServAndEv(serv, ev)
        self._bot.on_privmsg(self)

    def on_pubmsg(self, serv, ev):
        self._UpdateServAndEv(serv, ev)
        self._bot.on_pubmsg(self)


if __name__ == "__main__":
    IRCBot(masterbot.MasterBot()).start()
