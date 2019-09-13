# https://github.com/0xVikas/irc_relay
# Made for CRUx Round 2

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
        # Configuring the server for the clientprotocol (Proxy's client)
        # to send the data recieved from actual server
        self.factory.server = self

        if self.mainserver == None:
            get_site = b"Welcome!\nIRC Proxy - Made by Vikas\nEnter the IRC network address to connect :\nEx: /join irc.freenode.net\n\n"
            # Writes the above message to client
            self.transport.write(get_site)

    def dataReceived(self, data):
        # Redirect the data recieved from client to proxy's client
        if (self.client != None and self.mainserver != None):
            self.client.write(data)
        if self.mainserver == None and (b"JOIN" in data or b"join" in data):
            p = data.find(b"JOIN")
            self.mainserver = data[p+5:len(data)-2]
            print(b"Server set to : " + self.mainserver)
            reactor.connectTCP(self.mainserver, 6667, self.factory)

        # Appends all the data sent by client before
        # connecting to a network to self.buffer
        if self.mainserver == None and (b"JOIN" not in data or b"join" not in data):
            print("Adding to buffer: " + str(data))
            self.buffer += data

    def write(self, data):
        print("Data recieved from server: " + str(data))
        self.transport.write(data)

class ClientProtocol(protocol.Protocol):
    def connectionMade(self):
        # Setting the Client for the server protocol
        self.factory.server.client = self
        print("writing to server : " + str(self.factory.server.buffer))
        self.write(self.factory.server.buffer)
        # Clear the buffer once it is sent
        self.factory.server.buffer = ''

    def dataReceived(self, data):
        # Redirect the data recieved from mainserver
        # to the proxy's server
        self.factory.server.write(data)

    def write(self, data):
        print("Sending data as proxy: " + str(data))
        self.transport.write(data)

wordsRealm = service.InMemoryWordsRealm(None)
myportal = portal.Portal(wordsRealm)
factory = service.IRCFactory(wordsRealm, myportal)
factory.protocol = ircServerProtocol
# starts listening on the port 6667
reactor.listenTCP(6667, factory)
reactor.run()