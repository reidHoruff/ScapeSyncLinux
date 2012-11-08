import settings
import os
import json

class Persistence:

	def __init__(self):
		self.persistent_data = {}
		self.read()
		self.lock = None

	def lock(self, key):
		self.lock=key

	def unlock(self, key):
		if self.lock == key:
			self.lock = None 

	def read(self):
		if os.path.exists(settings.PERSISTENCE_FILE_PATH):
			with open(settings.PERSISTENCE_FILE_PATH, 'r') as file:
				json_text = file.read()
				self.persistent_data = json.loads(json_text)
				file.close()
		else:
			print 'using default persistent_data'
			self.persistent_data = settings.DEFAULT_PERSISTENCE_DATA

	def save(self):
		if not os.path.exists(settings.USER_DATA_PATH):
			os.makedirs(settings.USER_DATA_PATH)

		with open(settings.PERSISTENCE_FILE_PATH, 'w+') as file:
			file.write(json.dumps(self.persistent_data))
			file.close()

	def set(self, key, value):
		if not self.lock:
			self.persistent_data[key] = value
			#self.save()
		else:
			print 'Persistence is locked'
		
	def get(self, key):
		return self.persistent_data[key]

	def __getitem__(self, key):
		return self.get(key)

	def __setitem__(self, key, value):
		self.set(key, value)
