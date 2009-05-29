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

from osv import osv, fields
from tools.translate import _
    
import sys, os
import smtplib
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.Header import Header
from email.Utils import formatdate, COMMASPACE
from email import Encoders    

class ecommerce_partner(osv.osv):
    
    _description = 'ecommerce partner'
    _name = "ecommerce.partner"
    _order = "name"

    def _lang_get(self, cr, uid, context={}):
        obj = self.pool.get('res.lang')
        ids = obj.search(cr, uid, [], context=context)
        res = obj.read(cr, uid, ids, ['code', 'name'], context)
        return [(r['code'], r['name']) for r in res] + [('','')]
    
    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True,
                             help="Its ecommerce partner name and address"),
        'last_name': fields.char('Last Name', size=128, select=True),
        'lang': fields.selection(_lang_get, 'Language', size=5),
        'company_name': fields.char('Company Name', size=64),
        'active': fields.boolean('Active'),
        'address_ids': fields.one2many('ecommerce.partner.address', 'partner_id', 'Contacts'),
        'category_ids': fields.many2many('res.partner.category', 'ecommerce_partner_category_rel',
                                          'partner_id', 'category_id', 'Categories'),
    }
    _defaults = {
        'active': lambda *a: 1,
    }
  
    def user_get(self, cr, login=None):
        
        cr.execute("select * from res_users")
        res = cr.dictfetchall()
        if(login == None):
            userdata = map(lambda x: x['user_code'], res)
        else:
            userdata = map(lambda x: x['login'], res)
            
        return userdata
    
    def userdata_get(self, cr, uid, email_code, check=None, context={}):
      
        up_data = None
        if (check == None):
            cr.execute("select id from res_users where user_code = %s", (str(email_code), ))
            result = cr.fetchone()
        else:
            cr.execute("select id from res_users where login = %s", (str(email_code), ))
            result = cr.fetchone()
        if(result):
            user_id = result[0]
            res_users = self.pool.get('res.users')
            ecommerce_user = res_users.browse(cr, uid, user_id)
            get_data = res_users.read(cr, uid, ecommerce_user.id, [], context)
            if(check == None):
                res_users.write(cr, uid, get_data['id'], {'active':True})
                       
            up_data = res_users.read(cr, uid, ecommerce_user.id, [], context)
        return up_data
 
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=80):
        
        if not args:
            args = []
        if not context:
            context = {}
        if name:
            ids = self.search(cr, uid, [('ref', '=', name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, uid, [('name', operator, name)] + args, limit = limit, context = context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context=context)
    
    def address_get(self, cr, uid, ids, adr_pref=['default']):
        
        cr.execute('select type,id from ecommerce_partner_address where partner_id in ('+','.join(map(str, ids))+')')
        res = cr.fetchall()
        adr = dict(res)
        result = {}
        if res:
            default_address = adr.get('default', res[0][1])
        else:
            default_address = False
        
        for a in adr_pref:
            result[a] = adr.get(a, default_address)
        return result
    
    def delivery_grid(self, cr, uid, shop_id, adr_dict, context={}):
      
        delivery_grid_ids = []
        obj_shop = self.pool.get('ecommerce.shop') 
        if(adr_dict['type'] == 'delivery'):
            add_id = adr_dict['address_id']
           
        if(not adr_dict['type'] == 'delivery') and (adr_dict['type'] == 'default'):
            add_id = adr_dict['address_id']

        delivery_carrier = self.pool.get('delivery.carrier')
        delivery_ecommerce_car = obj_shop.browse(cr, uid, [shop_id])
        for i in delivery_ecommerce_car[0].delivery_ids:
            delivery_grid_ids.append(i.id)

        grid_id = self.grid_get(cr, uid, delivery_grid_ids, add_id, {}, from_web=True)       
        get_data = delivery_carrier.read(cr, uid, grid_id, ['name'], context)
        return get_data

    def grid_get(self, cr, uid, ids, contact_id, context={}, from_web=False):
      
        add_grid_list = []
        obj_ecom_prt_add = self.pool.get('res.partner.address')
        if from_web:
            contact = obj_ecom_prt_add.browse(cr, uid, [contact_id])[0]
            obj_deliverycarrier = self.pool.get('delivery.carrier')
            if ids:
                for carrier in obj_deliverycarrier.browse(cr, uid, ids):
                    for grid in carrier.grids_id:
                        get_id = lambda x: x.id
                        country_ids = map(get_id, grid.country_ids)
                        state_ids = map(get_id, grid.state_ids)
                       
                        if country_ids and not contact.country_id.id in country_ids:
                            continue
                        if state_ids and not contact.state_id.id in state_ids:
                            continue
                        if grid.zip_from and (contact.zip or '') < grid.zip_from:
                            continue
                        if grid.zip_to and (contact.zip or '') > grid.zip_to:
                            continue
                        add_grid_list.append(grid.id)
                    
                return add_grid_list
        else:    
            contact = obj_ecom_prt_add.browse(cr, uid, [contact_id])[0]
            for carrier in self.browse(cr, uid, ids):
                for grid in carrier.grids_id:
                    get_id = lambda x: x.id
                    country_ids = map(get_id, grid.country_ids)
                    state_ids = map(get_id, grid.state_ids)
                    if country_ids and not contact.country_id.id in country_ids:
                        continue
                    if state_ids and not contact.state_id.id in state_ids:
                        continue
                    if grid.zip_from and (contact.zip or '') < grid.zip_from:
                        continue
                    if grid.zip_to and (contact.zip or '') > grid.zip_to:
                        continue
                    return grid.id
            return False
  
        
    def delivery_get_price(self, cr, uid, grid_id, product_list, context):
         
        prd_list_ids = []
        total = 0
        weight = 0
        volume = 0
        final_tax_amt = 0
       
        tax_obj = self.pool.get('account.tax')
        for prd_ids in product_list:
            prd_list_ids.append(prd_ids['id']) 
        for prd in product_list:
            p = self.pool.get('product.product').browse(cr, uid, prd['id'])
            sub_total = round(prd['price'] * prd['quantity'])
            if not prd:
                continue
            total += sub_total or 0.0
            weight += (p.product_tmpl_id.weight or 0.0) * prd['quantity']
            volume += (p.product_tmpl_id.volume or 0.0) * prd['quantity']
            if p.taxes_id:
                for tax in tax_obj.compute(cr, uid, p.taxes_id, prd['price'], prd['quantity'], product=prd['id']):
                    final_tax_amt += tax['amount']
        get_ship_price = self.get_price_from_picking_ecommerce(cr, uid, grid_id, total, weight, volume, context)
        
        return dict(get_ship_price=get_ship_price, final_tax_amt=final_tax_amt)  
           

    
    def get_price_from_picking_ecommerce(self, cr, uid, get_id, total, weight, volume, context={}):
        
        grid = self.pool.get('delivery.grid')
        grid_get = grid.browse(cr, uid, int(get_id))
        price = 0.0
        ok = False

        for line in grid_get.line_ids:
            price_dict = {'price': total, 'volume': volume, 'weight': weight, 'wv': volume*weight}
            test = eval(line.type+line.operator+str(line.max_value), price_dict)
            if test:
                if line.price_type == 'variable':
                    price = line.list_price * price_dict[line.variable_factor]
                else:
                    price = line.list_price
                ok = True
                break
        if not ok:
            raise osv.except_osv(_('No price avaible !'),
                                  _('No line matched this order in the choosed delivery grids !'))
        return price   
    
    def ecommerce_sendmail(self, cr, uid, mail_to, subject, body, attachment=None, context = {}):
        try:
            mail_from = 'mansuri.sananaz@gmail.com'
            
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.set_debuglevel(1)
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login('mansuri.sananaz@gmail.com', '123456')
            outer = MIMEMultipart()
            outer['Subject'] = 'Invoice:'
            outer['To'] = mail_to
            outer['From'] = "noreply"
            outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'
          
            msg = MIMEText(body or '',  _charset = 'utf-8')
         
            if(attachment == None):
                
                msg['Subject'] = Header(subject.decode('utf8'), 'utf-8')
                msg['From'] = "noreply"
                s.sendmail(mail_from, mail_to, msg.as_string())
            else:
                msg.set_payload(attachment)
                Encoders.encode_base64(msg)
                msg.add_header('Content-Disposition', 'attachment', filename='invoice.pdf')
               
                outer.attach(msg)
                outer.attach(MIMEText(body))

                composed = outer.as_string()
                s.sendmail(mail_from, mail_to, composed)
            s.close()
        
        except Exception, e:
            logging.getLogger().error(str(e))
        
        return True 
        
ecommerce_partner()

class ecommerce_partner_address(osv.osv):
    _description = "ecommerce partner address"
    _rec_name = "username"
    _name = "ecommerce.partner.address"
    _columns = {
        'username': fields.char('Contact Name', size=128, select=True),
        'partner_id': fields.many2one('ecommerce.partner', 'Partner', ondelete='cascade', select=True),
        'type': fields.selection([('default', 'Default'), ('invoice', 'Invoice'), ('delivery', 'Delivery'),
                                   ('contact', 'Contact'), ('other', 'Other')], 'Address Type'),
        'street': fields.char('Street', size=128),
        'street2': fields.char('Street2', size=128),
        'zip': fields.char('Zip', change_default=True, size=24),
        'city': fields.char('City', size=128),
        'state_id': fields.many2one("res.country.state", 'State', domain="[('country_id', '=', country_id)]"),
        'country_id': fields.many2one('res.country', 'Country'),
        'email': fields.char('E-Mail', size=240),
        'phone': fields.char('Phone', size=64),
        'fax': fields.char('Fax', size=64),
        'mobile': fields.char('Mobile', size=64),
    }

ecommerce_partner_address()

