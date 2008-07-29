#!/usr/bin/python
# -*- encoding: utf-8 -*-
import csv
import datetime
import time
from datetime import date, timedelta

#TODO:
##genere chart with parents :( => create a root with code = 0 then create the tree structure
##change it in order to run it server side
##remove close_method when mra's work is pushed

account_map = {
#   'id': lambda x: 'account_'+x['AID,A,10'], # will have to be uncomment for server side import
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
#   'company_id': lambda x: "Tiny sprl", #will be replaced by id of main company
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
#   'company_id': 'Company',
    'parent_id:id':'parent_id:id'
    #'close_method': 'Deferral Method',
    }

journals_map = {
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
    'default_debit_account_id:id':lambda x: x['DBACCOUNT,A,10'], #should be filled with the id of the account_account with code = x['DBACCOUNT,A,10'],
    'default_credit_account_id:id':lambda x: x['DBACCOUNT,A,10'] ,#should be filled with the id of the account_account with code =
}

#this dict is used to know the header of each column
journals_headers = {
    'code': 'code',
    'name': 'name',
    'view_id:id': 'view_id:id', # journal view for all except the ones that are of type cash => cash journal view
    'currency:id': 'currency:id',
    'sequence_id:id': 'sequence_id:id', #entry journal for all
    'type': 'type',
    'default_debit_account_id:id':'default_debit_account_id:id', #should be filled with the id of the account_account with code = x['DBACCOUNT,A,10'],
    'default_credit_account_id:id': 'default_credit_account_id:id' ,#should be filled with the id of the account_account with code =['DBACCOUNT,A,10'],
    }

#===============================================Partner=====================================================================
def _get_cat(record):
    res=[]
    if 'CSUPTYPE,A,1' in record and record['CSUPTYPE,A,1'].upper() in ['S'] :
        res.append('base.res_partner_category_8')
    if 'CCUSTYPE,A,1' in record and record['CCUSTYPE,A,1'].upper() in ['C']:
        res.append('base.res_partner_category_0')
    return ','.join(res)

partners_map = {
    'id':lambda a:'',
    'ref': lambda x: x['CID,A,10'],
    'name': lambda x: x['CNAME1,A,40'],
    'lang': lambda x: {
        'E': 'en_US', #'E' for English
        'D': 'de_DE',#'de_DE',#?? #'D' for German....de_DE
        'F': 'fr_FR',#'fr_FR',#??#'F' for French..fr_FR
        'N': 'nl_NL',#'nl_NL',#??#'N' for Dutch....nl_NL
        'A': '',#no lang
        '' : ''
        #/!\ if a lang isn't installed, the value should be filled with ''
    }[x['CLANGUAGE,A,2']],
    'vat': lambda x: x['CVATNO,A,12'],
    'website': lambda x: x['HTTPADDRESS,A,60'],
    'comment': lambda x: x['CMEMO,M,11'],
    'domiciliation_bool': lambda x : x['CBANKORDERPAY,L,1'],
    'domiciliation': lambda x : x['CBANKORDERPAYNO,A,15'],
    'category_id:id':lambda x:_get_cat(x),#['CSUPTYPE,A,1'],CCUSTYPE,A

    }

partners_headers = {
    'id': 'id' ,
    'ref': 'ref',
    'name': 'name',
    'lang': 'lang',
    'vat': 'vat',
    'website': 'website',
    'comment': 'comment',
    'domiciliation_bool': 'domiciliation_bool',
    'domiciliation': 'domiciliation',
    'category_id:id':'category_id:id',
    }


#===============================================Partner Address=====================================================================
partner_add_map = {
#have to create one res.partner.adress for this partner with
'city' : lambda x: x['CLOCALITY,A,40'],
'fax': lambda x: x['CFAXNO,A,25'],
'zip' :  lambda x: x['CZIPCODE,A,10'],
'country_id:id':lambda a:a['CCOUNTRY,A,6'], #should be filled with id of res.country that have code == x['CCOUNTRY,A,6']
'phone' : lambda x: x['CTELNO,A,25'],
'street' : lambda x: x['CADDRESS1,A,40'],
'type' : lambda x: 'default',
'partner_id:id':lambda x: ''
    }
partner_add_headers = {
#have to create one res.partner.adress for this partner with
'city' : 'city',
'fax': 'fax',
'zip' :  'zip',
'country_id:id' : 'country_id:id',#should be filled with id of res.country that have code == x['CCOUNTRY,A,6']
'phone' : 'phone',
'street' : 'street',
'type' : 'type',
'partner_id:id':'partner_id:id'
    }

#have to put the partner into category suppliers if CSUPTYPE,A,1 == 'S'
#have to put the partner into category customers if CCUSTYPE,A,1 == 'C'

#===============================================Partner Bank=====================================================================
#have to create res.partner.bank if x['CBANKNO,A,20'] <> False
partner_bank_map = {
'state': lambda s:'bank',#should be filled with id of res.Partner.bank.type that have name == 'Bank Account'
'acc_number': lambda x: x['CBANKNO,A,20'],
'partner_id:id':lambda x:''
}
partner_bank_headers = {
'state': 'state',#should be filled with id of res.Partner.bank.type that have name == 'Bank Account'
'acc_number': 'acc_number',
'partner_id:id':'partner_id:id'
}


#~ partners_map = {

    #~ 'id': ,
    #~ 'code': lambda x: x['CID,A,10'],
    #~ 'name': lambda x: x['CNAME1,A,40'],
    #~ 'lang': lambda x: {
        #~ 'E': 'en_US', #'E' for English
        #~ 'D': ?? #'D' for German
        #~ 'F': ??#'F' for French
        #~ 'N': ??#'N' for Dutch

        #~ #/!\ if a lang isn't installed, the value should be filled with ''
    #~ }[x['CLANGUAGE,A,2']],
    #~ 'vat': lambda x: x['CVATNO,A,12'],
    #~ 'website': lambda x: x['HTTPADDRESS,A,60'],
    #~ 'comment': lambda x: x['CMEMO,M,11'],
    #~ 'domiciliation_bool': lambda x : x['CBANKORDERPAY,L,1'],
    #~ 'domiciliation': lambda x : x['CBANKORDERPAYNO,A,15'],

#~ #have to create one res.partner.adress for this partner with
#~ 'city' : lambda x: x['CLOCALITY,A,40'],
#~ 'fax': lambda x: x['CFAXNO,A,25'],
#~ 'zip' :  lambda x: x['CZIPCODE,A,10'],
#~ 'country_id' #should be filled with id of res.country that have code == x['CCOUNTRY,A,6']
#~ 'phone' : lambda x: x['CTELNO,A,25'],
#~ 'street' : lambda x: x['CADDRESS1,A,40'],
#~ 'type' : lambda x: 'default',


#~ #have to put the partner into category suppliers if CSUPTYPE,A,1 == 'S'
#~ #have to put the partner into category customers if CCUSTYPE,A,1 == 'C'

#~ #have to create res.partner.bank if x['CBANKNO,A,20'] <> False
#~ 'state': #should be filled with id of res.Partner.bank.type that have name == 'Bank Account'
#~ 'acc_number': lambda x: x['CBANKNO,A,20'],

#~ }


#~ contacts_map = {

    #~ 'id': ,
    #~ 'first_name': lambda x: x['PFIRSTNAME,A,30'],
    #~ 'name': lambda x: x['PNAME,A,30'],
    #~ 'title': lambda x: {
        #~ '0': #keep empty
        #~ '1': #should be the id of res.partner.title where name == 'Miss'
        #~ '2': #should be the id of res.partner.title where name == 'Madam'
        #~ '3': #should be the id of res.partner.title where name == 'Sir'
        #~ '': #keep empty

        #~ #/!\ if an id cannot be found, the value should be ''
    #~ }[x['PMF,A,1']],
    #~ 'mobile': lambda x: x['PGSM,A,25'],
    #~ 'lang_id': lambda x: {
        #~ 'E': #should be the id of res.lang where name == 'English'
        #~ 'D': #should be the id of res.lang where name == 'German'
        #~ 'F': #should be the id of res.lang where name == 'French'
        #~ 'N': #should be the id of res.lang where name == 'Dutch'

        #~ #/!\ if an id cannot be found, the value should be ''
    #~ }[x['PLANGUAGE,A,2']],

#~ #have to be linked to the default adress of the partner with code == x['PCID,A,10']
#~ }


#with the periods.csv you have to create fiscal years and periods
fyear_map = {
#have to create fiscal year with x['YEAR,I,4'] if not created yet
'id':  lambda x: 'FY'+x['YEAR,I,4'],
'date_stop': lambda x: x['YEAR,I,4']+'-12-31', #should be the last day of x['YEAR,I,4']
'date_start': lambda x: x['YEAR,I,4']+'-01-01',#should be the first day of x['YEAR,I,4']
'code': lambda x: 'FY'+x['YEAR,I,4'],
'name': lambda x: 'Fiscal Year '+x['YEAR,I,4'],
'state': lambda x: 'draft',
}

fyear_headers = {
    'id': 'id',
    'date_stop': 'date_stop',
    'date_start': 'date_start',
    'code': 'code',
    'name': 'name',
    'state': 'state',
    }




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


periods_map = {
#    'id': ,
    'date_stop': lambda x: get_last_day(mkDateTime(x['YEAR,I,4']+"-"+x['MONTH,I,4']+"-01")).strftime("%Y-%m-%d"),#should be the last day of x['MONTH,I,4']
    'date_start': lambda x:get_first_day(mkDateTime(x['YEAR,I,4']+"-"+x['MONTH,I,4']+"-01")).strftime("%Y-%m-%d"), #should be the first day of x['MONTH,I,4']

    'name': lambda x: x['LABEL,A,8'],
    'state': lambda x: 'draft',
    'fiscalyear_id:id': lambda x: 'FY'+x['YEAR,I,4'],#should be the id of account.fiscalyear for x['YEAR,I,4']
}

periods_headers = {
    'date_stop': 'date_stop',
    'date_start': 'date_start',
    'name': 'name',
    'state': 'state',
    'fiscalyear_id:id': 'fiscalyear_id:id',
}

def convert2utf(row):
    if row:
        retRow = {}
        for k,v in row.items():
            retRow[k] = v.decode('latin1').encode('utf8').strip()
        return retRow
    return row

def import_account(reader, writer, mapping, column_headers):
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

def import_journal(reader_journal, writer_journal, journals_map, journals_headers):
    record = {}
    for key, column_name in journals_headers.items():
        record[key] = column_name
    writer_journal.writerow(record)
    for row in reader_journal:
        record = {}
        for key,fnct in journals_map.items():
            record[key] = fnct(convert2utf(row))
        if record['default_debit_account_id:id']:
            record['default_debit_account_id:id'] = 'id' + str(record['default_debit_account_id:id'])
        if record['default_credit_account_id:id']:
            record['default_credit_account_id:id'] = 'id' + str(record['default_credit_account_id:id'])
        if record['type']=='cash':
            record['view_id:id']='account.account_journal_bank_view'
        cur = ''
        if record['currency:id']:
            cur = 'base.' + record['currency:id'].upper()
        record['currency:id'] = cur
        writer_journal.writerow(record)
    return True

def import_partner(reader_partner, writer_partner, partners_map, partners_headers, writer_address, partner_add_map, partner_add_headers, writer_bank, partner_bank_map, partner_bank_headers):
    record = {}
    record_address = {}
    record_bank = {}
    list_partners = []

    for key, column_name in partners_headers.items():
        record[key] = column_name
    for key, column_name in partner_add_headers.items():
        record_address[key] = column_name
    for key, column_name in partner_bank_headers.items():
        record_bank[key] = column_name

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

def import_fyear(reader_fyear, writer_fyear, fyear_map, fyear_headers):
    record = {}
    for key, column_name in fyear_headers.items():
        record[key] = column_name
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

def import_period(reader_period, writer_period, period_map, period_headers):
    record = {}
    for key, column_name in period_headers.items():
        record[key] = column_name
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


#importing chart of accounts
reader_account = csv.DictReader(file('original_csv/accounts.csv','rb'))
writer_account = csv.DictWriter(file('account.account.csv', 'wb'), account_map.keys())
import_account(reader_account, writer_account, account_map, account_headers)

#importing financial journals
reader_journal = csv.DictReader(file('original_csv/journals.csv','rb'))
writer_journal = csv.DictWriter(file('account.journal.csv', 'wb'), journals_map.keys())
import_journal(reader_journal, writer_journal, journals_map, journals_headers)

#importing Partners and its addresses
reader_partner = csv.DictReader(file('original_csv/partners.csv','rb'))
writer_partner = csv.DictWriter(file('res.partner.csv', 'wb'), partners_map.keys())
writer_address = csv.DictWriter(file('res.partner.address.csv','wb'), partner_add_map.keys())
writer_bank = csv.DictWriter(file('res.partner.bank.csv','wb'), partner_bank_map.keys())
import_partner(reader_partner, writer_partner, partners_map, partners_headers, writer_address, partner_add_map, partner_add_headers, writer_bank,  partner_bank_map, partner_bank_headers)



#importing periods and fiscal years
reader_fyear = csv.DictReader(file('original_csv/periods.csv','rb'))
writer_fyear = csv.DictWriter(file('account.fiscalyear.csv', 'wb'), fyear_map.keys())
import_fyear(reader_fyear, writer_fyear, fyear_map, fyear_headers)

reader_period = csv.DictReader(file('original_csv/periods.csv','rb'))
writer_period = csv.DictWriter(file('account.period.csv', 'wb'), periods_map.keys())
import_period(reader_period, writer_period, periods_map, periods_headers)

move_map = {
    'id': lambda x: 'move_'+x['MID,A,40'],
    'account_id:id': lambda x: 'account_'+x['AID']
}

#TODO:
#   Minimal Account Chart & Properties: Demo Only
#   Create Objects:
#       account.account.template
#           idem a account.account + champ selection property
#       account.tax.template
#       account.journal.template
#   Wizard:
#       Prend un template -> genere un vrai plan
#           - Societe -
#           - Template -
#       Cree properties
#   Changer l10n_be et l10n_fr, l10n_ch

#~ Problemes:
    #~ Minimal Account Chart : Demo Only
    #~ Creer une nouvelle societe (nvx plan de compte)
        #~ -> dupliquer un plan de compte si meme pays
        #~ -> si pas meme pays: installer l10n_XXX


#~ if __name__=='__main__':
    #~ pass

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

