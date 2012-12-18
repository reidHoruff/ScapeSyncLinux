import socket
import getpass
import os

VERSION = '0.02'
AUTHOR = 'Reid Horuff'

APP_NAME = 'Scape Sync (official)'
APP_TITLE = 'Scape Sync'


HOME_PAGE = 'http://scapesync.com/'

API_URL = 'http://localhost/cloud/api/json/'

APP_CWD = os.getcwd()

USER_DATA_PATH = os.path.join(os.getenv('HOME'), '.ScapeSync/')

PERSISTENCE_FILE_NAME = 'data.json'
PERSISTENCE_FILE_PATH = os.path.join(USER_DATA_PATH, PERSISTENCE_FILE_NAME)

DEFAULT_MEDIA_DIR = os.path.join(USER_DATA_PATH, 'wallpaper/')

DEFAULT_PERSISTENCE_DATA = {
	'registered': False,
	'login_success': False,
	'autoupdate': True,
	'remove_wallpaper': True,
	'media':{
		'images':[],
		'albums':[],
	},
	'media_dir': DEFAULT_MEDIA_DIR,
	'server_ping_interval_s': 5,
	'username': '',
	'password': '',
	'transition_duration': 0,
	'static_duration': 3,
	'displayed_photos_hash': '',
	'image_download_delay_s': 1,
}

DISPLAY_NEW_ALBUMS = True

COMPUTER_NAME = socket.gethostname()
COMPUTER_USERNAME = getpass.getuser()

DEAMON_INTERVAL_S = 1

GLADE_FILE = 'window.xml'

LOGO_IMAGE_PATH = os.path.join(APP_CWD, 'logo.png')

TRAY_LOGO_NAME = 'tray-logo.png'
TRAY_LOGO_IMAGE_PATH = os.path.join(APP_CWD, TRAY_LOGO_NAME)

GNOME_XML_TEMPLATE = 'gnome_template.xml'
GNOME_XML_FILENAME = 'wallpaper.xml'
GNOME_XML_PATH = os.path.join(USER_DATA_PATH, GNOME_XML_FILENAME)

RANDOM_PORT = 16482
