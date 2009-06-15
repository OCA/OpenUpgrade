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

from osv import fields
from osv import osv

class dm_campaign_proposition_segment(osv.osv):
    _inherit = "dm.campaign.proposition.segment"

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context and 'address_id' in context:
            if not context['address_id']:
                return []
            wi_obj = self.pool.get('dm.workitem')
            workitems = wi_obj.search(cr,uid,[('address_id','=',context['address_id'])])
            ids = [wi.segment_id.id for wi in wi_obj.browse(cr,uid,workitems)]
            return ids
        return super(dm_campaign_proposition_segment, self).search(cr, uid, args, offset, limit, order, context, count)
dm_campaign_proposition_segment()

class dm_after_sale_action(osv.osv_memory):
    _name = "dm.after.sale.action"
    _columns = {
        'segment_id' : fields.many2one('dm.campaign.proposition.segment', 'Segment', required=True),
        'action_id' : fields.many2one('dm.offer.step.transition.trigger', 'Action', required=True),
        'mail_service_id' : fields.many2one('dm.mail_service', 'Mail Service', required=True),
        'as_report' : fields.text('Report Content')
    }

    def onchange_content(self, cr, uid, ids, action_id):
        if not action_id:
            return {}
        result = {}
        transition_ids = self.pool.get('dm.offer.step.transition').search(cr,uid,[('condition_id','=',action_id)])
        step_ids = self.pool.get('dm.offer.step').search(cr,uid,[('incoming_transition_ids','in',transition_ids)])[0]
        srch_doc_id = self.pool.get('dm.offer.document').search(cr,uid,[('step_id','=',step_ids),('category_id','=','After-Sale Document Template')])
        print "srch_doc_id", srch_doc_id
        if not srch_doc_id:
            return {}
        doc_id = self.pool.get('dm.offer.document').browse(cr,uid,srch_doc_id)[0]
        print "doc_id", doc_id.content
        result={'as_report': doc_id.content}
        print "value", result
        return {'value':result}

    def set_cancel(self, cr, uid, ids, *args):
        return True
    
    def send_document(self, cr, uid, ids, *args):
        "Creaste workitem and document"
        print "-----------------------------",
        return True
dm_after_sale_action()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
