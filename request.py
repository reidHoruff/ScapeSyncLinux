import urllib
import urllib2
from urllib2 import URLError, HTTPError
import os
import json
import settings
import gui

def dict_by_attr(dicts, val):
	dict_out = {}

	for d in dicts:
		dict_out[d[val]] = d

	return dict_out

class Request:

	def __init__(self, persistence_data):
		self.persistence_data = persistence_data

		#callbacks
		self.download_image_callbacks = []
		self.media_change_callbacks = []
		self.connection_error_callbacks = []

	'''
	def parse_response(self, data):
		if data['success']:
			print 'Username: %s' % data['username']

			print "Owned Albums:"
			for album in data['owned_albums']:
				print "\t%s (%s)" % (album['album_name'], album['num_photos'])

				for pic in album['album_photos']:
					print "\t\t %s : %s : %s" % (pic['slug'], pic['filename'], pic['original_url'])

			print "Watched Albums:"
			for album in data['watched_albums']:
				print "\t%s (%s)" % (album['album_name'], album['num_photos'])

				for pic in album['album_photos']:
					print "\t\t %s : %s : %s" % (pic['slug'], pic['filename'], pic['original_url'])
		else:
			print data['error']
	'''

	def connect_to_server(self):
		self.persistence_data['login_success'] = False

		if not self.persistence_data['registered']:
			return False

		request_data = {
			'username': self.persistence_data['username'],
			'password': self.persistence_data['password'],
			'computer_name': settings.COMPUTER_NAME,
			'computer_username': settings.COMPUTER_USERNAME,
			'app_version': settings.VERSION,
			'app_name': settings.APP_NAME,
		}

		try:
			response = urllib2.urlopen(settings.API_URL, urllib.urlencode(request_data))

		except URLError, error:
			print 'Connection Error: %s' % (error.code)
			alert_connection_error_callbacks()
			return False

		except:
			print 'Unknown error during server connection'
			alert_connection_error_callbacks()
			return False

		try:
			data = json.loads(response.read())
		except:
			print 'Unable to parse server response'
			alert_connection_error_callbacks()
			return False

		if data['success']:
			self.persistence_data['login_success'] = True
			print 'Login Successful!'
			return data

		else:
			persistence.set('login_success', False)
			print 'Login Failure:'
			print 'Error: %s' % (data['error'])
			alert_connection_error_callbacks()
			return False


	def download_image(self, url, dest):
		print 'downloading image from %s to %s' % (url, dest)

		try:
			image = urllib.urlopen(url).read()
		except:
			print 'Unbale to open image @ %s' % (url)
			return False

		try:
			file = open(dest, 'wb')
			file.write(image)
			file.close()

		except:
			print 'Error writing image to file'
			return False

		return True

	def sync(self):
		data = self.connect_to_server()

		if not data: return False

		server_photos = data['all_photos']
		server_photos_by_slug = dict_by_attr(server_photos, 'slug')
		server_slugs = set([photo['slug'] for photo in server_photos])
		server_filenames = set([photo['filename'] for photo in server_photos])

		last_sync_photos = set(self.persistence_data['all_photos'])
		last_sync_slugs = set([photo['slug'] for photo in last_sync_photos])
		last_sync_filenames = set([photo['filename'] for photo in last_sync_photos])

		#create media dir if not exists
		if not os.path.exists(self.persistence_data['media_dir']):
			os.makedirs(self.persistence_data['media_dir'])

		existing_filenames = set(os.listdir(self.persistence_data['media_dir']))

		filenames_to_download = server_filenames - existing_filenames
		filenames_to_delete = last_sync_filenames - server_filenames

		if len(filenames_to_download) > 0:
			self.alert_image_download_callback(len(filenames_to_download))

		for filename in filenames_to_download:
			src_url = filter(lambda x: x['filename'] is filename, server_photos)[0]['original_url']
			dest_url = os.path.join(self.persistence_data['media_dir'], filename)

			self.download_image(src_url, dest_url)

		if self.persistence_data['remove_wallpaper']:
			self.delete_files(filenames_to_delete)

		#self.persistence_data.lock('foo')
		self.persistence_data['all_photos'] = server_photos
		self.persistence_data['owned_albums'] = data['owned_albums']
		self.persistence_data['watched_albums'] = data['watched_albums']
		self.persistence_data.save()
		#self.persistence_data.unlock('foo')

	def delete_files(self, filenames):

		for filename in filenames:
			path = os.path.join(self.persistence_data['media_dir'], filename)
			print 'deleting', path

			try:
				os.remove(path)
			except:
				print 'unable to delete file', path
				pass

	def register_image_download_callback(self, callback):
		self.download_image_callbacks.append(callback)

	def alert_image_download_callback(self, num_images=1):
		for cb in self.download_image_callbacks:
			cb(num_images)

	def register_media_change_callback(self, callback):
		self.media_change_callbacks += callback

	def register_connection_error_callbacks(self, callback):
		self.connection_error_callbacks += callback

	def alert_connection_error_callbacks(self, message='Unable to conenct to Server'):
		for cb in self.connection_error_callbacks:
			cb(message)

