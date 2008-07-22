#!/usr/bin/python
# -*- coding: utf8
import csv


#TODO: 
##genere chart with parents :( => create a root with code = 0 then create the tree structure
##change it in order to run it server side
##remove close_method when mra's work is pushed

account_map = {
#	'id': lambda x: 'account_'+x['AID,A,10'], # will have to be uncomment for server side import
	'id': lambda z:'',
	'code': lambda x: x['AID,A,10'],
	'name': lambda x: x['HEADING1,A,40'],
	'note': lambda x: x['AMEMO,M,11'], 
	'type': lambda x: {
		'LIABILIT': 'cash',
		'ASSETS': 'asset',
		'FXASSETS': 'asset',
		'INCOME': 'income',
		'DISCINC': 'income',
		'EXPENSE': 'expense',
		'DISCEXP': 'expense',
		'': 'view',
		'UNDEF': 'view',
	}[x['ABALANCE,A,10']],
	'sign': lambda x: 1, 
#	'company_id': lambda x: "Tiny sprl", #will be replaced by id of main company
	'parent_id:id': lambda a: ''#'account_bob_import.account_bob_0'
	#'close_method': lambda x: 'balance', #will be removed
}


#this dict is used to know the header of each column
account_headers = {
	'id':'id', 
	'code':'code', #'Code', 
	'name':'name',# 'Name', 
	'note': 'note',#'Note', 
	'type': 'type',#'Account Type',
	'sign': 'sign', #'Sign',
#	'company_id': 'Company',
	'parent_id:id':'parent_id:id'
	#'close_method': 'Deferral Method',
	}
def convert2utf(row):
	if row:
		retRow = {}
		for k,v in row.items():
			retRow[k] = v.decode('latin1').encode('utf8').strip()
		return retRow
	return row
def convert(reader, writer, mapping, column_headers):
	record = {}
	for key, column_name in column_headers.items():
		record[key] = column_name
	writer.writerow(record)
	temp_dict = {}
	list_ids = []
	for row in reader:
		record = {}
		for key,fnct in mapping.items():
			record[key] = fnct(convert2utf(row))
		temp_dict[record['code']]=record
		list_ids.append(record['code'])
		record['id'] = 'id' + record['code']
		#if len(record['code'])>1:
			#l = len(record['code'])
			#aa = range(l+1)
			#aa.reverse()#[0,1,2,3,4,5]
			#aa.pop()
			#for i in aa:
				#if record['code'][0:i-1] in list_ids:
					#record['parent_id:id'] = 'id' + str(record['code'][0:i-1])
					#break
		#else:
			#record['parent_id:id'] = 'account_bob_import.account_bob_0'
		#writer.writerow(record)
	temp_keys = map(lambda x: int(x),temp_dict.keys())
	temp_keys.sort()
	temp_str_keys = map(lambda x: str(x),temp_keys)
	for t in temp_str_keys:
		if len(t)>1:
			l = len(temp_dict[t]['code'])
			aa = range(l+1)
			aa.reverse()
			aa.pop()
			for i in aa:
				if temp_dict[t]['code'][0:i-1] in list_ids:
					temp_dict[t]['parent_id:id'] = 'id' + str(temp_dict[t]['code'][0:i-1])
					break
		else:
			temp_dict[t]['parent_id:id'] = 'account_bob_import.account_bob_0'
		writer.writerow(temp_dict[t])
	return True

reader = csv.DictReader(file('accounts.csv','rb'))
writer = csv.DictWriter(file('account_bob/account.account.csv', 'wb'), account_map.keys())
convert(reader, writer, account_map, account_headers)

move_map = {
	'id': lambda x: 'move_'+x['MID,A,40'],
	'account_id:id': lambda x: 'account_'+x['AID']
}

#TODO:
#	Minimal Account Chart & Properties: Demo Only
#	Create Objects:
#		account.account.template
#			idem a account.account + champ selection property
#		account.tax.template
#		account.journal.template
#	Wizard:
#		Prend un template -> genere un vrai plan
#			- Societe -
#			- Template -
#		Cree properties
#	Changer l10n_be et l10n_fr, l10n_ch

#~ Problemes:
	#~ Minimal Account Chart : Demo Only
	#~ Creer une nouvelle societe (nvx plan de compte)
		#~ -> dupliquer un plan de compte si meme pays
		#~ -> si pas meme pays: installer l10n_XXX


#~ if __name__=='__main__':
	#~ pass
