'''
handles storing data (not files) on the local computer.
format is json.

should only directly be accessed and read from by the ScapeSync object.
*unless instance is sent directly to a function

generally objects shouldnt have their own instance of persistence
'''

import settings
import os
import json

class Persistence:

	def __init__(self):
		self.persistent_data = {}
		self.read()
		self.pre_save_callbacks = []

	def read(self):
		if os.path.exists(settings.PERSISTENCE_FILE_PATH):
			with open(settings.PERSISTENCE_FILE_PATH, 'r') as mfile:
				json_text = mfile.read()
				self.persistent_data = json.loads(json_text)
		else:
			print 'using default persistent_data'
			self.persistent_data = settings.DEFAULT_PERSISTENCE_DATA

	def save(self):
		self.alert_presave_callbacks()
		
		print 'saving persistence data...'

		if not os.path.exists(settings.USER_DATA_PATH):
			os.makedirs(settings.USER_DATA_PATH)

		with open(settings.PERSISTENCE_FILE_PATH, 'w+') as mfile:
			mfile.write(json.dumps(self.persistent_data, indent=4))

	def set(self, key, value):
		self.persistent_data[key] = value
		#self.save()
		
	def get(self, key):
		return self.persistent_data[key]

	def __getitem__(self, key):
		return self.get(key)

	def __setitem__(self, key, value):
		self.set(key, value)

	def attach_presave_callback(self, callback):
		self.pre_save_callbacks.append(callback)

	def alert_presave_callbacks(self):
		for cb in self.pre_save_callbacks:
			cb()
