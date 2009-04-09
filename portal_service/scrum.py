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

from osv import fields, osv
class scrum_product_backlog(osv.osv):
    _inherit = 'scrum.product.backlog'

    def _get_partner(self, cr, uid, ids, name, args, context):
        cr.execute('select b.id, p.partner from scrum_product_backlog b join project_project p on (b.project_id = p.id) where id in (%s)', ','.join(ids))
        return dict(cr.fetchall())

    def _search_partner(self, cr, uid, obj, name, args):
        print args
        if not len(args):
            return []

        pids= self.pool.get('project.project').search(cr,uid,args)
        cr.execute('select id form scrum_product_backlog where project_id in (%s)', ','.join(pids) )
        res= cr.fetchall()
        if not res:
            return [('id','=','0')]
        return [('id','in',bids)]
    
    _columns = {
        'partner_id': fields.function(_get_partner, method=True, string='Customer', fnct_search=_search_partner),
        }
scrum_product_backlog()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

