import persistence
import request
import ScapeSyncORM
import os
import time
import threading
import settings
import datetime

class ScapeSync(threading.Thread):

	def __init__(self, wp_manager):
		threading.Thread.__init__(self)

		self.wp_manager = wp_manager

		self.pdata = persistence.Persistence()
		self.request = request.Request(self.pdata)

		#ORMs
		self.last_sync_orm = ScapeSyncORM.ScapeSyncORM()
		self.server_data_orm = ScapeSyncORM.ScapeSyncORM()
		self.media_dir_orm = ScapeSyncORM.ScapeSyncORM()

		#callbacks
		self.image_download_callbacks = []
		self.album_download_callbacks = []
		self.post_sync_callbacks = []
		self.image_delete_callbacks = []

		self.pdata.attach_presave_callback(self.presave_actions)

		self.sync_requested = False
		self.quit_requested = False
		self.is_syncing = False

	def __update_last_sync_orm(self):
		self.last_sync_orm.clear()
		self.last_sync_orm.add_from_persistence_dict(self.pdata['media'])

	def logout(self):
		self.pdata['username'] = ''
		self.pdata['password'] = ''
		self.pdata['registered'] = False
		self.pdata['login_success'] = False
		self.pdata.save()

	def request_sync(self):
		self.sync_requested = True

	def request_quit(self):
		self.quit_requested = True

	def can_log_in(self, username=None, password=None):

		if username and password:
			self.pdata['username'] = username
			self.pdata['password'] = password
			self.pdata['registered'] = True
			self.pdata.save()

		if not self.pdata['registered']: return False

		self.pdata['login_success'] = False

		data = self.request.connect_to_server(
			username=self.pdata['username'],
			password=self.pdata['password']
		)

		if data:
			self.pdata['login_success'] = True

		self.pdata.save()
		return self.pdata['login_success']

	def run(self):
		print 'scape sync thread started'

		self.deamon_seconds_running = 0

		while not self.quit_requested:
			should_autosync = self.pdata['registered'] and self.pdata['autoupdate'] and self.deamon_seconds_running % self.pdata['server_ping_interval_s'] == 0
			
			if should_autosync or self.sync_requested:
				self.is_syncing = True
				self.__sync()
				self.update_wallpaper()


			self.is_syncing = False
			self.sync_requested = False
			self.deamon_seconds_running += settings.DEAMON_INTERVAL_S
			time.sleep(settings.DEAMON_INTERVAL_S)

		print 'quit requested:', self.quit_requested
		print 'thread exiting'

	def __sync(self):

		if not self.pdata['registered']: return False

		print 'connecting to server...'

		data = self.request.connect_to_server(
			username=self.pdata['username'],
			password=self.pdata['password']
		)

		if not data:
			self.pdata['login_success'] = False
			self.pdata.save()
			return False

		self.pdata['login_success'] = True

		self.__update_last_sync_orm()

		self.server_data_orm.clear()
		self.server_data_orm.add_from_api_1_0_dict(data)

		self.media_dir_orm.clear()
		self.media_dir_orm.add_from_media_dir(self.pdata['media_dir'])

		#diffs
		images_to_download = self.server_data_orm.images - self.media_dir_orm.images
		images_to_delete = self.last_sync_orm.images - self.server_data_orm.images
		albums_added = self.server_data_orm.albums - self.last_sync_orm.albums
		albums_removed = self.last_sync_orm.albums - self.server_data_orm.albums

		#download new images
		if len(images_to_download) > 0:
			self.alert_image_download_callbacks(len(images_to_download))

			for image in images_to_download:
				self.request.download_image(
					src_uri=image.original_url,
					dest_uri=os.path.join(self.pdata['media_dir'], image.filename)
				)
				time.sleep(self.pdata['image_download_delay_s'])

		#delete old wallpaper
		if self.pdata['remove_wallpaper'] and len(images_to_delete) > 0:
			self.alert_image_delete_callbacks(len(images_to_delete))

			for image in images_to_delete:
				path = os.path.join(self.pdata['media_dir'], image.filename)
				print 'deleting', path
				os.remove(path)

		if len(albums_added) > 0:
			self.alert_album_download_callbacks(len(albums_added))

		self.server_data_orm.apply_displayed_filter(self.last_sync_orm)
		self.pdata['media'] = self.server_data_orm.to_dict()
		self.__update_last_sync_orm()

		#post sync callback
		self.alert_post_sync_callbacks(**{
			'images_downloaded': len(images_to_download), 
			'albums_downloaded': len(albums_added),
			'images_deleted': len(images_to_delete),
			'albums_removed': len(albums_removed),
		})

	def update_wallpaper(self):
		images_to_display = set()

		for album in self.last_sync_orm.albums:
			if album.is_displayed:
				images_to_display |= album.images

		uris = map(lambda image: os.path.join(self.pdata['media_dir'], image.filename), images_to_display)


		displayed_photos_hash = hash('$'.join(sorted(uris)) + str(self.pdata['static_duration']) + str(self.pdata['transition_duration']))

		if displayed_photos_hash != self.pdata['displayed_photos_hash']:
			print 'updating wallpaper slideshow'

			self.wp_manager.set_as_slideshow(
				uris=uris,
				static_duration=self.pdata['static_duration'],
				transition_duration=self.pdata['transition_duration']
			)

			self.pdata['displayed_photos_hash'] = displayed_photos_hash
			self.pdata.save()

	def autoupdate_enabled(self):
		return self.pdata['autoupdate']

	def set_autoupdate(self, autoupdate=True):
		self.pdata['autoupdate'] = autoupdate
		self.pdata.save()

	def presave_actions(self):
		print 'executing presave actions'
		self.pdata['media'] = self.last_sync_orm.to_dict()

	def save(self):
		self.pdata['media'] = self.last_sync_orm.to_dict()
		self.pdata.save()
	'''
	callbacks
	'''

	#image download
	def register_image_download_callback(self, callback):
		self.image_download_callbacks.append(callback)

	def alert_image_download_callbacks(self, num_images=1):
		for cb in self.image_download_callbacks:
			cb(num_images)

	#image delete
	def register_image_delete_callback(self, callback):
		self.image_delete_callbacks.append(callback)

	def alert_image_delete_callbacks(self, num_images=1):
		for cb in self.image_delete_callbacks:
			cb(num_images)

	#album download
	def register_album_download_callback(self, callback):
		self.album_download_callbacks.append(callback)

	def alert_album_download_callbacks(self, num_albums=1):
		for cb in self.album_download_callbacks:
			cb(num_albums)

	#post sync
	def register_post_sync_callback(self, callback):
		self.post_sync_callbacks.append(callback)

	def alert_post_sync_callbacks(self, **args):
		for cb in self.post_sync_callbacks:
			cb(**args)