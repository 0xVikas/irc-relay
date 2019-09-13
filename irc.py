# https://github.com/0xVikas/irc_relay
# Made for CRUx Round 2
# Requires python 2.X

import sys
from twisted.internet import protocol, reactor
from twisted.words.protocols import irc
from twisted.words import service
from twisted.words.protocols.irc import IRC
from twisted.cred import portal

class ircServerProtocol(IRC, protocol.Protocol):
    def __init__(self):
        self.mainserver = None
        self.buffer = b""
        self.client = None
        self.factory = None

    def connectionMade(self):
        self.factory = protocol.ClientFactory()
        self.factory.protocol = ClientProtocol
        self.factory.server = self

        if self.mainserver == None:
            get_site = b"Welcome!\nIRC Proxy - Made by Vikas\nEnter the IRC network address to connect :\nEx: /join irc.freenode.net\n\n"
            self.transport.write(get_site)

    def dataReceived(self, data):
        if (self.client != None and self.mainserver != None):
            self.client.write(data)
        if self.mainserver == None and (b"JOIN" in data or b"join" in data):
            p = data.find(b"JOIN")
            self.mainserver = data[p+5:len(data)-2]
            print(b"Server set to : " + self.mainserver)
            reactor.connectTCP(self.mainserver, 6667, self.factory)

        if self.mainserver == None and (b"JOIN" not in data or b"join" not in data):
            print("Adding to buffer: " + str(data))
            self.buffer += data

    def write(self, data):
        print("Data recieved from server: " + str(data))
        self.transport.write(data)

class ClientProtocol(protocol.Protocol):
    def connectionMade(self):
        self.factory.server.client = self
        print("writing to server : " + str(self.factory.server.buffer))
        self.write(self.factory.server.buffer)
        self.factory.server.buffer = ''

    def dataReceived(self, data):
        self.factory.server.write(data)

    def write(self, data):
        print("Sending data as proxy: " + str(data))
        self.transport.write(data)

wordsRealm = service.InMemoryWordsRealm(None)
myportal = portal.Portal(wordsRealm)
factory = service.IRCFactory(wordsRealm, myportal)
factory.protocol = ircServerProtocol
reactor.listenTCP(6667, factory)
reactor.run()