# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import tools
import common
import base64
import gc
import gtk
from gtk import glade

import interface
import os



class wid_picture(interface.widget_interface):
	def __init__(self, window, parent, model, attrs={}):
		interface.widget_interface.__init__(self, window, parent, model, attrs)
		self.win_gl = glade.XML(common.terp_path("picture2.glade"),"widget_picture")
		self.widget = self.win_gl.get_widget('widget_picture')
		self.win_gl.signal_connect('on_picture_but_open_clicked', self.sig_add)
		self.win_gl.signal_connect('on_picture_but_clear_clicked', self.sig_clear)
		self.win_gl.signal_connect('on_picture_but_saveas_clicked', self.sig_save_as)
		#self.wid_text = self.win_gl.get_widget('ent_picture')
		self.wid_picture = self.win_gl.get_widget('widget_picture_view')
		self.value=False

	def set_value(self, model_field):
		#return model_field.set_client(self.wid_text.get_text() or False)
		return model_field.set_client(self.value)
	
	def sig_clear(self, widget=None):
		self.value=False
		self.preview()
				
	def sig_save_as(self, widget=None):
		try:
			filename = common.file_selection(_('Save attachment as...'))
			fp = file(filename,'wb+')
			fp.write(base64.decodestring(self.value))
			fp.close()
		except:
			common.message(_('Error writing the file!'))
			
	def sig_add(self, widget=None):
		try:
			filename = common.file_selection(_('Select the file to picture(jpg,jpeg,gif,png)'))			
			#self.wid_text.set_text(filename)
			self.value=base64.encodestring(file(filename).read())
			self.preview()
		except:
			common.message(_('Error reading the file'))		
	def preview(self,*arg):
			try:			
				if self.value:
					def set_size(object, w, h):					
						ww=self.wid_picture.get_allocation().width
						ww=300
						scale = 1.0*ww/w
						object.set_size(int(scale*w),int(scale*h))
					#
					value2=base64.decodestring(self.value)
					loader = gtk.gdk.PixbufLoader ()
					loader.connect_after('size-prepared',set_size)
					loader.write (value2, len(value2))
					pixbuf = loader.get_pixbuf ()
					loader.close ()
					
					self.wid_picture.set_from_pixbuf(pixbuf)
				else:
					self.wid_picture.set_from_pixbuf(None)
			except Exception, e:
				common.message(_('Unable to preview image file !\nVerify the format.'))		
				gc.collect()
	def display(self, model_field):
		super(wid_picture, self).display(model_field)
		#self.wid_text.set_text( '')
		self.value=model_field and model_field.get()
		self.preview()
		

