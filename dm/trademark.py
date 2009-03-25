# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
import time

from osv import fields
from osv import osv

class dm_media(osv.osv):
    _name = "dm.media"
    """    
    def search(self, cr, uid, args, offset=0, limit=None, order=None,
            context=None, count=False):
        if 'step_media_ids' in context and context['step_media_ids']:
            if context['step_media_ids'][0][2]:
                brse_rec = context['step_media_ids'][0][2]
            else:
                raise osv.except_osv('Error !',"It is necessary to select media in offer step.")
        else:
            brse_rec = super(dm_media, self).search(cr, uid, [])
        return brse_rec
    """
    _columns = {
        'name' : fields.char('Name', size=64, translate=True, required=True),
        'code' : fields.char('Code', size=64, translate=True, required=True),
    }
dm_media()

class dm_trademark(osv.osv):
    _name = "dm.trademark"
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'code' : fields.char('Code', size=6, required=True),
        'partner_id' : fields.many2one('res.partner', 'Partner', required=False),
        'header' : fields.binary('Header (.odt)'),
        'logo' : fields.binary('Logo'),
        'signature' : fields.binary('Signature'),
        'media_id' : fields.many2one('dm.media', 'Media')
    }

dm_trademark()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

