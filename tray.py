#!/usr/bin/env python
import sys
import gtk
import appindicator

import imaplib
import re

PING_FREQUENCY = 1 # seconds

class CheckGMail:

    def __init__(self):
        self.ind = appindicator.Indicator("new-gmail-indicator", "indicator-messages", appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.ind.set_attention_icon("new-messages-red")

        self.menu_setup()
        self.ind.set_menu(self.menu)

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

    def show_settings(self, widget):
        print "show settings"

    def main(self):
        self.check_mail()
        gtk.timeout_add(PING_FREQUENCY * 1000, self.check_mail)
        gtk.main()

    def quit(self, widget):
        sys.exit(0)

    def check_mail(self):
        print 'check mail'
        return True

if __name__ == "__main__":
    indicator = CheckGMail()
    indicator.main()