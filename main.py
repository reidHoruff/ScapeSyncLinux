import settings
import scapesync
import wallpaperManager
import gui

if __name__ == '__main__':

	print '%s | version %s | %s' % (settings.APP_NAME, settings.VERSION, settings.AUTHOR)

	wp_manager = wallpaperManager.Gnome2WallpaperManager()
	scape_sync = scapesync.ScapeSync(wp_manager)
	
	scape_sync.start()

	tray = gui.TrayNotifyDeamon(scape_sync)
	tray.main()

	print 'goodbye'