import settings
import json
import os

'''
This is an ORM, or at least pretty close to one, for storing information about albums and images.
designed to create a common interface for userdata no matter 
whether it comes from a specific api version for is read from persistence data.
'''

class Image:

	def __init__(self, original_url, slug, filename):
		self.original_url = original_url
		self.slug = slug
		self.filename = filename

	def __hash__(self):
		return hash(self.filename)

	def __eq__(self, other):
		return self.filename == other.filename

	def __unicode__(self):
		return self.filename

	def __str__(self):
		return self.filename

	def __repr__(self):
		return self.filename

	def to_dict(self):
		data = {
			'filename': self.filename,
			'slug': self.slug,
			'original_url': self.original_url
		}

		return data

class Album:

	def __init__(self, name, id_string, is_displayed):
		self.name = name
		self.id_string = id_string
		self.is_displayed = is_displayed
		self.images = set()

	def __hash__(self):
		return hash(self.id_string)

	def __eq__(self, other):
		return self.id_string == other.id_string

	def __unicode__(self):
		return self.name

	def __str__(self):
		return self.name

	def __repr__(self):
		return self.name

	def __cmp__(self, other):
		return cmp(self.name, other.name)

	def to_dict(self):
		data = {
			'name': self.name,
			'id_string': self.id_string,
			'is_displayed': self.is_displayed,
			'images': [],
		}

		data['images'] = [image.filename for image in self.images]

		return data

class ScapeSyncORM:

	def __init__(self):
		self.albums = set()
		self.images = set()

	def add_album(self, name, id_string, filenames=[], is_displayed=True):
		album = Album(name, id_string, is_displayed)

		filenames = set(filenames)

		for image in self.images:
			if image.filename in filenames:
				album.images.add(image)
				filenames -= set([image.filename])

		if len(filenames) > 0:
			raise Exception('not all filenames were matched to images: %s' % filenames)

		self.albums.add(album)

	def get_displayed_albums(self):
		return set(filter(lambda x: x.is_displayed, self.albums))

	#display everything except for nondisplayed albums in other_orm.albums
	def apply_displayed_filter(self, other_orm):
		hidden_albums =  other_orm.albums - other_orm.get_displayed_albums()

		for album in self.albums:
			album.is_displayed = album not in hidden_albums

	def add_image(self, original_url, slug, filename):
		image  = Image(original_url, slug, filename)
		self.images.add(image)

	def add_from_api_1_0_dict(self, data):

		for image in data['all_photos']:
			self.add_image(image['original_url'], image['slug'], image['filename'])

		all_albums = data['owned_albums'] + data['watched_albums']

		for album in all_albums:
			self.add_album(album['album_name'], album['id_string'], album['album_photos'])

	def add_from_persistence_dict(self, data):
		for image in data['images']:
			self.add_image(image['original_url'], image['slug'], image['filename'])

		for album in data['albums']:
			self.add_album(album['name'], album['id_string'], album['images'], album['is_displayed'])

	#obviously doesnt supply all of the data, but is user for
	#object comparison for downloading/deleting
	def add_from_media_dir(self, media_dir):

		if os.path.exists(media_dir):
			for filename in os.listdir(media_dir):
				self.add_image(None, None, filename)
		
		else:	
			os.makedirs(media_dir)

	def clear(self):
		self.albums.clear()
		self.images.clear()

	def to_dict(self):
		data = {
			'albums': [album.to_dict() for album in self.albums],
			'images': [image.to_dict() for image in self.images]
		}

		return data

	def __sub__(self, other):
		diff = ScapeSyncORM()
		diff.albums = self.albums - other.albums
		diff.images = self.images - other.images
		return diff

#testing
if __name__ == '__main__':
	orm1 = ScapeSyncORM()
	orm1.add_image('foo1', 'foo1', 'foo1.png')
	orm1.add_image('foo2', 'foo2', 'foo2.png')
	orm1.add_album('album1', 'id1', [])


	orm2 = ScapeSyncORM()
	orm2.add_image('foo1', 'foo1', 'foo1.png')
	orm2.add_image('foo2', 'foo2', 'foo2.png')
	orm2.add_album('album1', 'id1', [])

	diff = orm1 - orm2

	print diff.albums

	class Foo:
		def __init__(self, value):
			self.value = value

		def __cmp__(self, other):
			return other.value - self.value

		def __repr__(self):
			return str(self.value)

	a = [Foo(1), Foo(-1)]
	sorted(a)
	print a