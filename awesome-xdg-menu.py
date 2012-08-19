#!/usr/bin/python
#
# Copyright (C) 2008  Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author(s): Luke Macken <lmacken@redhat.com>
#            Miroslav Lichvar <mlichvar@redhat.com>
#            Edward Sheldrake <ejsheldrake@gmail.com>


import xdg.Menu, xdg.DesktopEntry, xdg.Config
import re, sys, os
from xml.sax.saxutils import escape

icons = True

try:
	from gi.repository import Gtk
except ImportError:
	icons = False

def icon_attr(entry):
	if icons is False:
		return ''

	name = entry.getIcon()

	if os.path.exists(name):
		return ' icon="' + name + '"'

	# work around broken .desktop files
	# unless the icon is a full path it should not have an extension
	name = re.sub('\..{3,4}$', '', name)

	# imlib2 cannot load svg
	iconinfo = theme.lookup_icon(name, 22, Gtk.IconLookupFlags.NO_SVG)
	if iconinfo:
		iconfile = iconinfo.get_filename()
		iconinfo.free()
		if iconfile:
			return ' icon="' + iconfile + '"'
	return ''

def escape_utf8(s):
	return escape(s.encode('utf-8', 'xmlcharrefreplace'))

def entry_name(entry):
	return escape_utf8(entry.getName())

def walk_menu(entry):
	if isinstance(entry, xdg.Menu.Menu) and entry.Show is True:
		print '<menu id="%s" label="%s"%s>' \
			% (entry_name(entry),
			entry_name(entry),
			escape_utf8(icon_attr(entry)))
		map(walk_menu, entry.getEntries())
		print '</menu>'
	elif isinstance(entry, xdg.Menu.MenuEntry) and entry.Show is True:
		print '	<item label="%s"%s>' % \
			(entry_name(entry.DesktopEntry).replace('"', ''),
			escape_utf8(icon_attr(entry.DesktopEntry)))
		command = re.sub(' -caption "%c"| -caption %c', ' -caption "%s"' % entry_name(entry.DesktopEntry), entry.DesktopEntry.getExec())
		command = re.sub(' [^ ]*%[fFuUdDnNickvm]', '', command)
		if entry.DesktopEntry.getTerminal():
			command = 'xterm -title "%s" -e %s' % \
				(entry_name(entry.DesktopEntry), command)
		print '		<action name="Execute">' + \
			'<command>%s</command></action>' % command
		print '	</item>'

count = 0
menu_list = []
is_first = True

def generate_awesome_menu(entry):
	global is_first
	if isinstance(entry, xdg.Menu.Menu) and entry.Show is True:
		global count
		global menu_list
		is_first = True
		if count != 0:
			print '}'
			print ''
		print 'submenu%d =' % count
		print '{'
		count = count + 1
		menu_list.append(entry_name(entry))
		# print '<menu id="%s" label="%s"%s>' \
		# 	% (entry_name(entry),
		# 	entry_name(entry),
		# 	escape_utf8(icon_attr(entry)))
		map(generate_awesome_menu, entry.getEntries())
		# print '</menu>'
	elif isinstance(entry, xdg.Menu.MenuEntry) and entry.Show is True:
		if not is_first:
			elem = ',\n'
		else:
			is_first = False
			elem = ''
		elem += '  { "%s", ' % \
			(entry_name(entry.DesktopEntry).replace('"', ''))
		command = re.sub(' -caption "%c"| -caption %c', ' -caption "%s"' % entry_name(entry.DesktopEntry), entry.DesktopEntry.getExec())
		command = re.sub(' [^ ]*%[fFuUdDnNickvm]', '', command)
		if entry.DesktopEntry.getTerminal():
			command = 'xterm -title "%s" -e %s' % \
				(entry_name(entry.DesktopEntry), command)
		elem += '"%s" }' % command
		sys.stdout.write(elem)

def generate_main_menu():
	global menu_list
	content = ""
	i = 0

	print '\nmyappmenu = \n{'
	for elem in menu_list:
		if i != len(menu_list) and i != 0:
			content += ',\n'
		content += '  { "%s", submenu%d }' % (elem, i)
		i += 1
	print content
	print '}'

if len(sys.argv) > 1:
	menufile = sys.argv[1] + '.menu'
else:
	menufile = 'applications.menu'

lang = os.environ.get('LANG')
if lang:
	xdg.Config.setLocale(lang)

# lie to get the same menu as in GNOME
xdg.Config.setWindowManager('GNOME')

if icons:
  theme = Gtk.IconTheme.get_default()

menu = xdg.Menu.parse(menufile)

#map(walk_menu, menu.getEntries())
map(generate_awesome_menu, menu.getEntries())

generate_main_menu()

