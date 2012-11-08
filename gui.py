import settings
import pynotify
import sys
import appindicator
import gobject

try:
	import pygtk
  	pygtk.require("2.0")
except:
  	pass

import gtk
import gtk.glade

def notify(title, description):
	n = pynotify.Notification(title, description, "/usr/share/pixmaps/firefox.png")
	n.show()

def notify_download(num_photos):
	if num_photos <= 1:
		notify('ScapeSync', 'Downloading new wallpaper')

	else:
		notify('ScapeSync', 'Downloading %s new wallpapers' % num_photos)

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

	def disable_logout_if_loggedin(self):

		if True:
			self.wTree.get_widget('LogoutFrame').set_sensitive(True)
			self.wTree.get_widget('ProfileLinkButton').set_label(self.persistence_data['username'])

		else:
			self.wTree.get_widget('LogoutFrame').set_sensitive(False)
			self.wTree.get_widget('ProfileLinkButton').set_label('profile')

	def __init__(self, persistence_data):

		self.persistence_data = persistence_data
		self.wTree = gtk.glade.XML(settings.GLADE_FILE)

		self.window = self.wTree.get_widget('MainWindow')
		self.wTree.get_widget('UpdateMinuteSpinbutton').set_adjustment(gtk.Adjustment(value=1, lower=1, upper=1000, step_incr=1))
		self.wTree.get_widget('VersionLabel').set_label(settings.VERSION)
		self.wTree.get_widget('DeveloperLabel').set_label(settings.AUTHOR)

		self.init_album_tree_view()

		dic = {
			#'on_MainWindow_destroy': self.hide_window,
			'on_MainWindow_delete_event': self.delete_event,
			#'on_MainWindow_destroy_event': self.hide_window,
			'on_CloseButton_clicked': self.hide_window,
			'on_LoginSubmitButton_pressed': self.login_submit_button_pressed,
			'on_UnlinkComputerButton_pressed': self.unlink_computer_button_pressed,
			'on_AutoSyncCheckbox_toggled': self.auto_sync_checkbox_toggle,
			'on_UpdateMinuteSpinbutton_value_changed': self.update_minute_spinbutton_value_changed,
			'on_SyncButton_clicked': self.sync_button_pressed,
			#'on_albumsTreeView_row_activated': self.on_albumsTreeView_row_activated,
		}

		self.wTree.get_widget('AutoSyncCheckbox').set_active(self.persistence_data['autoupdate'])
		self.disable_logout_if_loggedin()

		self.wTree.signal_autoconnect(dic)

	def col1_toggled_cb(self, cell, path, model ):
		model[path][1] = not model[path][1]

	def init_album_tree_view(self):
		treeView = self.wTree.get_widget('albumsTreeView')

		model = gtk.ListStore(str, gobject.TYPE_BOOLEAN)

		for x in range(10):
			model.append(['dfs', False])

		treeView.set_model(model)
		treeView.set_rules_hint(True)

		#display toggle
		displayToggleRenderer = gtk.CellRendererToggle()
		displayToggleRenderer.set_property('activatable', True)
		displayToggleRenderer.connect('toggled', self.col1_toggled_cb, model)
		displayToggleColumn = gtk.TreeViewColumn('Displayed', displayToggleRenderer )
		displayToggleColumn.add_attribute( displayToggleRenderer, 'active', 1)
		treeView.append_column(displayToggleColumn)

		#album name
		albumNameRenderer = gtk.CellRendererText()
		albumNameColumn = gtk.TreeViewColumn("Album Name", albumNameRenderer, text=0)
		treeView.append_column(albumNameColumn)

	def login_submit_button_pressed(self, widget):

		username = self.wTree.get_widget('UsernameTextinput').get_text()
		password = self.wTree.get_widget('PasswordTextinput').get_text()

		print "submit %s %s" % (username, password)

	def sync_button_pressed(self, widget):
		pass

	def unlink_computer_button_pressed(self, widget):
		print 'unlink'

	def auto_sync_checkbox_toggle(self, widget):
		self.persistence_data['autoupdate'] = widget.get_active()

		print 'autosync toggle %s' % widget.get_active()
		self.disable_time_spin_if_uncheked()

	def update_minute_spinbutton_value_changed(self, widget):
		print 'spinbtn %s' % widget.get_value_as_int()

class TrayNotifyDeamon:

    def __init__(self, persistence_data, request=None):

    	self.persistence_data = persistence_data

    	self.ss_request = request

    	if self.ss_request:
    		self.ss_request.register_image_download_callback(notify_download)

    	self.settings_window = CloudPaperMainWindow(persistence_data)

        self.ind = appindicator.Indicator("new-scapesync-indicator", "indicator-messages", appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.ind.set_attention_icon("new-messages-red")

        self.menu_setup()

    def menu_setup(self):
        self.menu = gtk.Menu()

        self.quit_item = gtk.MenuItem("Quit ScapeSync")
        self.quit_item.connect("activate", self.quit)
        self.quit_item.show()
        self.menu.append(self.quit_item)

        self.show_settings_item = gtk.MenuItem("Settings")
        self.show_settings_item.connect("activate", self.show_settings)
        self.show_settings_item.show();
        self.menu.append(self.show_settings_item)

        self.ind.set_menu(self.menu)

    def show_settings(self, widget):
    	self.settings_window.show_window()

    def quit(self, widget):
        sys.exit(0)

    def main(self):
    	self.deamon_seconds_running = 0
        gobject.timeout_add(settings.DEAMON_INTERVAL_S * 1000, self.scape_sync_deamon)
        gtk.main()

    def scape_sync_deamon(self):
    	#print "deamon running %s" % self.deamon_seconds_running

    	if self.deamon_seconds_running % self.persistence_data['server_ping_interval_s'] == 0:
    		self.ss_request.sync()

    	self.deamon_seconds_running += settings.DEAMON_INTERVAL_S
    	return True

if __name__ == '__main__':
	import persistence
	persist_data = persistence.Persistence()
	persist_data.save()

	tray = TrayNotifyDeamon(persist_data)
	tray.settings_window.show_window()
	tray.main()
