#!/usr/bin/python

import psycopg
import csv

db_old = "new_huissier"

def import_sql(cr, fname, query, fields=None, trigger=None):
	cr.execute(query)
	if not fields:
		fields = map(lambda x: x[0], cr.description)
	fp = file(fname,'wb')
	result = cr.fetchall()
	if trigger:
		result = map(lambda x: tuple(trigger(cr, list(x))), result)
	writer = csv.writer(fp)
	writer.writerow(fields)
	writer.writerows(result)
	fp.close()


db = psycopg.connect("dbname="+db_old)
cr = db.cursor()

def _account_trigger(cr, x):
	x = list(x)
	if x[5] not in ('receivable','payable','view','income','expense','tax','cash','asset','equity','closed'):
		x[5] = {'stock_inventory':'asset','stock_income':'income','stock_expense':'expense'}.get(x[5], 'asset')
	return tuple(x)

import_sql(cr,
	'account.account.csv',
	"select 'account' || id as id, code, name, 'EUR' as currency_id, True as active, type from account_account",
	trigger = _account_trigger
)

import_sql(cr,
	'account.tax.csv',
	"""select
			'tax' || id as id,
			domain,
			name,
			'account'||account_collected_id as "account_collected_id:id",
			'account'||account_paid_id as "account_paid_id:id",
			amount,
			child_depend,
			type
		from
			account_tax
	"""
)


#auction.lot.category

import_sql(cr,
	'auction.lot.category.csv',
	"""
	select
		'cat'||id as "id",
		name,
		active
	from
		auction_lot_category
	order by
		id
	"""
)
#auction.dates.csv

import_sql(cr,
	'auction.dates.csv',
	"""
	select
	
		'date'||id as "id",
		'Auction'||id as "name",
		expo1,
		expo2,
		'account'||acc_expense as "acc_expense:id",
		'account'||acc_income as "acc_income:id",
		state,
		auction1,
		auction2,
		'account.expenses_journal' as "journal_seller_id:id",
		'account.sales_journal' as "journal_id:id",
		'auction_db.aaa_un' as "account_analytic_id:id"
		
	from
		auction_dates
	order by
		id
	"""
)


# auction.deposit.csv

import_sql(cr,
	'auction.diposit.csv',
	"""
	select
		'deposit'||id as "id",
		name,
		date_dep,
		partner_id as "partner_id:id",
		method,
		'tax'||tax_id as "tax_id:id",
		total_neg
		
	from
		auction_deposit
	order by
		id
	"""
)
#lot
import_sql(cr,
	'auction.lots.csv',
	"""
	select
		'lot'||id as id,		
		auction_id as "auction_id:id",
		bord_vnd_id as "bord_vnd_id:id",
		name,
		name2,
		lot_type,
		author_right,
		lot_est1,
		lot_est1,
		lot_local,
		artist_id,
		artist2_id,
		important,
		obj_desc,
		obj_num,
		obj_ret,
		obj_comm,
		obj_price,
		ach_avance,
		ach_login,
		ach_uid as "ach_uid:id",
		ach_emp,
		ach_inv_id as "ach_inv_id:id",
		buy_inv_id as "sel_inv_id:id",
		vnd_lim,
		vnd_lim_net,
		state,	
		'auction_db.product_unknown' as "product_id:id"	
	from
		auction_lots
	order by
		id
	"""
)



def _deposit(cr, rec):
	if not rec[3]:
		rec[3] = '6025'
	return rec




# 'invoice'||invoice_id as "invoice_id:id",
import_sql(cr,
	'account.invoice.csv',
	"""
	select
		'invoice'||id as "id",
		comment,
		date_due,
		number,
		'base.main_company' as "company_id:id",
		address_invoice_id as "address_invoice_id:id",
		partner_id as "partner_id:id",
		state,
		type,
		'account'||account_id as "account_id:id",
		date_invoice,
		name,
		address_contact_id as "address_contact_id:id"
	from
		account_invoice
	order by
		id
	"""
)

import_sql(cr,
	'account.invoice.line.csv',
	"""
	select
		name,
		'invoice'||invoice_id as "invoice_id:id",
		price_unit,
		'account'||account_id as "account_id:id",
		quantity
	from
		account_invoice_line
	order by
		id
	"""
)

#auction.bid.csv

import_sql(cr,
	'auction.bid.csv',
	"""
	select
		'bid'||id as "id",
		auction_id as "auction_id:id",
		partner_id as "partner_id:id",
		name,
		contact_tel 
	from
		auction_bid
	order by
		id
	"""
)


#auction.bid_line.csv
import_sql(cr,
	'auction.bid_line.csv.csv',
	"""
	select 
		name,
		'bid'||bid_id as "bid_id:id",
		'lot'||lot_id as "lot_id:id",
		price,
		call
		
	from
		auction_bid_line
	order by
		id
	"""
)






cr.close()
