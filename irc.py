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
        self.buffer = ""
        self.client = None
        self.factory = None

    def connectionMade(self):
        self.factory = protocol.ClientFactory()
        self.factory.protocol = ClientProtocol
        self.factory.server = self

        if self.mainserver == None:
            get_site = "Welcome!\nIRC Proxy - Made by Vikas\nEnter the IRC network address to connect :\nEx: /join irc.freenode.net\n\n"
            self.transport.write(get_site)

    def dataReceived(self, data):
        if (self.client != None and self.mainserver != None):
            self.client.write(data)
        if self.mainserver == None and ("JOIN" in data or "join" in data):
            p = data.find("JOIN")
            self.mainserver = data[p+5:len(data)-2]
            print "Server set to : " + self.mainserver
            reactor.connectTCP(self.mainserver, 6667, self.factory)

        if self.mainserver == None and ("JOIN" not in data or "join" not in data):
            print "Adding to buffer: " + data
            self.buffer += data

    def write(self, data):
        print "Data recieved from server: " + data
        self.transport.write(data)

class ClientProtocol(protocol.Protocol):
    def connectionMade(self):
        self.factory.server.client = self
        print "writing to server : " + self.factory.server.buffer
        self.write(self.factory.server.buffer)
        self.factory.server.buffer = ''

    def dataReceived(self, data):
        self.factory.server.write(data)

    def write(self, data):
        print "Sending data as proxy: " + data
        self.transport.write(data)

wordsRealm = service.InMemoryWordsRealm(None)
myportal = portal.Portal(wordsRealm)
factory = service.IRCFactory(wordsRealm, myportal)
factory.protocol = ircServerProtocol
reactor.listenTCP(6667, factory)
reactor.run()