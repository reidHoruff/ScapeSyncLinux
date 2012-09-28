import settings
import os
import json

persistent_data = {}

def create_dir_if_not_exists(dir):
	if not os.path.exists(dir):
		print 'creating dir %s' % dir
		os.makedirs(dir)


def read():
	global persistent_data

	create_dir_if_not_exists( settings.USER_DATA_PATH )

	if not os.path.exists( settings.PERSISTENCE_FILE_PATH ):
		print 'using default persistent_data'
		persistent_data = settings.DEFAULT_PERSISTENCE_DATA

	else:
		with open(settings.PERSISTENCE_FILE_PATH, 'r') as file:
			json_text = file.read()
			persistent_data = json.loads(json_text)
			file.close()


def save():
	global persistent_data

	create_dir_if_not_exists( settings.USER_DATA_PATH )

	with open(settings.PERSISTENCE_FILE_PATH, 'w+') as file:
		file.write( json.dumps(persistent_data) )
		file.close()


def set(key, value):
	global persistent_data
	persistent_data[key] = value
	

def get(key):
	try:
		return persistent_data[key]
	except:
		return None
