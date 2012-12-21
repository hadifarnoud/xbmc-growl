#!/usr/bin/env python

__version__ = "0.2"
__author__ = "Hadi Farnoud (http://hadifarnoud.com)"
__copyright__ = "(C) 2012 Hadi Farnoud. Original code (C) 2006 Rui Carmo. modified by Jim Pingle 2011. Code under BSD License."

import sys, os
from subprocess import call
from regrowl import *
from netgrowl import *
from SocketServer import *
from xbmc.xbmcclient import *

password="openelec"

class GrowlListener(UDPServer):
# Hostname/IP to listen on. No automatic detection.
	hostname = '192.168.1.3'
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

class GNTPHandler(SocketServer.StreamRequestHandler):
	dialogtimeout = '5'
	growlpath = '/usr/bin/xbmc-send'
	icon='growl.png'

#	def handle(self):
#		p = GrowlPacket(self.rfile.read(), self.server.inpassword,self.server.outpassword)
#		if p.type() == 'NOTIFY':
#			notification,title,description,app = p.info()
#			gtext = app + '\n' + notification + ': ' + description
#			action = 'Notification(%s,%s,%s,%s)' % (title, gtext, self.dialogtimeout, self.icon)
#			self.notifyXbmc(action)

	def read(self):
		bufferLength = 2048
		buffer = ''
		while(1):
			data = self.request.recv(bufferLength)
			logging.getLogger('Server').debug('Reading %s Bytes',len(data))
			buffer = buffer + data
			if len(data) < bufferLength and buffer.endswith('\r\n\r\n'):
				break
		logging.getLogger('Server').debug(buffer)
		return buffer
	def handle(self):
		logger = logging.getLogger('Server')
		reload(gntp)
		self.data = self.read()
		try:
			message = gntp.parse_gntp(self.data,self.server.options.password)
		
			response = gntp.GNTPOK(action=message.info['messagetype'])
			if message.info['messagetype'] == 'NOTICE':
				response.add_header('Notification-ID','')
			elif message.info['messagetype'] == 'SUBSCRIBE':
				raise gntp.UnsupportedError()
				#response.add_header('Subscription-TTL','10')
			self.write(response.encode())
		except gntp.BaseError, e:
			logger.exception('GNTP Error')
			if e.gntp_error:
				self.write(e.gntp_error())
		except:
			logger.exception('Unknown Error')
			error = gntp.GNTPError(errorcode=500,errordesc='Unknown server error')
			self.write(error.encode())
			raise
	
		message.send()




    	def notifyXbmc(self, action):
		ip = "localhost"
		port = 9777
		addr = (ip, port)
		sock = socket(AF_INET,SOCK_DGRAM)
		packet = PacketACTION(actionmessage=action, actiontype=ACTION_BUTTON)
		packet.send(sock, addr)

if __name__ == "__main__":
	r = GrowlListener(password,password)
	try:
		r.serve_forever()
	except KeyboardInterrupt:
		r.server_close()