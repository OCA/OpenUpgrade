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

from osv import osv
from tools.translate import _

class module(osv.osv):
    _inherit = 'ir.module.module'

    def button_uninstall(self, cr, uid, ids, context=None):
        if self.search(cr, uid, ['&', ('id', 'in', ids), ('name', '=', 'use_control')], context=context):
            raise osv.except_osv(_('Error'), _('The "use_control" module is not uninstallable'))
        return super(module, self).button_uninstall(cr, uid, ids, context)

module()

