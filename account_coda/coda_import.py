import pooler
import time
import datetime
import wizard
import netsvc
import base64
from osv import osv

codawiz_form = """<?xml version="1.0"?>
<form string="Import Coda Statement">
<separator colspan="4" string="Select your bank journal :" />
    <field name="journal_id" colspan="1" domain="[('type','=','cash')]" />
    <separator string="Clic on 'New' to select your file :" colspan="4"/>
    <field name="coda"/>
</form>
"""

codawiz_fields = {
    'journal_id' : {
        'string':'Bank Journal',
        'type':'many2one',
        'relation':'account.journal',
        'required':True,
    },
    'coda' : {
        'string':'Coda File',
        'type':'binary',
        'required':True,
    },

}

result_form = """<?xml version="1.0"?>
<form string="Import Coda Statement">
<separator colspan="4" string="Results :" />
    <field name="note" colspan="4" nolabel="1" width="500"/>
</form>
"""

result_fields = {

    'note' : {'string':'Log','type':'text'}

}

def _coda_parsing(self, cr, uid, data, context):
    print "Coda Parsing is start here..........."
    pool = pooler.get_pool(cr.dbname)
    codafile = data['form']['coda']
    jur_id = data['form']['journal_id']
    recordlist = base64.decodestring(codafile).split('\n')

    records = []
    for line in recordlist:
        if line :
            s = list(line.rstrip())
            records.append(s)
    resstatement = {}
    resstatement['journal_id'] = jur_id
    resstatement_lines = []
    bn_statement = 0
    isHeader = False
    isFooter = False
    isOldBal = False
    isNewBal = False
    for line in records:
        if line[0] == '0':
            print "Header Record"
            if not isHeader:
                d = str2date(list2str(line[5:11]))
                resstatement['date'] = d
                period_id = pool.get('account.period').search(cr,uid,[('date_start','<=',time.strftime("%y/%m/%d",time.strptime(d,"%d/%m/%y"))),('date_stop','>=',time.strftime("%y/%m/%d",time.strptime(d,"%d/%m/%y")))])
                resstatement['period_id'] = period_id[0]
                bn_statement = pool.get('account.bank.statement').create(cr,uid,resstatement)
                isHeader = True
        elif line[0] == '1':
            print "OldBalance Record"
            if not isOldBal:
                bal_start = list2float(line[43:58])
                if line[42] == '1':
                    bal_start = - bal_start
                pool.get('account.bank.statement').write(cr,uid,[bn_statement],{'balance_start': bal_start})
                isOldBal = True
        elif line[0]=='2':
            print "Details Record"
            if line[1]=='1':
                print "movement Record here "
                st_line = {}
                st_line['statement_id']=bn_statement
                st_line['name'] = list2str(line[2:10])
                st_line['date'] = str2date(list2str(line[115:121]))
                st_line_amt = list2float(line[32:47])
                if line[31] == '1':
                    st_line_amt = - st_line_amt
                    st_line['account_id'] = pool.get('account.journal').browse(cr,uid,data['form']['journal_id'],context).default_debit_account_id.id
                else:
                    st_line['account_id'] = pool.get('account.journal').browse(cr,uid,data['form']['journal_id'],context).default_credit_account_id.id
                st_line['amount'] = st_line_amt
                bn_st_line = pool.get('account.bank.statement.line').create(cr,uid,st_line)
            elif line[1] == '3':
                print ""
                #st_line_name = list2str(line[2:10])
                #st_line_partner_name = list2str(line[47:82])
                #st_line_account_num = list2str(line[10:47])
                #partner_ids = pool.get('res.partner').search(cr,uid,[('date_start','<=',time.strftime("%y/%m/%d",time.strptime(d,"%d/%m/%y"))),('date_stop','>=',time.strftime("%y/%m/%d",time.strptime(d,"%d/%m/%y")))])



        elif line[0]=='3':
            print "Information Record"
        elif line[0]=='8':
            print "New Balance"
            if not isNewBal:
                bal_end = list2float(line[42:57])
                if line[41] == '1':
                    bal_end = - bal_end
                print bal_end
                pool.get('account.bank.statement').write(cr,uid,[bn_statement],{'balance_end_real': bal_end})

                isNewBal = True
        elif line[0]=='9':
            print "Trailler Record"

    #end for
    print "Finish Loop"
    return {}

def str2date(date_str):
            return time.strftime("%y/%m/%d",time.strptime(date_str,"%d%m%y"))
def str2float(str):
    try:
        return float(str)
    except:
        return 0.0


def list2str(lst):
            return str(lst).strip('[]').replace(',','').replace('\'','').replace(' ','')

def list2float(lst):
            try:
                return str2float((lambda s : s[:-3] + '.' + s[-3:])(list2str(lst)))
            except:
                return 0.0

class coda_import(wizard.interface):
    states = {
        'init' : {
            'actions' : [],
            'result' : {'type' : 'form',
                    'arch' : codawiz_form,
                    'fields' : codawiz_fields,
                    'state' : [('end', 'Cancel'),('extraction', 'Yes') ]}
        },
        'extraction' : {
            'actions' : [_coda_parsing],
            'result' : {'type' : 'form',
                        'arch' : result_form,
                        'fields' : result_fields,
                        'state' : [('end', 'Quit') ]}
        },

    }
coda_import("account.coda_import")









