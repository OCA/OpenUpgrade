import netsvc
import xmlrpclib
import pooler
import wizard

#===============================================================================
#    Payment mapping constants; change them if you need
#===============================================================================

#TODO: makes this a parametrable OpenERP persistent object
payments_mapping = {'checkmo': 'prepaid', 'ccsave': 'prepaid', 'free':'prepaid','googlecheckout':'prepaid','paypayl_express':'prepaid'}
default_payment = 'prepaid'
#other possible OpenERP values would be: 'manual', 'postpaid' and 'picking'
#using 'postpaid' might be interresting for testing purposes

class magento_utils:

    def __init__(self):
	self.logger = netsvc.Logger()

    def createOrders(self, cr, uid, sale_order_array):
        so_nb = 0
        has_error = 0
        self.pool = pooler.get_pool(cr.dbname)

        # order Processing
        for so in sale_order_array:
            has_error += self.createOrder(cr, uid, so) 
            so_nb += 1

        return {'so_nb':so_nb, 'has_error':has_error}

        
    def createOrder(self, cr, uid, so): 
        has_error = 0

        # is there a matching OpenERP partner?
        partner_id = self.pool.get('res.partner').search(cr, uid, [('magento_id', '=', so['customer']['customer_id'])])
        
        # if partner is known, then check the address
        if partner_id:
            known_ba= False
            known_sa= False
            
            # getting all the partner addresses
            adr_ids=self.pool.get('res.partner.address').search(cr, uid, [('partner_id', '=', partner_id[0])])
            
            # checks for bill an ship address
            for adr_id in adr_ids:
                # iterates over the addresses
                address=self.pool.get('res.partner.address').browse(cr, uid, adr_id)
                # Does the address exist?
                if ((address.name == so['billing_address']['firstname']+" "+so['billing_address']['lastname']) and 
                    (address.street == so['billing_address']['street']) and 
                    (address.street2 == so['billing_address']['street2']) and 
                    (address.city == so['billing_address']['city']) and 
                    (address.zip == so['billing_address']['postcode']) and 
                    (address.phone == so['billing_address']['phone'])):
                
                    known_ba= True
                    bill_adr_id = address.id
                    
                if ((address.name == so['shipping_address']['firstname']+" "+so['shipping_address']['lastname']) and 
                    (address.street == so['shipping_address']['street']) and 
                    (address.street2 == so['shipping_address']['street2']) and 
                    (address.city == so['shipping_address']['city']) and 
                    (address.zip == so['shipping_address']['postcode']) and 
                    (address.phone == so['shipping_address']['phone'])):
                    
                    known_sa= True
                    ship_adr_id = address.id
        
        # unknown business partner -> create a new one 
        else:
            partner_id = self.pool.get('res.partner').create(cr, uid, {
                'name': so['customer']['customer_name'],
                'magento_id': so['customer']['customer_id'],
            })
            
            known_ba= False
            known_sa= False
            
            
        if(type(partner_id)== list):
            fixed_partner_id = partner_id[0]
        else:
            fixed_partner_id = partner_id
                    
        # if address doesn't exist, create it
        if(known_ba == False):
            bill_adr_id = self.pool.get('res.partner.address').create(cr, uid, {
            'partner_id': fixed_partner_id,
            'name': so['billing_address']['firstname']+" "+so['billing_address']['lastname'],
            'street': so['billing_address']['street'],
            'street2': so['billing_address']['street2'],
            'city': so['billing_address']['city'],
            'zip': so['billing_address']['postcode'],
            'phone': so['billing_address']['phone'],
            })
            
        # if the address doesn't exist & isn't the same as billing, create it
        if((so['shipping_address'] == so['billing_address']) and known_sa == False):
            ship_adr_id = self.pool.get('res.partner.address').create(cr, uid, {
                'partner_id': fixed_partner_id,
                'name': so['shipping_address']['firstname']+" "+so['shipping_address']['lastname'],
                'street': so['shipping_address']['street'],
                'street2': so['shipping_address']['street2'],
                'city': so['shipping_address']['city'],
                'zip': so['shipping_address']['postcode'],
                'phone': so['shipping_address']['phone'],
            })
        # if billing & shipping are the same, retrieve id
        else:
            ship_adr_id = bill_adr_id
                
        # retrieves Magento Shop in OpenERP
        shop_id=self.pool.get('sale.shop').search(cr, uid, [('magento_id', '>', 0)])
        if shop_id and len(shop_id) >= 1:
            shop=self.pool.get('sale.shop').browse(cr, uid, shop_id[0])
        else:
            raise wizard.except_wizard(_('UserError'), _('You must have one shop with magento_id set to 1'))
            
        # creates Sale Order
        order_id=self.pool.get('sale.order').create(cr, uid, {
                'name': _('magento SO/')+str(so['id']),
                'partner_id': fixed_partner_id,
                'partner_shipping_id': ship_adr_id,
                'partner_invoice_id': bill_adr_id,
                'partner_order_id': bill_adr_id,
                'shop_id' : shop.id or 1, #Deal with Shop!!
                'pricelist_id' : shop.pricelist_id.id or 1, #Deal with PriceList!!
                'magento_id' : so['id'],
                'has_error' : 0,
                'order_policy' : payments_mapping[so['payment']] or default_payment 
            })
        
        #===============================================================================
        # Sale order lines
        #-If the product exist : create line
        #-Else : report error on sale order            
        #===============================================================================
        line_error = False
        
        for line in so['lines']:
            # is the Magento id known?
            product=self.pool.get('product.product').search(cr, uid, [('magento_id', '=', line["product_magento_id"])])
            if product: # then save the line
                get_product=self.pool.get('product.product').browse(cr, uid, product[0])
                self.pool.get('sale.order.line').create(cr, uid, {
                        'product_id': product[0], #line['product_sku'][3:],
                        'name': line['product_name'],
                        'order_id': order_id,
                        'product_uom': get_product.uom_id.id,
                        'product_uom_qty': line['product_qty'],
                        'price_unit': line['product_price'],
                        'discount' : float(100*float(line['product_discount_amount']))/(float(line['product_price'])*float(line['product_qty'])),
                        'tax_id' : [(6, 0, [x.id for x in get_product.taxes_id])] #See fields.py, many2many set method.
                })
                
            # report the error
            else:
                self.logger.notifyChannel(_("Magento Import"), netsvc.LOG_ERROR, _("Sale Order %s : Cannot find product with id : %s sku : %s name %s") % (order_id , line['product_magento_id'], line['product_sku'], line['product_name']))
                self.pool.get('sale.order').write(cr, uid, order_id, {'has_error' : 1})
                line_error = True
           
        # shipping line
        ship_product_id=self.pool.get('product.product').search(cr, uid, [('default_code', '=', 'SHIP')])
        ship_product=self.pool.get('product.product').browse(cr, uid, ship_product_id[0])

        self.pool.get('sale.order.line').create(cr, uid, {
                'product_id': ship_product_id[0],
                'name': ship_product.name,
                'order_id': order_id,
                'product_uom': ship_product.uom_id.id,
                'product_uom_qty': 1,
                'price_unit': so['shipping_amount'],
        })
        
        # done fields counter
        if line_error :
            has_error = 1
        
        return has_error

magento_utils()
