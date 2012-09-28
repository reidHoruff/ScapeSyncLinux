import socket
import getpass
import os

VERSION = '0.02'
AUTHOR = 'Reid Horuff'

APP_NAME = 'cloudpaper (official)'

API_URL = 'http://localhost/cloud/api/json/'

USER_DATA_PATH = os.path.join(os.getenv('HOME'), '.cloudpaper/')

PERSISTENCE_FILE_NAME = 'data.js'
PERSISTENCE_FILE_PATH = os.path.join(USER_DATA_PATH, PERSISTENCE_FILE_NAME)

DEFAULT_MEDIA_DIR = os.path.join(USER_DATA_PATH, 'wallpaper/')

DEFAULT_PERSISTENCE_DATA = {
	'registered': True,
	'login_success': False,
	'autoupdate': True,
	'remove_wallpaper': True,
	'albums': [],
	'media_dir': DEFAULT_MEDIA_DIR,
	'update_freq': 20,
	'username': 'reid',
	'password': 'root',
	'transition_duration': 1,
	'display_duration': 15,
}

COMPUTER_NAME = socket.gethostname()
COMPUTER_USERNAME = getpass.getuser()
