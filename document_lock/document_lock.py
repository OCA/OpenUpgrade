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

from osv import osv, fields

class ir_attachment(osv.osv):
    _inherit = 'ir.attachment'

    _columns = {
        'state' : fields.selection([('locked', 'Locked'),('unlocked', 'Unlocked')], 'State', readonly=True),
    }

    _defaults = {
        'state' : lambda *a: 'unlocked'
    }

    def check(self, cr, uid, ids, mode):
        if not ids:
            return
        ima = self.pool.get('ir.model.access')
        if isinstance(ids, (int, long)):
            ids = [ids]

        if mode != 'read':
            if len(ids) == 1:
                msg = _('You can not modify this document !')
            else:
                msg = _('You can not modify one of these documents !')

            for obj in self.browse(cr, uid, ids):
                if obj.state == 'locked':
                    raise osv.except_osv(_('AccessError'), msg)

        cr.execute('select distinct res_model from ir_attachment where id in ('+','.join(map(str, ids))+')')
        for obj in cr.fetchall():
            ima.check(cr, uid, obj[0], mode)

ir_attachment()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
