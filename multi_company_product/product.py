from osv import osv,fields
from tools import config
from tools.translate import _

class product_supplierinfo(osv.osv):
    _name='product.supplierinfo'
    _inherit='product.supplierinfo'
    
    _columns={
             'company_id':fields.many2one('res.company','Company')
             }
product_supplierinfo()

class product_template(osv.osv):
    _name = "product.template"
    _inherit="product.template"
    
    def _calc_standard_price(self, cr, uid, ids, name, arg, context=None):
        res = {}
        print 'ids--------------------',ids
        print 'uid-----------------',uid
        company=self.pool.get('res.users').read(cr,uid,uid,['company_id'])['company_id']
        print 'company---------------',company
        company_cost_obj=self.pool.get('company.wise.cost.price')
        for product in self.browse(cr, uid, ids, context=context):
            company_cost_ids=company_cost_obj.search(cr,uid,[('company_id','=',company[0]),('product_id','=',product.id)])
            if company_cost_ids:
                company_cost_data=company_cost_obj.read(cr,uid,company_cost_ids,['standard_price'])
                print 'company_cost_data-----------------',company_cost_data
    #            res[product.standard_price]=company_cost_data['standard_price']
                res[product.id]=company_cost_data[0]['standard_price']
            else:
                res[product.id]=1.0
                raise osv.except_osv(_('Error !'),
                        _('There is no cost price defined for this company "%s" ') % \
                                (company[1]))
            
        return dict([(i, res[i]) for i in ids ])
    
    def _calc_list_price(self, cr, uid, ids, name, arg, context=None):
        res = {}
        print 'ids--------------------',ids
        print 'uid-----------------',uid
        company=self.pool.get('res.users').read(cr,uid,uid,['company_id'])['company_id']
        print 'company---------------',company
        company_cost_obj=self.pool.get('company.wise.sale.price')
        for product in self.browse(cr, uid, ids, context=context):
            company_list_ids=company_cost_obj.search(cr,uid,[('company_id','=',company[0]),('product_id','=',product.id)])
            if company_list_ids:
                company_list_data=company_cost_obj.read(cr,uid,company_list_ids,['list_price'])
                print 'company_cost_data-----------------',company_list_data
    #            res[product.standard_price]=company_cost_data['standard_price']
                res[product.id]=company_list_data[0]['list_price']
            else:
                res[product.id]=1.0
                
        return dict([(i, res[i]) for i in ids ])
    
#        for id in ids:
#            res.setdefault(id, 0.0)
#        for product in self.browse(cr, uid, ids, context=context):
#                res[product.id] = product.list_price
#            res[product.id] =  (res[product.id] or 0.0) * product.price_margin + product.price_extra
        return res
    
    _columns={
              'list_price': fields.function(_calc_list_price, method=True, type='float', string='Sale Price', help="Base price for computing the customer price. Sometimes called the catalog price."),
              'standard_price': fields.function(_calc_standard_price, method=True, type='float', string='Cost Price', required=True, help="The cost of the product for accounting stock valuation. It can serves as a base price for supplier price."),
              'standard_price_ids' :fields.one2many('company.wise.cost.price','product_id'),
              'list_price_ids' :fields.one2many('company.wise.sale.price','product_id')
              }
    def create(self,cr,uid,vals,context={}):
        
        standard_ids=vals['standard_price_ids']
        if not standard_ids:
            company=self.pool.get('res.users').read(cr,uid,uid,['company_id'])['company_id']
            raise osv.except_osv(_('Error !'),
                        _('There is no cost price defined for this company "%s" ') % \
                                (company[1]))
        cr_id=super(osv.osv,self).create(cr,uid,vals,context=context)
        return cr_id
    
product_template()

class company_wise_cost_price(osv.osv):
    _name="company.wise.cost.price"
    _description="Company Wise Cost Price"
    _columns={
              'product_id':fields.many2one('product.template','Product Id'),
              'company_id':fields.many2one('res.company','Company'),
              'standard_price':fields.float('Cost Price', required=True, digits=(16, int(config['price_accuracy'])), help="The cost of the product for accounting stock valuation. It can serves as a base price for supplier price."),
              'currency_id':fields.many2one('res.currency','Currency',readonly=True)
              }
    def company_cost_onchange(self,cr,uid,ids,company_id):
        if company_id:
            currency=self.pool.get('res.company').read(cr,uid,company_id,['currency_id'])
            return {'value':{'currency_id':currency['currency_id'][0]}}
        else:
            return{'value':{'currency_id':False}}
            
    def create(self,cr,uid,values,context={}):
        #code to make onchange_currency_id effectiv for readonly fields
        if values and values.has_key('company_id') and values['company_id']:
            val = self.company_cost_onchange(cr, uid, [] ,values['company_id'])['value']
            values['currency_id']=val['currency_id']
            
        return super(company_wise_cost_price, self).create(cr, uid, values, context=context)
    
    def write(self,cr,uid,ids,values,context={}):
         #code to make onchange_currency_id effectiv for readonly fields
        if values and  values.has_key('company_id') and values['company_id']:
            company_id = values['company_id']
        # this code effects when currency_id is not changed still the rate are chnged then 
        #
        
        val = self.company_cost_onchange(cr, uid, ids ,company_id)['value']
        values['currency_id']=val['currency_id']
        
        return super(company_wise_cost_price, self).write(cr, uid, ids, values, context=context)
    

        
company_wise_cost_price()

class company_wise_sale_price(osv.osv):
    _name="company.wise.sale.price"
    _description="Company Wise Sale Price"
    _columns={
              'product_id':fields.many2one('product.template','Product Id'),
              'company_id':fields.many2one('res.company','Company'),
              'list_price':fields.float('Sale Price', required=True, digits=(16, int(config['price_accuracy'])), help="Base price for computing the customer price. Sometimes called the catalog price."),
              'currency_id':fields.many2one('res.currency','Currency',readonly=True)
              }
    
    def company_sale_onchange(self,cr,uid,ids,company_id):
        if company_id:
            currency=self.pool.get('res.company').read(cr,uid,company_id,['currency_id'])
            return {'value':{'currency_id':currency['currency_id'][0]}}
        else:
            return{'value':{'currency_id':False}}
            
    def create(self,cr,uid,values,context={}):
        #code to make onchange_currency_id effectiv for readonly fields
        if values and values.has_key('company_id') and values['company_id']:
            val = self.company_sale_onchange(cr, uid, [] ,values['company_id'])['value']
            values['currency_id']=val['currency_id']
            
        return super(company_wise_sale_price, self).create(cr, uid, values, context=context)
    
    def write(self,cr,uid,ids,values,context={}):
         #code to make onchange_currency_id effectiv for readonly fields
        if values and  values.has_key('company_id') and values['company_id']:
            company_id = values['company_id']
        # this code effects when currency_id is not changed still the rate are chnged then 
        #
        
        val = self.company_sale_onchange(cr, uid, ids ,company_id)['value']
        values['currency_id']=val['currency_id']
        
        return super(company_wise_sale_price, self).write(cr, uid, ids, values, context=context)
company_wise_sale_price()