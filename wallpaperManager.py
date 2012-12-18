import datetime
import settings
import random
import os
import gconf
from jinja2 import Template

class Gnome2WallpaperManager:

	def __init__(self):
		pass

	'''
	this algorith guarantees no repeats
	'''
	def __randomize(self, uris, length=3):

		if len(uris) < 3: return

		orig = uris
		uris = []

		for x in range(length):
			random.shuffle(orig)

			while len(uris) > 0 and uris[-1] == orig[0]:
				random.shuffle(orig)

			uris += orig

	def set_as_slideshow(self, uris, static_duration, transition_duration, add_randomness=True):

		if len(uris) < 1:
			print 'uris[] is empty'
			return

		'''
		gnome backgrounds cant be randomized, only displyed
		as defined in the xml file, so 'randomness' must be created in 
		the xml file
		'''

		if add_randomness:
			self.__randomize(uris, 3)

		#create render_vars
		render_vars = {}
		render_vars['filename'] = settings.GNOME_XML_PATH
		render_vars['timestamp'] = datetime.datetime.now()
		render_vars['start_time'] = datetime.datetime.now() - datetime.timedelta(seconds=1)
		render_vars['app_name'] = settings.APP_NAME
		render_vars['app_version'] = settings.VERSION
		render_vars['static_duration'] = static_duration
		render_vars['transition_duration'] = transition_duration
		render_vars['wallpaper'] = []

		for x in range(len(uris)):
			render_vars['wallpaper'].append({
				'location': uris[x],
				'next_location': uris[(x+1) % len(uris)]
				})

		#read template file
		with open(settings.GNOME_XML_TEMPLATE, 'r') as template_file:
			template = Template(template_file.read())
		
		#save parsed template to xml file
		with open(settings.GNOME_XML_PATH, 'w+') as output_file:
			output_file.write(template.render(**render_vars))

		#point gnome at xml file
		conf_client = gconf.client_get_default()
		conf_client.add_dir("/desktop/gnome/background", gconf.CLIENT_PRELOAD_NONE)
		conf_client.set_string("/desktop/gnome/background/picture_filename", settings.GNOME_XML_PATH)
		conf_client.set_string("/desktop/gnome/background/picture_options", "stretched")