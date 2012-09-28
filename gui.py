import settings
import pynotify

try:
 	import pygtk
  	pygtk.require("2.0")
except:
  	pass

import gtk
import gtk.glade

class CloudPaperMainWindow:

	GLADE_FILE = 'window.xml'

	def disable_time_spin_if_uncheked(self):
		isactive = self.wTree.get_widget('AutoSyncCheckbox').get_active()
		self.wTree.get_widget('UpdateMinuteSpinbutton').set_sensitive( isactive )

	def disable_logout_id_loggedin(self):

		if self.user_is_loggedin:
			self.wTree.get_widget('LogoutFrame').set_sensitive(True)
			self.wTree.get_widget('ProfileLinkButton').set_label(self.username)

		else:
			self.wTree.get_widget('LogoutFrame').set_sensitive(False)
			self.wTree.get_widget('ProfileLinkButton').set_label('profile')

	def __init__(self):

		self.user_is_loggedin = False
		self.username = None
		self.livesync = True

		self.wTree = gtk.glade.XML(CloudPaperMainWindow.GLADE_FILE)

		self.window = self.wTree.get_widget('MainWindow')
		self.wTree.get_widget('UpdateMinuteSpinbutton').set_adjustment( gtk.Adjustment(value=1, lower=1, upper=1000, step_incr=1) )
		self.wTree.get_widget('VersionLabel').set_label(settings.VERSION)
		self.wTree.get_widget('DeveloperLabel').set_label(settings.AUTHOR)

		dic = {
			'on_MainWindow_destroy': gtk.main_quit,
			'on_CloseButton_clicked': gtk.main_quit,
			'on_LoginSubmitButton_pressed': self.login_submit_button_pressed,
			'on_UnlinkComputerButton_pressed': self.unlink_computer_button_pressed,
			'on_AutoSyncCheckbox_toggled': self.auto_sync_checkbox_toggle,
			'on_UpdateMinuteSpinbutton_value_changed': self.update_minute_spinbutton_value_changed,
			'on_SyncButton_clicked': self.sync_button_pressed,
		}

		self.wTree.get_widget('AutoSyncCheckbox').set_active(self.livesync)
		self.disable_time_spin_if_uncheked()
		self.disable_logout_id_loggedin()

		self.wTree.signal_autoconnect(dic)
		self.window.show()


	def login_submit_button_pressed(self, widget):
		username = self.wTree.get_widget('UsernameTextinput').get_text()
		password = self.wTree.get_widget('PasswordTextinput').get_text()
		print "submit %s %s" % (username, password)

	def sync_button_pressed(self, widget):
		print 'sync now'

	def unlink_computer_button_pressed(self, widget):
		print "unlink"

	def auto_sync_checkbox_toggle(self, widget):
		print 'autosync toggle %s' % widget.get_active()
		self.disable_time_spin_if_uncheked()

	def update_minute_spinbutton_value_changed(self, widget):
		print 'spinbtn %s' % widget.get_value_as_int()

	def show_window(self):
		self.window.show()

	def hide_window(self):
		self.window.hide()

def notify(title, description):
	n = pynotify.Notification(title, description, "/usr/share/pixmaps/firefox.png")
	n.show()

if __name__ == "__main__":
	hwg = CloudPaperMainWindow()
	gtk.main()

