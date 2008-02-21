
##############################################################################
#
# Copyright (c) 2007 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import fields, osv


class res_partner(osv.osv):
    _inherit = 'res.partner'
    _description = 'res.partner'
    _columns = {
        'asker_name': fields.char('Asker Name',size=50),
        'asker_address': fields.char('Asker Address',size=50),
        'asker_zip_id': fields.many2one('res.partner.zip','Asker Zip Code'),
        'sender_name': fields.char('Sender Name',size=50),
    }

res_partner()

class cci_missions_site(osv.osv):
    _name = 'cci_missions.site'
    _description = 'cci_missions.site'
    _columns = {
        'name' : fields.char('Name of the Site',size=50,required=True)
                }

cci_missions_site()

class cci_missions_certificate_type(osv.osv):
    _name = 'cci_missions.certificate_type'
    _description = 'cci_missions.certificate_type'
    _columns = {
        'code' : fields.char('Code',size=2,required=True),
        'name' : fields.char('Description',size=30,required=True),
        'original_product_id' : fields.many2one('product.product','Reference for Original Copies',required=True,help='for the association with a pricelist'),
        'copy_product_id' : fields.many2one('product.product','Reference for Copies',required=True,help='for the association with a pricelist'),
        'site_id' : fields.many2one('cci_missions.site','Site',required=True),
        'sequence_id' : fields.many2one('ir.sequence','Sequence',required=True,help='for association with a sequence'),
        'section' : fields.selection([('certificate','Certificate'),('legalization','Legalization'),('ATA Carnet','ATA Carnet')],'Type',required=True),
                }

cci_missions_certificate_type()

class cci_missions_dossier(osv.osv):
    _name = 'cci_missions.dossier'
    _description = 'cci_missions.dossier'
    _columns = {
        'name' : fields.char('Reference',size=20,required=True),#Default: '/'
        'type_id' : fields.many2one('cci_missions.certificate_type','Certificate Type',required=True),
        'date' : fields.date('Creation Date',required=True),#by default, current date
        'order_partner_id': fields.many2one('res.partner','Billed Customer',required=True),
        'asker_name':fields.char('Asker Name',size=50),#by default, res.partner->asker_name or, res_partner->name
        'sender_name':fields.char('Sender Name',size=50),#by default, res.partner->sender_name or, res_partner.address[default]->name
        'to_bill':fields.boolean('To Be Billed'),#by default: True
        'state':fields.selection([('confirmed','confirmed'),('canceled','canceled'),('invoiced','invoiced')],'State',),#by default: confirmed
        'goods':fields.char('Goods Description',size=100),
        'goods_value':fields.float('Value of the Sold Goods'),#Monetary; must be greater than zero
        'destination_id':fields.many2one('res.country','Destination Country'),
        'embassy_folder_id':fields.many2one('cci_missions.embassy_folder','Related Embassy Folder'),
        'quantity_copies':fields.integer('Number of Copies'),
        'total':fields.function('Total'),#readonly, sum of the price for copies, originals and extra_products
        'sub_total':fields.function('Sub Total for Extra Products'),#readonly, sum of the extra_products
        'text_on_invoice':fields.text('Text to Display on the Invoice')
                }
cci_missions_dossier()