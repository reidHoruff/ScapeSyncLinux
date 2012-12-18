import settings
import pynotify
import appindicator
import gobject
import subprocess
import webbrowser
import time

try:
	import pygtk
	pygtk.require("2.0")
except:
	pass

import gtk
import gtk.glade

class CloudPaperMainWindow:

	def show_window(self, widget=None):
		self.window.show_all()
		return True

	def hide_window(self, widget=None):
		self.window.hide()
		return True

	def delete_event(self, event, widget):
		self.hide_window()
		return True

	def refresh_account_visability(self):
		self.wTree.get_widget('LoginFrame').hide()
		self.wTree.get_widget('LogoutFrame').hide()
		self.wTree.get_widget('LoginError').hide()

		if self.pdata['registered']:
			if self.pdata['login_success']:
				self.wTree.get_widget('LogoutFrame').show()

			else:
				self.wTree.get_widget('LoginError').show()
				self.wTree.get_widget('LoginFrame').show()

		else:
			self.wTree.get_widget('LoginFrame').show()

	def on_MainWindow_show(self, widget):
		self.refresh_account_visability()

	def __init__(self, tray_deamon, scape_sync):

		self.tray_deamon = tray_deamon
		self.scape_sync = scape_sync
		self.pdata = self.scape_sync.pdata

		self.wTree = gtk.glade.XML(settings.GLADE_FILE)

		self.window = self.wTree.get_widget('MainWindow')
		self.wTree.get_widget('UpdateMinuteSpinbutton').set_adjustment(gtk.Adjustment(value=1, lower=5, upper=1000, step_incr=1))
		self.wTree.get_widget('DisplayDurationSpinbutton').set_adjustment(gtk.Adjustment(value=1, lower=1, upper=1000, step_incr=1))
		self.wTree.get_widget('TransitionDurationSpinbutton').set_adjustment(gtk.Adjustment(value=0, lower=0, upper=1000, step_incr=1))
		self.wTree.get_widget('VersionLabel').set_label(settings.VERSION)
		self.wTree.get_widget('DeveloperLabel').set_label(settings.AUTHOR)

		self.init_album_tree_view()
		self.update_album_tree_view()

		self.wTree.signal_autoconnect({
			'on_MainWindow_delete_event': self.delete_event,
			'on_CloseButton_clicked': self.hide_window,
			'on_LoginSubmitButton_pressed': self.login_submit_button_pressed,
			'on_UnlinkComputerButton_pressed': self.unlink_computer_button_pressed,
			'on_AutoSyncCheckbox_toggled': self.auto_sync_checkbox_toggle,
			'on_UpdateMinuteSpinbutton_value_changed': self.update_minute_spinbutton_value_changed,
			'on_TransitionDurationSpinbutton_value_changed': self.transition_duration_spinbutton_value_changed,
			'on_DisplayDurationSpinbutton_value_changed': self.display_duration_spinbutton_value_changed,
			'on_SyncButton_clicked': self.sync_button_pressed,
			'on_MainWindow_show': self.on_MainWindow_show,
		})

		self.wTree.get_widget('AutoSyncCheckbox').set_active(self.pdata['autoupdate'])
		self.wTree.get_widget('UpdateMinuteSpinbutton').set_value(self.pdata['server_ping_interval_s'])


	def album_check_cb(self, cell, path, model):
		model[path][1] = not model[path][1]
		
		index = int(path)
		album_set = self.scape_sync.last_sync_orm.albums

		sorted(album_set)[index].is_displayed = model[path][1]

		self.scape_sync.save()

		self.scape_sync.update_wallpaper()

	def init_album_tree_view(self):
		treeView = self.wTree.get_widget('albumsTreeView')

		model = gtk.ListStore(str, gobject.TYPE_BOOLEAN)
		treeView.set_model(model)
		treeView.set_rules_hint(True)

		#display toggle
		displayToggleRenderer = gtk.CellRendererToggle()
		displayToggleRenderer.set_property('activatable', True)
		displayToggleRenderer.connect('toggled', self.album_check_cb, model)
		displayToggleColumn = gtk.TreeViewColumn('Displayed', displayToggleRenderer )
		displayToggleColumn.add_attribute( displayToggleRenderer, 'active', 1)
		treeView.append_column(displayToggleColumn)

		#album name
		albumNameRenderer = gtk.CellRendererText()
		albumNameColumn = gtk.TreeViewColumn("Album Name", albumNameRenderer, text=0)
		treeView.append_column(albumNameColumn)

	def update_album_tree_view(self):
		treeView = self.wTree.get_widget('albumsTreeView')
		model = treeView.get_model()
		model.clear()

		for album in sorted(self.scape_sync.last_sync_orm.albums):
			model.append([album.name, album.is_displayed])

	def login_submit_button_pressed(self, widget):
		print 'submit login data'
		self.scape_sync.can_log_in(
			username=self.wTree.get_widget('UsernameTextinput').get_text(),
			password=self.wTree.get_widget('PasswordTextinput').get_text()
		)

		self.refresh_account_visability()
		self.scape_sync.request_sync()

	def unlink_computer_button_pressed(self, widget):
		print 'unlinging PC'
		self.scape_sync.logout()
		self.refresh_account_visability()

	def sync_button_pressed(self, widget):
		print 'request next sync'
		self.scape_sync.request_sync()

	def auto_sync_checkbox_toggle(self, widget):
		print 'autosync: %s' % widget.get_active()
		self.scape_sync.set_autoupdate(widget.get_active())

	def update_minute_spinbutton_value_changed(self, widget):
		seconds = widget.get_value_as_int()
		print 'update: %s seconds' % seconds
		self.pdata['server_ping_interval_s'] = seconds 
		self.scape_sync.save()

	def transition_duration_spinbutton_value_changed(self, widget):
		seconds = widget.get_value_as_int()
		print 'transition duration', seconds
		self.pdata['transition_duration'] = seconds
		self.scape_sync.update_wallpaper()
		self.scape_sync.save()

	def display_duration_spinbutton_value_changed(self, widget):
		seconds = widget.get_value_as_int()
		print 'display duration', seconds
		self.pdata['static_duration'] = seconds
		self.scape_sync.update_wallpaper()
		self.scape_sync.save()

class TrayNotifyDeamon:

	def notify(self, description):
		n = pynotify.Notification(settings.APP_TITLE, description, settings.LOGO_IMAGE_PATH)
		n.show()

	def notify_download(self, num_photos):
		if num_photos <= 1:
			self.notify('Downloading new wallpaper')

		else:
			self.notify('Downloading %s new wallpapers' % num_photos)

	def notify_image_delete(self, num_photos):
		if num_photos <= 1:
			self.notify('Removing wallpaper from computer')

		else:
			self.notify('Removing %s images from computer' % num_photos)

	def post_sync_notify(self, images_downloaded, albums_downloaded, images_deleted, albums_removed):
		if albums_downloaded + albums_removed > 0:
			self.settings_window.update_album_tree_view()
			print 'albums added/removed'

	def __init__(self, scape_sync):

		#self.notify('Scape Sync is Running')

		#globals
		self.scape_sync = scape_sync
		self.pdata = self.scape_sync.pdata

		#callbacks
		self.scape_sync.register_image_download_callback(self.notify_download)
		self.scape_sync.register_image_delete_callback(self.notify_image_delete)
		self.scape_sync.register_post_sync_callback(self.post_sync_notify)

		#main window
		self.settings_window = CloudPaperMainWindow(self, self.scape_sync)
		self.ind = appindicator.Indicator(settings.APP_TITLE, settings.TRAY_LOGO_IMAGE_PATH, appindicator.CATEGORY_APPLICATION_STATUS)
		self.ind.set_status(appindicator.STATUS_ACTIVE)

		#print settings.TRAY_LOGO_IMAGE_PATH
		self.ind.set_attention_icon("new-messages-red")
		#self.ind.set_icon_theme_path(settings.APP_CWD)
		#self.ind.set_icon(settings.TRAY_LOGO_NAME)

		#tray menu
		self.menu = gtk.Menu()

		self.visit_site_item = gtk.MenuItem("Visit Scape Sync Website")
		self.visit_site_item.connect("activate", self.visit_site)
		self.visit_site_item.show()
		self.menu.append(self.visit_site_item)

		self.browse_item = gtk.MenuItem("Browse Synced Wallpapers")
		self.browse_item.connect("activate", self.browse_wallpapers)
		self.browse_item.show()
		self.menu.append(self.browse_item)

		#seperator
		self.seperator1 = gtk.SeparatorMenuItem()
		self.seperator1.show()
		self.menu.append(self.seperator1)

		self.last_update_item = gtk.MenuItem("Last Synced %s" % 'foo')
		self.last_update_item.set_sensitive(False)
		self.last_update_item.show()
		self.menu.append(self.last_update_item)

		self.sync_item = gtk.MenuItem("Sync with ScapeSync.com")
		self.sync_item.connect("activate", self.request_sync)
		self.sync_item.show()
		self.menu.append(self.sync_item)

		#seperator
		self.seperator2 = gtk.SeparatorMenuItem()
		self.seperator2.show()
		self.menu.append(self.seperator2)

		self.show_settings_item = gtk.MenuItem("Preferences...")
		self.show_settings_item.connect("activate", self.show_settings)
		self.show_settings_item.show();
		self.menu.append(self.show_settings_item)

		self.quit_item = gtk.MenuItem("Quit %s" % settings.APP_TITLE)
		self.quit_item.connect("activate", self.quit)
		self.quit_item.show()
		self.menu.append(self.quit_item)

		self.ind.set_menu(self.menu)

	def visit_site(self, widget=None):
		webbrowser.open(settings.HOME_PAGE)

	def request_sync(self, widget=None):
		self.scape_sync.request_sync()

	def show_settings(self, widget):
		self.settings_window.show_window()

	def browse_wallpapers(self, widget=None):
		subprocess.check_call(['gnome-open', self.pdata['media_dir']])

	def quit(self, widget):
		self.scape_sync.request_quit()
		time.sleep(2)
		gtk.main_quit()

	def main(self):
		gtk.gdk.threads_init()
		gtk.main()