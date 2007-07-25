from osv import osv, fields
import time

class lunch_category(osv.osv):
##	_name='lunch.category'
##	_columns = {
##	  'name': fields.char('name', size=50, required=true),
##	  'category_id': fields.one2many('lunch.product', 'category', required=true, ondelete='cascade'),
	_name = 'lunch.category'
	_description = "category"
	_columns = {
	'name': fields.char('name', required=True, size=50),
	'category':fields.char('sequence',required=True, size=10),
		}
	_order = 'name'
lunch_category()

##				
##class name_category(osv.osv):
##	_name = 'lunch.category.name'
##	_columns = {
##		'name': fields.char('title', required=true, size=46, translate=true),
##		
##	}
##name_category()

def _category_name_get(self, cr, uid, context={}):
	
	obj = self.pool.get('lunch.category')
	cat_ids= obj.search(cr,uid,[])
   #	print name
	res = obj.read(cr,uid,cat_ids,['name'])
	return [(r['category'],r['name']) for r in res]+ [(0,'')]
 
##	res = obj.read(cr, uid, ['name'])
##	return [(r['name']) for r in res]
##
##	for i in self.browse(cr,uid,id):
##		res = obj.read(cr, uid,['i.name'], context)
##	return ([r['i.name'] for i in res])
##	
   
class lunch_product(osv.osv):
	_name='lunch.product'	
	_columns = {
		'name': fields.char('name', size=50, required=True),
		'category_id': fields.selection(_category_name_get, 'category', size=32),
		'description': fields.char('description', size=40, required=False),
		'price': fields.float('price'),
		}
lunch_product()



class lunch_cashbox(osv.osv):
	def amount_available(self, cr, uid, ids, field_name, arg, context):
		cr.execute("select box,sum(amount) from lunch_cashmove where active = 't' group by box")
		r = dict(cr.fetchall())
		for i in ids :
			r.setdefault(i,0)
		return r
  
##
##				res={}
##				print ids
##				for box in self.browse(cr,uid,ids):
##					print box.id
##					res[box.id]= 0
##					for move in box.moves:
##						res[box.id]+=move.amount
##				return res
##				
##				for i in res.fecthall():
###parcourir la table pr mettre a jour le champ sum_remain
##				   if user_cashbox==res[0]:
##						
##					   sum_remain+= res[1] + amount
##					
##			  
##	  return res
			   
	_name='lunch.cashbox'
	_columns={
		'manager':fields.many2one('res.users','manager'),
		'name':fields.char('name',size=30,required=True, unique = True),
		'sum_remain': fields.function(amount_available, method=True, string='remained total'),
		'moves': fields.one2many('lunch.cashmove','box','moves'),
		}
lunch_cashbox()




class lunch_cashmove(osv.osv):
	_name= 'lunch.cashmove'
		
	_columns={
		'name': fields.char('name',size=128),
		'user_cashmove': fields.many2one('res.users','user name', required=True),
		'amount': fields.float('amount'),
		#'manager':fields.many2one('lunch.manager','box name',size=30),
		'box':fields.many2one('lunch.cashbox','box name',size=30,required=True),
		'active':fields.boolean('active'),
		}
	_defaults={
	'active': lambda *a: True,
		}
#calcul de l argent depose pr un utilisateur
lunch_cashmove()

class lunch_order(osv.osv):
	
	_name='lunch.order'
	_rec_name= "user_id"
	
	def _price_get(self, cr, uid, ids, *a):
		res={}
		prods=self.browse(cr,uid,ids)
		for prod in prods:
			res[prod.id]= prod.product.price
		return res 
		

	_columns={
		'user_id': fields.many2one('res.users','user name', required=True,readonly=True,states={'draft':[('readonly',False)]}),
		'product':fields.many2one('lunch.product','product', change_default=True,required=True,relate=True,states={'draft':[('readonly',False)]}),
		'date': fields.date('date',required=True, readonly=True,states={'draft':[('readonly',False)]}),
		'cashmove':fields.many2one('lunch.cashmove', 'cashmove' , readonly=True  ),
		'price': fields.function(_price_get, method=True, string='price'),
		'descript':fields.char('description order', readonly=True, size=50,states={'draft':[('readonly',False)]}),
		'state': fields.selection([
						('draft','draft'),
			('confirmed','confirmed'),
						],'state', readonly=True, select=True),

		}
	
	_defaults={

		'user_id': lambda self,cr,uid,context: uid,
		'date': lambda self,cr,uid,context: time.strftime('%y-%m-%d'),
		'state': lambda self,cr,uid,context: 'draft',
		}

	
	def onchange_product(self, cr, uid, ids, product):
		if not product:
			return  {'value': {'price': 0}}
		prod = self.pool.get('lunch.product').browse(cr, uid, product)
		return {'value': {'price': prod.price}}

	def confirm(self,cr,uid,ids,box,context):
		cashmove_ref= self.pool.get('lunch.cashmove')
		for order in self.browse(cr,uid,ids):
			if order.state == 'confirmed':
				continue
			new_id= cashmove_ref.create(cr,uid,{'name': order.product.name+' order',
							'amount':-order.product.price,
							'user_cashmove':order.user_id.id,
							'box':box,
							'active':True,
							})
			self.write(cr,uid,[order.id],{'cashmove':new_id, 'state':'confirmed'})
		return {}

	def lunch_order_cancel(self,cr,uid,ids,context):

		orders= self.browse(cr,uid,ids)
		for order in orders:
			if not order.cashmove: continue
			self.pool.get('lunch.cashmove').unlink(cr, uid, [order.cashmove.id])
		self.write(cr,uid,ids,{'state':'draft'})
		return {}
	
		
lunch_order()


class report_lunch_amount(osv.osv):
	
	_name='report.lunch.amount'
	_description = "Amount available by user and box"
	_auto = False
	_rec_name= "user"
	_columns = {
		'user_id': fields.many2one('res.users','User Name',readonly=True),
		'amount': fields.float('Amount', readonly=True),
		'box':fields.many2one('lunch.cashbox','Box Name',size=30,readonly=True),
		}


	
	def init(self, cr):
		cr.execute("""
			create or replace view report_lunch_amount as (
				select
									min(lc.id) as id,
									lc.user_cashmove as user_id,
									sum(amount) as amount,
									lc.box as box
				from
									lunch_cashmove lc
								where
									active = 't'
				group by lc.user_cashmove, lc.box
				)""")


report_lunch_amount()

