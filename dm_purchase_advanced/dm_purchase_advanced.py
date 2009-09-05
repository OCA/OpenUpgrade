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
from mx import DateTime
import netsvc

class one2many_mod_pline(fields.one2many):#{{{
    def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
        if not context:
            context = {}
        if not values:
                values = {}
        res = {}
        for id in ids:
            res[id] = []
        cr.execute("select id from product_category where name='Direct Marketing'")
        direct_id = cr.fetchone()
        sql="select id,name from product_category where parent_id=%d" %direct_id
        cr.execute(sql)
        res_type = cr.fetchall()
        type={}
        for x in res_type:
            type[x[1]]=x[0]
        for id in ids:
            if name[0] == 'd':
                ids2 = obj.pool.get(self._obj).search(cr, user, [('campaign_id','=',id),('product_category','=',type['DTP'])], limit=self._limit)
            elif name[0] == 'm':
                ids2 = obj.pool.get(self._obj).search(cr, user, [('campaign_id','=',id),('product_category','=',type['Mailing Manufacturing'])], limit=self._limit)
            elif name[0] == 'c':
                ids2 = obj.pool.get(self._obj).search(cr, user, [('campaign_id','=',id),('product_category','=',type['Customers List'])], limit=self._limit)
            elif name[0] == 'i':
                ids2 = obj.pool.get(self._obj).search(cr, user, [('campaign_id','=',id),('product_category','=',type['Items'])], limit=self._limit)
            else :
                ids2 = obj.pool.get(self._obj).search(cr, user, [('campaign_id','=',id),('product_category','=',type['Mailing Manufacturing'])], limit=self._limit)
            for r in obj.pool.get(self._obj)._read_flat(cr, user, ids2, [self._fields_id], context=context, load='_classic_write'):
                res[id].append( r['id'] )
        return res#}}}

class dm_campaign(osv.osv): # {{{
    _inherit = "dm.campaign"
    _columns = {
        'manufacturing_responsible_id' : fields.many2one('res.users','Responsible'),
        'dtp_responsible_id' : fields.many2one('res.users','Responsible'),
        'files_responsible_id' : fields.many2one('res.users','Responsible'),
        'item_responsible_id' : fields.many2one('res.users','Responsible'),
        'dtp_purchase_line_ids': one2many_mod_pline('dm.campaign.purchase_line', 'campaign_id', "DTP Purchase Lines",
                                                        domain=[('product_category','=','DTP')], context={'product_category':'DTP'}),
        'manufacturing_purchase_line_ids': one2many_mod_pline('dm.campaign.purchase_line', 'campaign_id', "Manufacturing Purchase Lines",
                                                        domain=[('product_category','=','Mailing Manufacturing')],
                                                        context={'product_category':'Mailing Manufacturing'}),
        'cust_file_purchase_line_ids': one2many_mod_pline('dm.campaign.purchase_line', 'campaign_id', "Customer Files Purchase Lines",
                                                        domain=[('product_category','=','Customers List')], context={'product_category':'Customers List'}),
        'item_purchase_line_ids': one2many_mod_pline('dm.campaign.purchase_line', 'campaign_id', "Items Purchase Lines",
                                                        domain=[('product_category','=','Items')], context={'product_category':'Items'}),

    }
dm_campaign() # }}}

PURCHASE_LINE_TRIGGERS = [ # {{{
    ('draft','At Draft'),
    ('open','At Open'),
    ('planned','At Planning'),
    ('close','At Close'),
    ('manual','Manual'),
]

PURCHASE_LINE_STATES = [
    ('pending','Pending'),
    ('requested','Quotations Requested'),
    ('ordered','Ordered'),
    ('delivered','Delivered'),
]

PURCHASE_LINE_TYPES = [
    ('manufacturing','Manufacturing'),
    ('items','Items'),
    ('customer_file','Customer Files'),
    ('translation','Translation'),
    ('dtp','DTP'),
]

QTY_TYPES = [
    ('quantity_planned','planned Quantity'),
    ('quantity_wanted','Wanted Quantity'),
    ('quantity_delivered','Delivered Quantity'),
    ('quantity_usable','Usable Quantity'),
]

DOC_TYPES = [
    ('po','Purchase Order'),
    ('rfq','Request For Quotation'),
] # }}}

class dm_campaign_purchase_line(osv.osv):#{{{
    _name = 'dm.campaign.purchase_line'
    _rec_name = 'product_id'

#    def default_get(self, cr, uid, fields, context=None):
#        if context.has_key('product_category'):
#            raise osv.except_osv('Warning', "Purchase order generation is not yet implemented")
#        return super(dm_campaign_purchase_line, self).default_get(cr, uid, fields, context)

    def _get_uom_id(self, cr, uid, *args):
        cr.execute('select id from product_uom order by id limit 1')
        res = cr.fetchone()
        return res and res[0] or False

    def pline_doc_generate(self,cr, uid, ids, *args):
        "Genererates Documents (POs or Request fo Quotations) for Purchase Lines"
        plines = self.browse(cr, uid ,ids)

        for pline in plines:
            if pline.state == 'pending':

                obj = pline.campaign_id
                code = pline.campaign_id.code1

                if not pline.product_id.seller_ids:
                    raise  osv.except_osv('Warning', "There's no supplier defined for this product : %s" % (pline.product_id.name,) )


                "If Mailing Manufacturing purchase line"
                if int(pline.product_category) == self.pool.get('product.category').search(cr, uid,[('name','=','Mailing Manufacturing')])[0]:

                    "If the product is a compound product (BoM) => Add Subproducts infos in document notes"
                    note = []
                    cr.execute("select id from mrp_bom where product_id = %s limit 1" % (pline.product_id.id))
                    bom_id = cr.fetchone()
                    if bom_id:
                        bom = self.pool.get('mrp.bom').browse(cr, uid, [bom_id[0]])[0]
                        note.append("Product Composed of : ")
                        note.append("---------------------------------------------------------------------------")
                        for bom_child in bom.child_ids:
                            note.append(bom_child.name)
                            note.append("---------------------------------------------------------------------------")

                    "Get Manufacturing Descriptions if asked"
                    if pline.desc_from_offer:
                        for step in obj.offer_id.step_ids:
                            for const in step.manufacturing_constraint_ids:
                                if not const.country_ids:
                                    note.append("---------------------------------------------------------------------------")
                                    note.append("Description : ")
                                    note.append("---------------------------------------------------------------------------")
                                    note.append(const.name)
                                    note.append(const.constraint)
                                elif obj.country_id in const.country_ids:
                                    note.append("---------------------------------------------------------------------------")
                                    note.append(const.name + ' for country :' +  obj.country_id.name)
                                    note.append(const.constraint)

                    "Add note if defined"
                    if pline.notes:
                        note.append("---------------------------------------------------------------------------")
                        note.append(pline.notes)
                    else:
                        note.append(' ')

                    "If Document Type is Request for Quotation => create 1 Request for Quotation/Supplier grouped in a Tender"
                    "If Document Type is Purchase Order => Create One Purchase Order for the main Supplier"
                    if pline.type_document == 'rfq':

                        "Create Purchase tender"
                        tender_id = self.pool.get('purchase.tender').create(cr, uid,{'state':'open'})

                        "Get Suppliers infos"
                        for supplier in pline.product_id.seller_ids:
                            partner_id = supplier.id
                            partner = supplier.name

                            address_id = self.pool.get('res.partner').address_get(cr, uid, [partner.id], ['default'])['default']
                            if not address_id:
                                raise osv.except_osv('Warning', "There is no default address defined for this partner : %s" % (partner.name,) )
                            delivery_address = address_id
                            pricelist_id = partner.property_product_pricelist_purchase.id
                            if not pricelist_id:
                                raise osv.except_osv('Warning', "There is no purchase pricelist defined for this partner : %s" % (partner.name,) )
                            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_id], pline.product_id.id, pline.quantity, False, {'uom': pline.uom_id.id})[pricelist_id]
                            newdate = DateTime.strptime(pline.date_planned, '%Y-%m-%d %H:%M:%S') - DateTime.RelativeDateTime(days=pline.product_id.product_tmpl_id.seller_delay or 0.0)

                            "Create Document"
                            purchase_id = self.pool.get('purchase.order').create(cr, uid, {
                                'origin': code,
                                'partner_id': partner.id,
                                'partner_address_id': address_id,
                                #'dest_address_id': delivery_address.id,
                                'location_id': 1,
                                'pricelist_id': pricelist_id,
                                'notes': "\n".join(note),
                                'tender_id': tender_id,
                                'dm_campaign_purchase_line': pline.id
                            })

                            "Create po lines for each proposition"
                            lines = []
                            for propo in obj.proposition_ids:
                                line_name = propo.code1 + '-' + propo.type

                                if pline.type_quantity == 'quantity_planned':
                                    quantity = propo.quantity_planned
                                elif pline.type_quantity == 'quantity_wanted':
                                    if propo.quantity_wanted.isdigit():
                                        quantity = propo.quantity_wanted
                                    elif propo.quantity_wanted == 'AAA for a Segment':
                                        raise osv.except_osv('Warning',
                                            'Cannot use wanted quantity for Mailing Manufacturing if there is AAA defined for a segment')
                                    else :
                                        raise osv.except_osv('Warning',
                                            'Cannot get wanted quantity, check prososition %s' % (propo.name,))
                                elif pline.type_quantity == 'quantity_delivered':
                                    if propo.quantity_delivered.isdigit():
                                        quantity = propo.quantity_delivered
                                    else : 
                                        raise osv.except_osv('Warning',
                                            'Cannot get delivered quantity, check prososition %s' % (propo.name,))
                                elif pline.type_quantity == 'quantity_usable':
                                    if propo.quantity_usable.isdigit():
                                        quantity = propo.quantity_usable
                                    else : 
                                        raise osv.except_osv('Warning',
                                            'Cannot get delivered quantity, check prososition %s' % (propo.name,))
                                else:
                                    raise osv.except_osv('Warning','Error getting quantity for proposition %s' % (propo.name,))

                                line = self.pool.get('purchase.order.line').create(cr, uid, {
                                   'order_id': purchase_id,
                                   'name': line_name,
                                   'product_qty': quantity,
                                   'product_id': pline.product_id.id,
                                   'product_uom': pline.uom_id.id,
                                   'price_unit': price,
                                   'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                                   'taxes_id': [(6, 0, [x.id for x in pline.product_id.product_tmpl_id.supplier_taxes_id])],
                                   'account_analytic_id': propo.analytic_account_id.id,
                                })

                    elif pline.type_document == 'po':

                        "Create 1 PO for the main supplier"
                        "Get the main supplier = the 1st product supplier with sequence = 1"
                        cr.execute('select name from product_supplierinfo where product_id = %s and sequence = 1', (pline.product_id.id,))
                        res = cr.fetchone()
                        supplier = self.pool.get('res.partner').browse(cr,uid,[res[0]])[0]
                        partner_id = supplier.id
                        partner = supplier.name

                        address_id = self.pool.get('res.partner').address_get(cr, uid, [supplier.id], ['default'])['default']
                        if not address_id:
                            raise osv.except_osv('Warning', "There is no default address defined for this partner : %s" % (supplier.name,) )
                        delivery_address = address_id
                        pricelist_id = supplier.property_product_pricelist_purchase.id
                        if not pricelist_id:
                            raise osv.except_osv('Warning', "There is no purchase pricelist defined for this partner : %s" % (supplier.name,) )
                        price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_id], pline.product_id.id, pline.quantity, False, {'uom': pline.uom_id.id})[pricelist_id]
                        newdate = DateTime.strptime(pline.date_planned, '%Y-%m-%d %H:%M:%S') - DateTime.RelativeDateTime(days=pline.product_id.product_tmpl_id.seller_delay or 0.0)

                        "Create Document"
                        purchase_id = self.pool.get('purchase.order').create(cr, uid, {
                            'origin': code,
                            'partner_id': supplier.id,
                            'partner_address_id': address_id,
                            #'dest_address_id': delivery_address.id,
                            'location_id': 1,
                            'pricelist_id': pricelist_id,
                            'notes': "\n".join(note),
                            'dm_campaign_purchase_line': pline.id
                        })

                        # Set as PO
                        wf_service = netsvc.LocalService("workflow")
                        wf_service.trg_validate(uid, 'purchase.order', purchase_id, 'purchase_confirm', cr)

                        "Create po lines for each proposition"
                        lines = []
                        for propo in obj.proposition_ids:
                            line_name = propo.code1 + '-' + propo.type

                            if pline.type_quantity == 'quantity_planned':
                                quantity = propo.quantity_planned
                            elif pline.type_quantity == 'quantity_wanted':
                                if propo.quantity_wanted.isdigit():
                                    quantity = propo.quantity_wanted
                                elif propo.quantity_wanted == 'AAA for a Segment':
                                    raise osv.except_osv('Warning',
                                        'Cannot use wanted quantity for Mailing Manufacturing if there is AAA defined for a segment')
                                else :
                                    raise osv.except_osv('Warning',
                                        'Cannot get wanted quantity, check prososition %s' % (propo.name,))
                            elif pline.type_quantity == 'quantity_delivered':
                                if propo.quantity_delivered.isdigit():
                                    quantity = propo.quantity_delivered
                                else : 
                                    raise osv.except_osv('Warning',
                                        'Cannot get delivered quantity, check prososition %s' % (propo.name,))
                            elif pline.type_quantity == 'quantity_usable':
                                if propo.quantity_usable.isdigit():
                                    quantity = propo.quantity_usable
                                else : 
                                    raise osv.except_osv('Warning',
                                        'Cannot get delivered quantity, check prososition %s' % (propo.name,))
                            else:
                                raise osv.except_osv('Warning','Error getting quantity for proposition %s' % (propo.name,))

                            line = self.pool.get('purchase.order.line').create(cr, uid, {
                               'order_id': purchase_id,
                               'name': line_name,
                               'product_qty': quantity,
                               'product_id': pline.product_id.id,
                               'product_uom': pline.uom_id.id,
                               'price_unit': price,
                               'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                               'taxes_id': [(6, 0, [x.id for x in pline.product_id.product_tmpl_id.supplier_taxes_id])],
                               'account_analytic_id': propo.analytic_account_id,
                            })

                    else:
                        raise osv.except_osv('Warning', "The's no Document Type defined for this Purchase Line")

                    "If Customers List purchase line"
                elif int(pline.product_category) == self.pool.get('product.category').search(cr, uid,[('name','=','Customers List')])[0]:

                    "Get Customers File note if asked"
                    note = []
                    if pline.desc_from_offer:
                        note.append("---------------------------------------------------------------------------")
                        note.append('Campaign Name : %s' % (obj.name,))
                        note.append('Campaign Code : %s' % (obj.code1,))
                        note.append('Drop Date : %s' % (obj.date_start,))
                        note.append("---------------------------------------------------------------------------")
                        note.append('Trademark : %s' % (obj.trademark_id.name,))
                        note.append('planned Quantity : %s' % (obj.quantity_planned_total,))
                        note.append('Responsible : %s' % (obj.files_responsible_id.name,))

                    "Add note if defined"
                    if pline.notes:
                        note.append("---------------------------------------------------------------------------")
                        note.append(pline.notes)
                    else:
                        note.append(' ')

                    "If Document Type is Request for Quotation => create 1 Request for Quotation/Supplier grouped in a Tender"
                    "If Document Type is Purchase Order => Create One Purchase Order for the main Supplier"
                    if pline.type_document == 'rfq':

                        """Create Purchase tender"""
                        tender_id = self.pool.get('purchase.tender').create(cr, uid,{'state':'open'})

                        "Get Suppliers infos"
                        for supplier in pline.product_id.seller_ids:
                            partner_id = supplier.id
                            partner = supplier.name

                            address_id = self.pool.get('res.partner').address_get(cr, uid, [partner.id], ['default'])['default']
                            if not address_id:
                                raise osv.except_osv('Warning', "There's no default address defined for this partner : %s" % (partner.name,) )
                            delivery_address = address_id
                            pricelist_id = partner.property_product_pricelist_purchase.id
                            if not pricelist_id:
                                raise osv.except_osv('Warning', "There's no purchase pricelist defined for this partner : %s" % (partner.name,) )
                            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_id], pline.product_id.id, pline.quantity, False, {'uom': pline.uom_id.id})[pricelist_id]
                            newdate = DateTime.strptime(pline.date_planned, '%Y-%m-%d %H:%M:%S') - DateTime.RelativeDateTime(days=pline.product_id.product_tmpl_id.seller_delay or 0.0)

                            "Create Document"
                            purchase_id = self.pool.get('purchase.order').create(cr, uid, {
                                'origin': code,
                                'partner_id': partner.id,
                                'partner_address_id': address_id,
                                #'dest_address_id': delivery_address.id,
                                'location_id': 1,
                                'pricelist_id': pricelist_id,
                                'notes': "\n".join(note),
                                'tender_id': tender_id,
                                'dm_campaign_purchase_line': pline.id
                            })

                            "Create po lines for each proposition (of each campaign if group)"
                            lines = []
                            for propo in obj.proposition_ids:
                                for segment in propo.segment_ids:
                                    line_name = propo.code1 + ' - ' + segment.customers_list_id.name
                                    if pline.type_quantity == 'quantity_planned':
                                        quantity = segment.quantity_planned
                                    elif pline.type_quantity == 'quantity_wanted':
                                        quantity = segment.quantity_wanted
                                        if segment.all_add_avail:
                                            quantity = 0
                                            line_name = propo.code1 + ' - ' + segment.customers_list_id.name + ' - All Addresses Available'
                                    elif pline.type_quantity == 'quantity_delivered':
                                        quantity = propo.quantity_delivered
                                    elif pline.type_quantity == 'quantity_usable':
                                        quantity = propo.quantity_usable
                                    else:
                                        raise osv.except_osv('Warning','Error getting quantity for proposition %s' % (propo.name,))

                                    line = self.pool.get('purchase.order.line').create(cr, uid, {
                                       'order_id': purchase_id,
                                       'name': line_name,
                                       'product_qty': quantity,
                                       'product_id': pline.product_id.id,
                                       'product_uom': pline.uom_id.id,
                                       'price_unit': price,
                                       'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                                       'taxes_id': [(6, 0, [x.id for x in pline.product_id.product_tmpl_id.supplier_taxes_id])],
                                       'account_analytic_id': propo.analytic_account_id,
                                    })

                    elif pline.type_document == 'po':

                        """Create 1 PO for the main supplier"""
                        """Get the customers list = supplier in Customers List for that country"""

                        lists = []
                        for propo in obj.proposition_ids:
                            for segment in propo.segment_ids:
                                lists.append(segment.customers_list_id)
                        cust_lists = set(lists)

                        """Create 1 PO / Customets List"""
                        for list in cust_lists:
                            print "--- Enter List : ", list.name
                            if list.broker_id:
                                partner = list.broker_id
                            else:
                                raise osv.except_osv('Warning', "There's no broker defined for this list : %s" % (list.name,) )
                                
                            address_id = self.pool.get('res.partner').address_get(cr, uid, [partner.id], ['default'])['default']
                            if not address_id:
                                raise osv.except_osv('Warning', "There's no default address defined for this partner : %s" % (partner.name,) )
                            if pline.campaign_id.cleaner_id :
                                dest_address_id = self.pool.get('res.partner').address_get(cr, uid, [pline.campaign_id.cleaner_id.id], ['default'])['default']
                                if not address_id:
                                    raise osv.except_osv('Warning', "There's no default address defined for this partner : %s" % (pline.campaign_id.cleaner_id.name,) )
                            elif pline.campaign_id.deduplicator_id :
                                dest_address_id = self.pool.get('res.partner').address_get(cr, uid, [pline.campaign_id.deduplicator_id.id], ['default'])['default']
                                if not address_id:
                                    raise osv.except_osv('Warning', "There's no default address defined for this partner : %s" % (pline.campaign_id.deduplicator_id.name,) )
                            elif pline.campaign_id.router_id :
                                dest_address_id = self.pool.get('res.partner').address_get(cr, uid, [pline.campaign_id.router_id.id], ['default'])['default']
                                if not address_id:
                                    raise osv.except_osv('Warning', "There's no default address defined for this partner : %s" % (pline.campaign_id.router_id.name,) )
                            else:
                                raise osv.except_osv('Warning', "There's no intermediaries defined for this campaign") 

                            pricelist_id = partner.property_product_pricelist_purchase.id
                            if not pricelist_id:
                                raise osv.except_osv('Warning', "There's no purchase pricelist defined for this partner : %s" % (partner.name,) )
                            newdate = DateTime.strptime(pline.date_planned, '%Y-%m-%d %H:%M:%S') - DateTime.RelativeDateTime(days=pline.product_id.product_tmpl_id.seller_delay or 0.0)

                            """Create Document"""
                            purchase_id = self.pool.get('purchase.order').create(cr, uid, {
                                'origin': code,
                                'partner_id': partner.id,
                                'partner_address_id': address_id,
                                'dest_address_id': dest_address_id,
                                'location_id': 1,
                                'pricelist_id': pricelist_id,
                                'notes': "\n".join(note),
                                'dm_campaign_purchase_line': pline.id
                            })

                            # Set as PO
                            wf_service = netsvc.LocalService("workflow")
                            wf_service.trg_validate(uid, 'purchase.order', purchase_id, 'purchase_confirm', cr)

                            """Creare a PO line / segment for that Customers List"""
                            lines = []
                            for propo in obj.proposition_ids:
                                for segment in propo.segment_ids:
                                    if segment.customers_list_id == list:
                                        line_name = propo.code1 + ' - ' + segment.customers_list_id.name
                                        if pline.type_quantity == 'quantity_planned':
                                            quantity = segment.quantity_planned
                                        elif pline.type_quantity == 'quantity_wanted':
                                            quantity = segment.quantity_wanted
                                            if segment.all_add_avail:
                                                quantity = 0
                                                line_name = propo.code1 + ' - ' + segment.customers_list_id.name + ' - All Addresses Available'
                                        elif pline.type_quantity == 'quantity_delivered':
                                            quantity = propo.quantity_delivered
                                        elif pline.type_quantity == 'quantity_usable':
                                            quantity = propo.quantity_usable
                                        else:
                                            raise osv.except_osv('Warning','Error getting quantity for proposition %s' % (propo.name,))

                                        """Compute price"""
                                        price = ((list.per_thousand_price / 1000) * ((100 - list.broker_discount) / 100) * (list.selection_cost / 1000)) + list.delivery_cost + list.other_cost
                                        line = self.pool.get('purchase.order.line').create(cr, uid, {
                                           'order_id': purchase_id,
                                           'name': line_name,
                                           'product_qty': quantity,
                                           'product_id': pline.product_id.id,
                                           'product_uom': pline.uom_id.id,
                                           'price_unit': price,
                                           'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                                           'taxes_id': [(6, 0, [x.id for x in pline.product_id.product_tmpl_id.supplier_taxes_id])],
                                           'account_analytic_id': propo.analytic_account_id,
                                        })

                    else:
                        raise osv.except_osv('Warning', "The's no Document Type defined for this Purchase Line")

                elif int(pline.product_category) == self.pool.get('product.category').search(cr, uid,[('name','=','DTP')])[0]:
                    """If DTP purchase line"""
                    raise osv.except_osv('Warning', "Purchase of DTP is not yet implemented")

                elif int(pline.product_category) == self.pool.get('product.category').search(cr, uid,[('name','=','Item')])[0]:
                    """If Items purchase line"""
                    raise osv.except_osv('Warning', "Purchase of items is not yet implemented")

                elif int(pline.product_category) == self.pool.get('product.category').search(cr, uid,[('name','=','Translation')])[0]:
                    """If Translation purchase line"""
                    raise osv.except_osv('Warning', "Purchase of translations is not yet implemented")

                    if not obj.lang_id:
                        raise osv.except_osv('Warning', "There's no language defined for this campaign : %s" % (obj.name,) )
                    if pline.notes:
                        constraints.append(pline.notes)
                    else:
                        constraints.append(' ')

                    quantity=0
                    for step in pline.campaign_id.offer_id.step_ids:
                        quantity += step.doc_number
                    line = self.pool.get('purchase.order.line').create(cr, uid, {
                       'order_id': purchase_id,
                       'name': code,
                       'product_qty': quantity,
                       'product_id': pline.product_id.id,
                       'product_uom': pline.uom_id.id,
                       'price_unit': price,
                       'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                       'taxes_id': [(6, 0, [x.id for x in pline.product_id.product_tmpl_id.supplier_taxes_id])],
#                           'account_analytic_id': obj.analytic_account_id,
                    })

                else:
                    raise osv.except_osv('Warning', "The's no Product Category defined for this Purchase Line")
        self.write(cr, uid, ids, {'state':'ordered'})
        return True

    def _default_date(self, cr, uid, context={}):
        if 'date1' in context and context['date1']:
            dd = context['date1']
            newdate =  DateTime.strptime(dd + ' 09:00:00','%Y-%m-%d %H:%M:%S')
            #print "From _default_date : ",newdate.strftime('%Y-%m-%d %H:%M:%S')
            return newdate.strftime('%Y-%m-%d %H:%M:%S')
        return []

    def _state_get(self, cr, uid, ids, name, args, context={}):
        result = {}
        for pline in self.browse(cr, uid, ids):
            delivered=False
            ordered=False
            print 'pline po ids : ',pline.purchase_order_ids
            if pline.purchase_order_ids:
                for po in pline.purchase_order_ids:
                    if delivered:
                        continue
                    if po.shipped:
                        result[pline.id]='delivered'
                        delivered=True
                        if pline.type == 'translation':
                            trans_id = self.pool.get('dm.offer.translation').create(cr, uid,
                                {'offer_id': pline.campaign_id.offer_id.id,
                                 'date': pline.date_delivery,
                                 'language_id': pline.campaign_id.lang_id.id,
                                 'translator_id':  po.partner_id.id,
                                 'notes': pline.notes,
                                 })
                        continue
                    if ordered:
                        continue
                    if po.state == 'confirmed' or po.state == 'approved':
                        result[pline.id]='ordered'
                        ordered=True
                    if po.state == 'draft':
                        result[pline.id]='requested'
            else:
                result[pline.id] = 'pending'
        return result

    def _delivery_date_get(self, cr, uid, ids, name, args, context={}):
        result = {}
        for pline in self.browse(cr, uid, ids):
            result[pline.id] = False
            for po in pline.purchase_order_ids:
                if po.shipped:
                    if po.picking_ids:
                        result[pline.id] = po.picking_ids[0].date_done
                    continue
        return result

    def _default_category_get(self, cr, uid, context):
        if 'product_category' in context and context['product_category']:
            cr.execute('select id from product_category where name=%s order by id limit 1', (context['product_category'],))
        else:
            cr.execute('select id from product_category where name=%s order by id limit 1', ('Mailing Manufacturing',))
        res = cr.fetchone()
        return str(res[0]) or False

    def _product_category_get(self,cr,uid,context={}):
        type_obj = self.pool.get('product.category')
        dmcat_id = type_obj.search(cr,uid,[('name','ilike','Direct Marketing')])[0]
        type_ids = type_obj.search(cr,uid,[('parent_id','=',dmcat_id)])
        type = type_obj.browse(cr,uid,type_ids)
        return map(lambda x : [str(x.id),x.name],type) 

    def _default_quantity_get(self, cr, uid, context):
        if 'product_category' in context and context['product_category']:
            if context['product_category'] == 'Mailing Manufacturing':
                return 'quantity_planned'
            elif context['product_category'] == 'Customers List':
                return 'quantity_wanted'
        return 'quantity_planned'

    def _default_doctype_get(self, cr, uid, context):
        if 'product_category' in context and context['product_category']:
            if context['product_category'] == 'Mailing Manufacturing':
                return 'rfq'
            elif context['product_category'] == 'Customers List':
                return 'po'
        return 'rfq'


    _columns = {
        'campaign_id': fields.many2one('dm.campaign', 'Campaign'),
        'product_id' : fields.many2one('product.product', 'Product', required=True, context={'flag':True}),
        'quantity' : fields.integer('Total Quantity', readonly=False, required=True),
        'quantity_warning' : fields.char('Warning', size=128, readonly=True),
        'type_quantity' : fields.selection(QTY_TYPES, 'Quantity Type', size=32),
        'type_document' : fields.selection(DOC_TYPES, 'Document Type', size=32),
        'product_category' : fields.selection(_product_category_get, 'Product Category', size=64 ,select=True),
        'uom_id' : fields.many2one('product.uom','UOM', required=True),
        'date_order': fields.datetime('Order date', readonly=True),
        'date_planned': fields.datetime('Scheduled date', required=True),
        'date_delivery': fields.function(_delivery_date_get, method=True, type='datetime', string='Delivery Date', readonly=True),
        'trigger' : fields.selection(PURCHASE_LINE_TRIGGERS, 'Trigger'),
        'type' : fields.selection(PURCHASE_LINE_TYPES, 'Type'),
        'purchase_order_ids' : fields.one2many('purchase.order','dm_campaign_purchase_line','Campaign Purchase Line'),
        'notes': fields.text('Notes'),
        'desc_from_offer' : fields.boolean('Insert Description from Offer'),
        'state' : fields.function(_state_get, method=True, type='selection', selection=[
            ('pending','Pending'),
            ('requested','Quotations Requested'),
            ('ordered','Ordered'),
            ('delivered','Delivered'),
            ], string='State', store=True, readonly=True),
    }

    _defaults = {
#        'date_planned' : _default_date,
        'quantity' : lambda *a : 0,
        'product_category' : _default_category_get,
        'uom_id' : _get_uom_id,
        'trigger': lambda *a : 'manual',
        'state': lambda *a : 'pending',
        'type_quantity': _default_quantity_get,
        'type_document': _default_doctype_get,
        'desc_from_offer': lambda *a : True,
    }
dm_campaign_purchase_line()#}}}

class purchase_order(osv.osv):#{{{
    _name = 'purchase.order'
    _inherit = 'purchase.order'
    _columns = {
        'dm_campaign_purchase_line' : fields.many2one('dm.campaign.purchase_line','DM Campaign Purchase Line'),
    }
purchase_order()#}}}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
