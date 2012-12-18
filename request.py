'''
handles direct communication with the server
loggin in, fetching api data, downloading images etc.
'''
import urllib
import urllib2
from urllib2 import URLError, HTTPError
import json
import settings

class Request:

	def __init__(self, persistence_data):
		pass

	def connect_to_server(self, username, password):

		request_data = {
			'username': username,
			'password': password,
			'computer_name': settings.COMPUTER_NAME,
			'computer_username': settings.COMPUTER_USERNAME,
			'app_version': settings.VERSION,
			'app_name': settings.APP_NAME,
		}

		try:
			response = urllib2.urlopen(settings.API_URL, urllib.urlencode(request_data))

		except URLError, error:
			print 'Connection Error: %s' % (error.code)
			return False

		except:
			print 'Unknown error during server connection'
			return False

		try:
			data = json.loads(response.read())
		except:
			print 'Unable to parse server response'
			return False

		if data['success']:
			#print 'Login Successful!'
			return data

		else:
			print 'Login Failure:'
			print 'Error: %s' % (data['error'])
			return False


	def download_image(self, src_uri, dest_uri):
		print 'downloading image from %s to %s' % (src_uri, dest_uri)

		try:
			image = urllib.urlopen(src_uri).read()
		except:
			print 'Unbale to open image @ %s' % (src_uri)
			return False

		try:
			mfile = open(dest_uri, 'wb')
			mfile.write(image)
			mfile.close()

		except:
			print 'Error writing image to file'
			return False

		return True