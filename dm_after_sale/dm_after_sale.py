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
        'as_report' : fields.text('Report Content'),
        'document_id' : fields.many2one('dm.offer.document','Document'),
        'state': fields.selection([('draft','Draft'),('set','Set'),('done','Done')],"State",size=10),
        'display_info':fields.text('Info'),
    }

    def set_cancel(self, cr, uid, ids, *args):
        return True
    _defaults = {
             'state' : lambda *a : 'draft',
    }

    def send_document(self, cr, uid, ids, *args):
        "Create workitem and document"
        lang_id = self.pool.get('res.lang').search(cr,uid,[('code','=',args[0]['lang'])])[0]
        doc_categ_id = self.pool.get('dm.offer.document.category').search(cr,uid,[('name','=','Production')])[0]
        for i in self.browse(cr,uid,ids):
            vals = {
                'segment_id' : i.segment_id.id,
                'step_id' : i.document_id.step_id.id,
                'address_id' : args[0]['address_id'],
                'trigger_type_id' : i.action_id.id,
                'mail_service_id' : i.mail_service_id.id,
            }
            id = self.pool.get('dm.event').create(cr,uid,vals)
            production_doc_id = self.pool.get('dm.offer.document').search(cr,uid,[('step_id','=',i.document_id.step_id.id),('category_id','=','Production')])
            if not production_doc_id :
                vals = {'name':'From AS wizard production',
                        'code':'ASW Production',
                        'lang_id' : lang_id,
                        'category_id': doc_categ_id,
                        'content' : i.as_report,
                        'step_id': i.document_id.step_id.id,
                }
                doc_id = self.pool.get('dm.offer.document').create(cr,uid,vals)
            else :
                self.pool.get('dm.offer.document').write(cr,uid,[production_doc_id[0]],{'content':i.as_report})
            display_info ="Event is created for the above information and internal report is changed for the '%s' document"%i.document_id.name
            self.write(cr,uid,[i.id],{'state':'done','display_info':display_info})
        return True

    def set_content(self,cr,uid,ids,*args):
        result = []
        lang_id = self.pool.get('res.lang').search(cr,uid,[('code','=',args[0]['lang'])])[0]
        doc_categ_id = self.pool.get('dm.offer.document.category').search(cr,uid,[('name','=','After-Sale Document Template')])[0]
        for i in self.browse(cr,uid,ids):
            transition_ids = self.pool.get('dm.offer.step.transition').search(cr,uid,[('condition_id','=',i.action_id.id)])
            step_id = self.pool.get('dm.offer.step').search(cr,uid,[('incoming_transition_ids','in',transition_ids)])[0]
            if i.as_report and not i.document_id:
                vals = {'name':'From AS wizard',
                        'code':'ASW',
                        'lang_id':lang_id,
                        'category_id':doc_categ_id,
                        'content' :i.as_report,
                        'step_id' : step_id,

                }
                doc_id = self.pool.get('dm.offer.document').create(cr,uid,vals)
                result.append((i.id,{'state':'set','document_id':doc_id}))
            else :
                srch_doc_id = self.pool.get('dm.offer.document').search(cr,uid,[('step_id','=',step_id),('category_id','=','After-Sale Document Template')])
                if srch_doc_id :
                    doc_id = self.pool.get('dm.offer.document').browse(cr,uid,srch_doc_id)[0]
                    result.append((i.id,{'as_report': doc_id.content,'state':'set','document_id':srch_doc_id[0]}))
        for id,vals in result:
            self.write(cr,uid,[id],vals)
        return True
dm_after_sale_action()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
