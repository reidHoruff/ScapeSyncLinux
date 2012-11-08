import settings
import persistence
import request
import gui

if __name__ == '__main__':

	print '%s | version %s | %s' % (settings.APP_NAME, settings.VERSION, settings.AUTHOR)

	
	persist_data = persistence.Persistence()
	persist_data.save()

	ss_request = request.Request(persist_data)

	tray = gui.TrayNotifyDeamon(persist_data, ss_request)
	tray.main()

	persistence.save()


"""
	if persistence.get('registered'):
		print 'logging in with %s %s' % (persistence.get('username'), persistence.get('password'))
		response = request.connect_to_server()

		if response:
			#request.parse_response(response)
			request.sync_wallpaper(response)

	else:
		#app is not registered
		pass
"""