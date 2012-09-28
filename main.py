import settings
import persistence
import request

if __name__ == '__main__':

	print '%s | version %s | %s' % (settings.APP_NAME, settings.VERSION, settings.AUTHOR)

	persistence.read()

	if persistence.get('registered'):
		print 'logging in with %s %s' % (persistence.get('username'), persistence.get('password'))
		response = request.connect_to_server()

		if response:
			#request.parse_response(response)
			request.sync_wallpaper(response)

	else:
		#app is not registered
		pass

	persistence.save()