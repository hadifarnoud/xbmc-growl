#!/usr/bin/env python

__version__ = "0.1"
__author__ = "Jim Pingle (http://pingle.org)"
__copyright__ = "(C) 2011 Jim Pingle, original code (C) 2006 Rui Carmo. Code under BSD License."

import sys, os
from subprocess import call
from regrowl import GrowlPacket
from netgrowl import *
from SocketServer import *

password="openelec"

class GrowlListener(UDPServer):
# Hostname/IP to listen on. No automatic detection.
	hostname = '0.0.0.0'
	allow_reuse_address = True

	def __init__(self, inpassword = None, outpassword = None):
		self.inpassword = inpassword
		self.outpassword = outpassword
		UDPServer.__init__(self,(self.hostname, GROWL_UDP_PORT), _RequestHandler)
	# end def

	def server_close(self):
		self.resolver.shutdown()
	# end def
# end class

class _RequestHandler(DatagramRequestHandler):
	dialogtimeout = '5'
	growlpath = '/usr/bin/xbmc-send'
	icon='growl.png'

	def handle(self):
		p = GrowlPacket(self.rfile.read(), self.server.inpassword,self.server.outpassword)
		if p.type() == 'NOTIFY':
			notification,title,description,app = p.info()
			gtext = app + '\n' + notification + ': ' + description
			def notifyXbmc(action):
				    ip = "localhost"
				    port = 9777
				    addr = (ip, port)
				    sock = socket(AF_INET,SOCK_DGRAM)
				    packet = PacketACTION(actionmessage=action, actiontype=ACTION_BUTTON)
				    packet.send(sock, addr)

			#action="title, gtext, self.dialogtimeout, self.icon"
			action = "Notification(title, gtext, self.dialogtimeout, self.icon)"
			notifyXbmc(action)


if __name__ == "__main__":
	r = GrowlListener(password,password)
try:
	r.serve_forever()
except KeyboardInterrupt:
	r.server_close()