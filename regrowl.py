#!/usr/bin/env python
#
# ReGrowl Server
# A simple ? server for *regrowling* GNTP messages to the local OSX Growl system

import SocketServer
import traceback
import logging

import gntp_bridge as gntp


class GNTPServer(SocketServer.TCPServer):
	def __init__(self, options, RequestHandlerClass):
		try:
			SocketServer.TCPServer.__init__(self, (options.host, options.port), RequestHandlerClass)
		except:
			logging.getLogger('Server').critical('There is already a server running on port %d'%options.port)
			exit(1)
		self.options = options
		logging.getLogger('Server').info('Activating server')
	def run(self):
		try:
			sa = self.socket.getsockname()
			logging.getLogger('Server').info('Listening for GNTP on %s port %s'%(sa[0],sa[1]))
			self.serve_forever()
		except KeyboardInterrupt:
			self.__serving = False

class GNTPHandler(SocketServer.StreamRequestHandler):
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
	def write(self,msg):
		logging.getLogger('Server').debug(msg)
		self.request.sendall(msg)
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
		
		pprint(message)
		
if __name__ == "__main__":
	from Parser import ServerParser
	
	(options,args) = ServerParser().parse_args()
	
	try: 
		import setproctitle
		setproctitle.setproctitle('regrowl-server')
	except ImportError:
		pass
	logging.basicConfig(level=logging.DEBUG,
		format='%(name)-12s: %(levelname)-8s %(message)s',
		datefmt='%m-%d %H:%M',
		filename=options.log)
	
	console = logging.StreamHandler()
	console.setLevel(logging.INFO)
	formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
	console.setFormatter(formatter)
	logging.getLogger('').addHandler(console)
	
	server = GNTPServer(options, GNTPHandler)
	server.run()