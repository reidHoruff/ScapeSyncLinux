import urllib
import urllib2
from urllib2 import URLError, HTTPError
import os
import json
import settings
import persistence
import gui

def parse_response(data):

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


def connect_to_server():

	persistence.set('login_success', False)

	if not persistence.get('registered'):
		return False

	request_data = {
		'username': persistence.get('username'),
		'password': persistence.get('password'),
		'computer_name': settings.COMPUTER_NAME,
		'computer_username': settings.COMPUTER_USERNAME,
		'app_version': settings.VERSION,
		'app_name': settings.APP_NAME,
	}

	try:
		print 'Connecting to server...'
		response = urllib2.urlopen(settings.API_URL, urllib.urlencode(request_data))
		print 'Connection Successful!'

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
		persistence.set('login_success', True)
		print 'Login Successful!'
		return data

	else:
		persistence.set('login_success', False)
		print 'Login Failure'
		print 'Error: %s' % (data['error'])
		return False

def download_image(url, dest):

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

def sync_wallpaper(data):

	server_files = {}

	for album in data['owned_albums']:
		for pic in album['album_photos']:
			server_files[pic['filename']] = pic

	for album in data['watched_albums']:
		for pic in album['album_photos']:
			server_files[pic['filename']] = pic


	persistence.create_dir_if_not_exists( persistence.get('media_dir') )

	existing_files = set()

	for filename in os.listdir( persistence.get('media_dir')):
		#print '\t %s' % (filename)
		existing_files.add(filename)


	files_to_download = set(server_files) - existing_files
	files_to_delete   = existing_files - set(server_files)
	files_to_keep     = existing_files & set(server_files)

	print 'files to download:'
	for filename in files_to_download:
		print filename, server_files[filename]['original_url']

	print 'files to delete:'
	for filename in files_to_delete:
		print filename

	#print 'files to keep:'
	#for filename in files_to_keep:
	#	print filename, server_files[filename]['original_url']


	print 'Downloading new wallpaper... (%s)' % (len(files_to_download))

	if len(files_to_download) > 0:

		if len(files_to_download) > 1:
			msg = "%s new wallpapers synced" % len(files_to_download)

		else:
			msg = "A new wallapaer has been synced"

	else:
		msg = "No wallpapers synced"
		
	gui.notify("Scape Sync", msg)

	for filename in files_to_download:
		image = server_files[filename]
		dest = os.path.join(persistence.get('media_dir'), image['filename'] )
		download_image(image['original_url'], dest)

	if persistence.get('remove_wallpaper'):

		#TODO: compare to previously sycned list, not existing files
		print 'Removing unused wallpaper... (%s)' % (len(files_to_delete))

		for filename in files_to_delete:
			kill_path = os.path.join(persistence.get('media_dir'), filename)

			print 'Removing %s' % (kill_path)

			try:
				os.remove(kill_path)
			except:
				print 'Unable to remove file'