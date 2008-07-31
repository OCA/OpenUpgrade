#!/usr/bin/python
# -*- encoding: utf-8 -*-
import csv
import datetime
import time
from datetime import date, timedelta

def convert2utf(row):
    if row:
        retRow = {}
        for k,v in row.items():
            retRow[k] = v.decode('latin1').encode('utf8').strip()
        return retRow
    return row

def get_first_day(dt, d_years=0, d_months=0):
    # d_years, d_months are "deltas" to apply to dt
    y, m = dt.year + d_years, dt.month + d_months
    a, m = divmod(m-1, 12)
    return date(y+a, m+1, 1)

def get_last_day(dt):
    return get_first_day(dt, 0, 1) + timedelta(-1)

def mkDateTime(dateString,strFormat="%Y-%m-%d"):
    # Expects "YYYY-MM-DD" string
    # returns a datetime object
    eSeconds = time.mktime(time.strptime(dateString,strFormat))
    return datetime.datetime.fromtimestamp(eSeconds)

def construct_vat_dict(reader_vat, vat_dict):
    count = 0
    for row in reader_vat:
        #fill the first line with False
        if count != "0":
            if row['VIMPINV,A,10']:
                vat_dict[row['VSTORED,A,15']] = 'account_'+row['VIMPINV,A,10']
            else:
                vat_dict[row['VSTORED,A,15']] = False
        else:
            vat_dict[''] = False
        count += 1
    return vat_dict


#tax_code_map = {
#    'id': lambda x: x['VSTORED,A,15'],
##    'name': #should be filled with sequence number,
#    'journal_id:id': lambda x: 'journal_'+x['HDBK,A,4'],
#    'state': lambda x: 'draft',
#    'period_id:id': lambda x: 'period_'+x['HFYEAR,A,5']+"-"+x['HMONTH,I,4'],
#    'ref': lambda x: '',
#}




#======================= Importing Chart of Accounts =======================

##genere chart with parents :( => create a root with code = 0 then create the tree structure
account_map = {
   'id': lambda x: 'account_'+x['AID,A,10'], # will have to be uncomment for server side import
#    'id': lambda z:'',
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
#   'company_id': lambda x: "Tiny sprl", #will be replaced by id of main company
    'parent_id:id': lambda a: ''#'account_bob_import.account_bob_0'
    #'close_method': lambda x: 'balance', #will be removed
}

def import_account(reader, writer, mapping):
    record = {}
    for key, column_name in mapping.items():
        record[key] = key
    writer.writerow(record)
    temp_dict = {}
    list_ids = []
    for row in reader:
        record = {}
        for key,fnct in mapping.items():
            record[key] = fnct(convert2utf(row))
        temp_dict[record['code']]=record
        list_ids.append(record['code'])
        #record['id'] = 'id' + record['code']

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
                    temp_dict[t]['parent_id:id'] = 'account_' + str(temp_dict[t]['code'][0:i-1])
                    break
        else:
            temp_dict[t]['parent_id:id'] = 'account_bob_import.account_bob_0'
        writer.writerow(temp_dict[t])
    return True

print 'importing chart of accounts'
reader_account = csv.DictReader(file('original_csv/accounts.csv','rb'))
writer_account = csv.DictWriter(file('account.account.csv', 'wb'), account_map.keys())
import_account(reader_account, writer_account, account_map)




#======================= Importing Financial Journals =======================

journals_map = {
    'id' : lambda x: 'journal_'+x['DBID,A,4'],
    'code': lambda x: x['DBID,A,4'],
    'name': lambda x: x['HEADING1,A,30'],
    'view_id:id': lambda x: 'account.account_journal_view', # journal view for all except the ones that are of type cash => cash journal view
    'currency:id': lambda x: x['DBCURRENCY,A,3'],#to be check
    'sequence_id:id': lambda x: 'account.sequence_journal', #entry journal for all
    'type': lambda x: {
        'PUR': 'purchase',
        'PUC': 'purchase',
        'SAL': 'sale',
        'SAC': 'sale',
        'CAS': 'cash',
        'ISB': 'general',#default
        'PRI': 'general',#default
        'ISD': 'general',#default
        'ICO': 'general',#default
        'ISO': 'general',#default
        'PRO': 'general',#default
        'COP': 'general',#default
        'ISI': 'general',#default
        'ISM': 'general',#default
        'IDN': 'general',#default
        'ICE': 'general',#default
        '':'general'
        #else should be of 'general' type

    }[x['DBTYPE,A,3']],
    'default_debit_account_id:id':lambda x: x['DBACCOUNT,A,10'], #filled with the id of the account_account with code = x['DBACCOUNT,A,10'],
    'default_credit_account_id:id':lambda x: x['DBACCOUNT,A,10'] ,#filled with the id of the account_account with code =
}

def import_journal(reader_journal, writer_journal, journals_map):
    record = {}
    for key, column_name in journals_map.items():
        record[key] = key
    writer_journal.writerow(record)
    for row in reader_journal:
        record = {}
        for key,fnct in journals_map.items():
            record[key] = fnct(convert2utf(row))
        if record['default_debit_account_id:id']:
            record['default_debit_account_id:id'] = 'account_' + str(record['default_debit_account_id:id'])
        if record['default_credit_account_id:id']:
            record['default_credit_account_id:id'] = 'account_' + str(record['default_credit_account_id:id'])
        if record['type']=='cash':
            record['view_id:id']='account.account_journal_bank_view'
        cur = ''
        if record['currency:id']:
            cur = 'base.' + record['currency:id'].upper()
        record['currency:id'] = cur
        writer_journal.writerow(record)
    return True

print 'importing financial journals'
reader_journal = csv.DictReader(file('original_csv/journals.csv','rb'))
writer_journal = csv.DictWriter(file('account.journal.csv', 'wb'), journals_map.keys())
import_journal(reader_journal, writer_journal, journals_map)




#======================= Importing Partners Data =======================

def _get_cat(record):
#have to put the partner into category suppliers if CSUPTYPE,A,1 == 'S'
#have to put the partner into category customers if CCUSTYPE,A,1 == 'C'
    res=[]
    if 'CSUPTYPE,A,1' in record and record['CSUPTYPE,A,1'].upper() in ['S'] :
        res.append('base.res_partner_category_8')
    if 'CCUSTYPE,A,1' in record and record['CCUSTYPE,A,1'].upper() in ['C']:
        res.append('base.res_partner_category_0')
    return ','.join(res)

partners_map = {
    'id':lambda x: 'partner_'+x['CID,A,10'],
    'ref': lambda x: x['CID,A,10'],
    'name': lambda x: x['CNAME1,A,40'],
    'lang': lambda x: {
        #/!\ if a lang isn't installed, the value should be filled with ''

        'E': 'en_US', #'E' for English
        'D': 'de_DE',#'de_DE',#?? #'D' for German....de_DE
        'F': 'fr_FR',#'fr_FR',#??#'F' for French..fr_FR
        'N': 'nl_NL',#'nl_NL',#??#'N' for Dutch....nl_NL
        'A': '',#no lang
        '' : ''
    }[x['CLANGUAGE,A,2']],
    'vat': lambda x: x['CVATNO,A,12'],
    'website': lambda x: x['HTTPADDRESS,A,60'],
    'comment': lambda x: x['CMEMO,M,11'],
    'domiciliation_bool': lambda x : x['CBANKORDERPAY,L,1'],
    'domiciliation': lambda x : x['CBANKORDERPAYNO,A,15'],
    'category_id:id':lambda x:_get_cat(x),
}

#have to create one res.partner.adress for this partner with this
partner_add_map = {
    'city' : lambda x: x['CLOCALITY,A,40'],
    'fax': lambda x: x['CFAXNO,A,25'],
    'zip' :  lambda x: x['CZIPCODE,A,10'],
    'country_id:id':lambda x: x['CCOUNTRY,A,6'], #filled with id of res.country that have code == x['CCOUNTRY,A,6']
    'phone' : lambda x: x['CTELNO,A,25'],
    'street' : lambda x: x['CADDRESS1,A,40'],
    'type' : lambda x: 'default',
    'partner_id:id':lambda x: x['CID,A,10'],
}

#have to create res.partner.bank if x['CBANKNO,A,20'] <> False
partner_bank_map = {
    'state': lambda x:'bank',#should be filled with id of res.Partner.bank.type that have name == 'Bank Account'
    'acc_number': lambda x: x['CBANKNO,A,20'],
    'partner_id:id':lambda x:''
}


def import_partner(reader_partner, writer_partner, partners_map, writer_address, partner_add_map, writer_bank, partner_bank_map):
    record = {}
    record_address = {}
    record_bank = {}
    list_partners = []

    for key, column_name in partners_map.items():
        record[key] = key
    for key, column_name in partner_add_map.items():
        record_address[key] = key
    for key, column_name in partner_bank_map.items():
        record_bank[key] = key

    writer_partner.writerow(record)
    writer_address.writerow(record_address)
    writer_bank.writerow(record_bank)
    for row in reader_partner:
        record = {}
        record_address = {}
        record_bank = {}
        for key,fnct in partners_map.items():
            record[key] = fnct(convert2utf(row))
        for key,fnct in partner_add_map.items():
            record_address[key] = fnct(convert2utf(row))
        partner_name = record['name']
        if partner_name.find('.')!=-1:
            partner_name = partner_name.replace('.','')
        record['id'] = partner_name

        if row.has_key('CBANKNO,A,20') and row['CBANKNO,A,20']:
            for key,fnct in partner_bank_map.items():
                record_bank[key] = fnct(convert2utf(row))
            record_bank['partner_id:id'] = partner_name
            writer_bank.writerow(record_bank)
        address = ''
        if record_address['country_id:id']:
                address = 'base.'+record_address['country_id:id'].lower()

        if not record['domiciliation_bool']=='1':
            record['domiciliation_bool'] = ''

        if record['name'] in list_partners:
            record_address['type'] = 'other'
            record_address['partner_id:id'] = partner_name
            record_address['country_id:id'] = address
            writer_address.writerow(record_address)
        else:
            list_partners.append(record['name'])
            record_address['partner_id:id'] = partner_name
            record_address['country_id:id'] = address
            writer_partner.writerow(record)
            writer_address.writerow(record_address)
    return True

print 'importing partners'
reader_partner = csv.DictReader(file('original_csv/partners.csv','rb'))
writer_partner = csv.DictWriter(file('res.partner.csv', 'wb'), partners_map.keys())
writer_address = csv.DictWriter(file('res.partner.address.csv','wb'), partner_add_map.keys())
writer_bank = csv.DictWriter(file('res.partner.bank.csv','wb'), partner_bank_map.keys())
import_partner(reader_partner, writer_partner, partners_map, writer_address, partner_add_map, writer_bank, partner_bank_map)




#======================= Importing Contacts =======================

contacts_map = {
    #'id':'' ,
    'first_name': lambda x: x['PFIRSTNAME,A,30'],
    'name': lambda x: x['PNAME,A,30'],
    'title': lambda x: {
        '0':'', #keep empty
        '1':'Mss', #should be the id of res.partner.title where name == 'Miss'
        '2':'Ms.', #should be the id of res.partner.title where name == 'Madam'
        '3':'M.', #should be the id of res.partner.title where name == 'Sir'
        '':'', #keep empty
        #~ #/!\ if an id cannot be found, the value should be ''
     }[x['PMF,A,1']],
    'mobile': lambda x: x['PGSM,A,25'],
#    'lang_id': lambda x: {
#        'E': 'English',#should be the id of res.lang where name == 'English'
#        'D': 'German',#should be the id of res.lang where name == 'German'
#        'F': 'French',#should be the id of res.lang where name == 'French'
#        'N': 'Dutch',#should be the id of res.lang where name == 'Dutch'
#        '': ''#for empty data.....
#
#        #~ #/!\ if an id cannot be found, the value should be ''
#     }[x['PLANGUAGE,A,2']],
#~ #have to be linked to the default adress of the partner with code == x['PCID,A,10']
    }

def import_contact(reader_contact, writer_contact, contacts_map):
    record = {}
    for key, column_name in contacts_map.items():
        record[key] = key
    writer_contact.writerow(record)
    for row in reader_contact:
        record = {}
        for key,fnct in contacts_map.items():
            record[key] = fnct(convert2utf(row))
        writer_contact.writerow(record)
    return True

print 'importing contacts'
reader_contact = csv.DictReader(file('original_csv/contacts.csv','rb'))
writer_contact = csv.DictWriter(file('res.partner.contact.csv','wb'),contacts_map.keys())
import_contact(reader_contact, writer_contact, contacts_map)




#======================= Importing Periods and FY =======================

fyear_map = {
    'id':  lambda x: 'FY'+x['YEAR,I,4'],
    'date_stop': lambda x: x['YEAR,I,4']+'-12-31', #last day of x['YEAR,I,4']
    'date_start': lambda x: x['YEAR,I,4']+'-01-01',#first day of x['YEAR,I,4']
    'code': lambda x: 'FY'+x['YEAR,I,4'],
    'name': lambda x: 'Fiscal Year '+x['YEAR,I,4'],
    'state': lambda x: 'draft',
}

def import_fyear(reader_fyear, writer_fyear, fyear_map):
    record = {}
    for key, column_name in fyear_map.items():
        record[key] = key
    writer_fyear.writerow(record)
    fyear_rows = []
    fyear_rows_ref = []
    #parse the period csv file to know what are the fiscal years that need to be created
    for row in reader_fyear:
        if row['YEAR,I,4'] not in fyear_rows_ref:
            fyear_rows_ref.append(row['YEAR,I,4'])
            fyear_rows.append(row)

    #create the fiscal years
    for fyear in fyear_rows:
        record = {}
        for key,fnct in fyear_map.items():
            record[key] = fnct(convert2utf(fyear))
        writer_fyear.writerow(record)
    return True

periods_map = {
    'id': lambda x: 'period_'+x['YEAR,I,4']+"-"+x['MONTH,I,4'],
    'date_stop': lambda x: get_last_day(mkDateTime(x['YEAR,I,4']+"-"+x['MONTH,I,4']+"-01")).strftime("%Y-%m-%d"),#should be the last day of x['MONTH,I,4']
    'date_start': lambda x:get_first_day(mkDateTime(x['YEAR,I,4']+"-"+x['MONTH,I,4']+"-01")).strftime("%Y-%m-%d"), #should be the first day of x['MONTH,I,4']

    'name': lambda x: x['LABEL,A,8'],
    'state': lambda x: 'draft',
    'fiscalyear_id:id': lambda x: 'FY'+x['YEAR,I,4'],#should be the id of account.fiscalyear for x['YEAR,I,4']
}

def import_period(reader_period, writer_period, period_map):
    record = {}
    for key, column_name in period_map.items():
        record[key] = key
    writer_period.writerow(record)
    period_rows = []
    for row in reader_period:
        #only create periods if x['MONTH,I,4'] != 0
        if row['MONTH,I,4'] != "0":
            record = {}
            for key,fnct in period_map.items():
                record[key] = fnct(convert2utf(row))
            writer_period.writerow(record)
    return True

print 'importing fiscal years'
reader_fyear = csv.DictReader(file('original_csv/periods.csv','rb'))
writer_fyear = csv.DictWriter(file('account.fiscalyear.csv', 'wb'), fyear_map.keys())
import_fyear(reader_fyear, writer_fyear, fyear_map)

print 'importing periods'
reader_period = csv.DictReader(file('original_csv/periods.csv','rb'))
writer_period = csv.DictWriter(file('account.period.csv', 'wb'), periods_map.keys())
import_period(reader_period, writer_period, periods_map)




#======================= Importing Move and Move_line =======================

move_map = {
    'id': lambda x: 'move_'+x['HDBK,A,4']+x['HFYEAR,A,5']+x['HDOCNO,I,4'], #+ numero de journal et année ?
#    'name': #should be filled with sequence number,
    'journal_id:id': lambda x: 'journal_'+x['HDBK,A,4'],
    'state': lambda x: 'draft',
    'period_id:id': lambda x: 'period_'+x['HFYEAR,A,5']+"-"+x['HMONTH,I,4'],
    'ref': lambda x: '',
}

def _check_debit(x):
    if (int(x['HAMOUNT,$,8']) > 0):
        return x['HAMOUNT,$,8']
    return 0

def _check_credit(x):
    if (int(x['HAMOUNT,$,8']) < 0):
        return -x['HAMOUNT,$,8']
    return 0




move_line_map = {
#TODO improve currency import
    'id': lambda x: 'move_line_'+x['HDBK,A,4']+x['HFYEAR,A,5']+x['HDOCNO,I,4']+x['HORDERNO,I,4'],
#@    'currency_id': x['HCURRENCY,A,3']
    'date_maturity': lambda x: x['HDUEDATE,D,4'],
    'partner_id:id': lambda x: x['HCUSSUP,A,10'],
#    'reconcile_partial_id':
#    'blocked':
#    'centralisation':
    'journal_id:id': lambda x: 'journal_'+x['HDBK,A,4'],
    'tax_code_id:id': lambda x: x['HVATCODE,A,10'] and vat_dict[x['HVATCODE,A,10']],
    'tax_amount': lambda x: x['HBASE,$,8'],

    'state': lambda x: 'draft',

        #qd vente: <0 c'est credit et >0 c'est debit
        #qd achat: <0 c'est le credit et >0 c'est debit
    'debit': lambda x: _check_debit(x), 
    'credit': lambda x: _check_credit(x),
    'ref': lambda x: x['HDOCNO,I,4'],
    'account_id:id': lambda x: 'account_'+x['HID,A,10'],
    'period_id:id': lambda x: 'period_'+x['HFYEAR,A,5']+"-"+x['HMONTH,I,4'],
#    'date_created':
    'date': lambda x: x['HDOCDATE,D,4'],
    'move_id:id': lambda x: 'move_'+x['HDBK,A,4']+x['HFYEAR,A,5']+x['HDOCNO,I,4'],
#@    'reconcile_id':
    'name': lambda x: x['HREM,A,40'] or '/',
#@    'amount_currency': x['HCURAMN,?,?']
#    'quantity':
}

def import_move(reader_move, writer_move, move_map):
    record = {}
    for key, column_name in move_map.items():
        record[key] = key
    writer_move.writerow(record)
    move_rows = []
    move_rows_ref = []
    #parse the move.csv file to know what are the account_move that need to be created
    for row in reader_move:
        #only create move if x['HMONTH,I,4'] != 0
        if row['HMONTH,I,4'] != "0":
            temp = 'move_line_'+row['HDBK,A,4']+row['HFYEAR,A,5']+row['HDOCNO,I,4']+row['HORDERNO,I,4']
            if temp not in move_rows_ref:
                move_rows_ref.append(temp)
                move_rows.append(row)

    #create the moves
    for move in move_rows:
        record = {}
        for key,fnct in move_map.items():
            record[key] = fnct(convert2utf(move))
        writer_move.writerow(record)
    return True

def import_move_line(reader, writer, map, ):
    record = {}
    for key, column_name in map.items():
        record[key] = key
    writer.writerow(record)
    period_rows = []
    for row in reader:
        #only create move_line if x['HMONTH,I,4'] != 0
        if row['HMONTH,I,4'] != "0":
            record = {}
            for key,fnct in map.items():
                record[key] = fnct(convert2utf(row))
            if record['partner_id:id']:
                record['partner_id:id'] = 'partner_' + str(record['partner_id:id'])
            writer.writerow(record)
    return True

#   1. constructing table account_tax => account_tax_code
reader_vat = csv.DictReader(file('original_csv/vat.csv','rb')) #TODO: will be given by pxview IFvat.DB -c > ....../account_bob_import/original_csv/vat.csv
vat_dict = construct_vat_dict(reader_vat, {})

#   2. importing move
print "importing account.move"
reader_move = csv.DictReader(file('original_csv/move.csv','rb'))#TODO: will be given by pxview IFahisto.db -c > ~/tinydev/cci/code/addons-extra/account_bob_import/original_csv/move.csv
writer_move = csv.DictWriter(file('account.move.csv', 'wb'), move_map.keys())
import_move(reader_move, writer_move, move_map)

#   3. importing move_line
print "importing account.move.line"
reader_move_line = csv.DictReader(file('original_csv/move.csv','rb'))
writer_move_line = csv.DictWriter(file('account.move.line.csv', 'wb'), move_line_map.keys())
import_move_line(reader_move_line, writer_move_line, move_line_map)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

