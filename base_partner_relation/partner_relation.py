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

from osv import fields,osv


class res_partner_relation(osv.osv):
    _description='Partner Relation'
    _name = "res.partner.relation"
    _columns = {
        'name': fields.selection( [ ('default','Default'),('invoice','Invoice'), ('delivery','Delivery'), ('contact','Contact'), ('other','Other') ],'Relation Type', required=True),
        'partner_id': fields.many2one('res.partner', 'Main Partner', required=True, ondelete='cascade'),
        'relation_id': fields.many2one('res.partner', 'Relation Partner', required=True, ondelete='cascade')
    }
    _defaults = {
        'name' : lambda *a: 'invoice',
    }

res_partner_relation()


class res_partner(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'relation_ids': fields.one2many('res.partner.relation', 'partner_id', 'Relations')
    }
    def _is_related_to(self, cr, uid, ids, toid):
        related=[]
        for id in ids:
            cr.execute("select id from res_partner_relation where (partner_id=%s and relation_id=%s) or (partner_id=%s and relation_id=%s)" % (id,toid,toid,id))
            res=cr.fetchone()
            if res and len(res):
                related.append(True)
            else:
                related.append(False)
        return related

    def address_get(self, cr, uid, ids, adr_pref=['default']):
        todo = []
        result = {}
        cr.execute('select name,relation_id from res_partner_relation where partner_id in ('+','.join(map(str,ids))+')')
        adrs = dict(cr.fetchall())
        for adr in adr_pref:
            if adr in adrs:
                adr_prov = super(res_partner, self).address_get(cr, uid, [adrs[adr]], [adr]).values()[0]
                result[adr] = adr_prov
            else:
                todo.append(adr)
        if len(todo):
            result.update(super(res_partner, self).address_get(cr, uid, ids, todo))
        return result

res_partner()

