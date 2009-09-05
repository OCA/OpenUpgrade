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
        criteria=[]
        if context and 'address_id' in context:
            if not context['address_id']:
                return []
            criteria.append(('address_id','=',context['address_id']))
        if context and 'sale_order_id' in context:
            if not context['sale_order_id']:
                return []
            criteria.append(('sale_order_id','=',context['sale_order_id']))
        if criteria:
            wi_obj = self.pool.get('dm.workitem')
            workitems = wi_obj.search(cr,uid,criteria)
            ids = [wi.segment_id.id for wi in wi_obj.browse(cr,uid,workitems)]
            return ids
        return super(dm_campaign_proposition_segment, self).search(cr, uid, args, offset, limit, order, context, count)
dm_campaign_proposition_segment()

class dm_after_sale_action(osv.osv_memory):
    _name = "dm.after.sale.action"
    _columns = {
        'segment_id' : fields.many2one('dm.campaign.proposition.segment', 'Segment', required=True),
        'action_id' : fields.many2one('dm.offer.step.transition.trigger', 'Action', domain=[('type','=','as')], required=True),
        'mail_service_id' : fields.many2one('dm.mail_service', 'Mail Service'),
        'as_report' : fields.text('Report Content'),
        'document_id' : fields.many2one('dm.offer.document','Document'),
        'state': fields.selection([('draft','Draft'),('set','Set'),('done','Done')],"State",size=10),
        'display_info':fields.text('Info'),
    }

    def default_get(self, cr, uid, fields, context=None):
        if context.has_key('sale_order_id'):
            workitem = self.pool.get('dm.workitem').search(cr,uid,[('sale_order_id','=',context['sale_order_id'])])
            if not workitem:
                 raise osv.except_osv(
                  _('Cannot perform After-Sale Action'),
                  _('This sale order doesnt seem to originate from a Direct Marketing campaign'))
        return super(dm_after_sale_action, self).default_get(cr, uid, fields, context)

    def set_cancel(self, cr, uid, ids, *args):
        return True
    _defaults = {
             'state' : lambda *a : 'draft',
    }

    def send_document(self, cr, uid, ids, *args):
        "Create workitem and document"
        lang_id = self.pool.get('res.lang').search(cr,uid,[('code','=',args[0]['lang'])])[0]
        doc_categ_id = self.pool.get('dm.offer.document.category').search(cr,uid,[('name','=','Production')])
        # to improve : not multimedia
        step = address = mail_service = sale_order = False
        if args and 'sale_order_id' in args[0] and args[0]['sale_order_id']:
            workitem = self.pool.get('dm.workitem').search(cr,uid,[('sale_order_id','=',args[0]['sale_order_id'])])
            if workitem:
                wi_browse_id = self.pool.get('dm.workitem').browse(cr, uid, workitem[0])
                for camp_mail_service in wi_browse_id.segment_id.proposition_id.camp_id.mail_service_ids:
                    if wi_browse_id.step_id.id == camp_mail_service.offer_step_id.id:
                        mail_service = camp_mail_service.mail_service_id.id
                step_id = self.pool.get('dm.offer.step').search(cr,uid,[('code','=','ASEVENT-EMAIL')])
                if step_id:
                    step = step_id[0]
                address = wi_browse_id.address_id.id
                sale_order = args[0]['sale_order_id']

        if args and 'address_id' in args[0] and args[0]['address_id']:
            # TO FIX : works only for email
            step_id = self.pool.get('dm.offer.step').search(cr,uid,[('code','=','ASEVENT-EMAIL')])
            if step_id:
                step = step_id[0]
            address = args[0]['address_id']
            mail_service = self.browse(cr,uid,ids[0]).mail_service_id.id

        for i in self.browse(cr,uid,ids):
            vals = {
                'segment_id' : i.segment_id.id,
                'step_id' : step,
                'address_id' : address,
                'sale_order_id' : sale_order,
                'trigger_type_id' : i.action_id.id,
                'mail_service_id' : mail_service,
            }
            id = self.pool.get('dm.event.sale').create(cr,uid,vals)
            production_doc_id = self.pool.get('dm.offer.document').search(cr,uid,[('step_id','=',i.document_id.step_id.id),('category_id','=','Production')])
            if not production_doc_id :
                vals = {'name':'From AS wizard production',
                        'code':'ASW Production',
                        'lang_id' : lang_id,
                        'category_id': doc_categ_id and doc_categ_id[0] or False,
                        'content' : i.as_report,
                        'step_id': i.document_id.step_id.id,
                        'subject' : 'After-Sale Document',
                        'editor' : 'internal',
                }
                doc_id = self.pool.get('dm.offer.document').create(cr,uid,vals)
            else :
                self.pool.get('dm.offer.document').write(cr,uid,[production_doc_id[0]],{'content':i.as_report})
            display_info ="Document '%s' sucessfully sent"%i.document_id.name
            self.write(cr,uid,[i.id],{'state':'done','display_info':display_info})
        return True

    def set_content(self,cr,uid,ids,*args):
        result = []
        lang_id = self.pool.get('res.lang').search(cr,uid,[('code','=',args[0]['lang'])])[0]
        doc_categ_id = self.pool.get('dm.offer.document.category').search(cr,uid,[('name','=','After-Sale Document Template')])
        for i in self.browse(cr,uid,ids):
            transition_ids = self.pool.get('dm.offer.step.transition').search(cr,uid,[('condition_id','=',i.action_id.id)])
            step_id = self.pool.get('dm.offer.step').search(cr,uid,[('incoming_transition_ids','in',transition_ids)])[0]
            if i.as_report and not i.document_id:
                vals = {'name':'From AS wizard',
                        'code':'ASW',
                        'lang_id':lang_id,
                        'category_id':doc_categ_id and doc_categ_id[0] or False,
                        'content' :i.as_report,
                        'step_id' : step_id,
                        'subject' : 'After-Sale Document',
                        'editor' : 'internal',
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
