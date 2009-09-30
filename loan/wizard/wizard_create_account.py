import wizard
import pooler

acct_form = '''<?xml version="1.0"?>
<form string="Select period">

    <field name="cus_pay_acc" select="1"/>
    <newline/>
    <field name="parent_emp_pay_acc" select="1"/>
    <newline/>
    <field name="int_acc" select="1"/>
    <newline/>
    <field name="bank_acc" select="1"/>
    <newline/>
    <field name="proc_fee" select="1"/>
    <newline/>   
 </form>'''

acct_fields = {
                     
    'cus_pay_acc': {'string': 'Customer Loan Account', 'type': 'char', 'required': 'True', 'size':'200' },
    'parent_emp_pay_acc': {'string': 'Parent Loan Account', 'type': 'many2one', 'relation': 'account.account', 'domain':"[('type','=','other')]",'required': 'True','help':'This is parent account for Employee Payable Account' },
    'int_acc':{'string': 'Interest Account', 'type': 'many2one', 'relation': 'account.account', 'domain':"[('type','=','other')]",'required': 'True' },
    'bank_acc': {'string': 'Bank Account', 'type': 'many2one', 'relation': 'account.account', 'domain':"[('type','=','other')]",'required': 'True'},
    'proc_fee': {'string': 'Processing fee Account', 'type': 'many2one', 'relation': 'account.account', 'domain':"[('type','=','other')]",'required': 'True'},
}

class wizard_cus_acct(wizard.interface): 
    
          
    def get_defaults(self, cr, uid, data, context):
        user = pooler.get_pool(cr.dbname).get('account.loan').browse(cr, uid, data['id'])
        data['form']['cus_pay_acc'] = user.loan_id 
        return data['form']
    
    def create_cus_acct(self, cr, uid, data, context):
        cname = data['form']['cus_pay_acc']
        print'cname----------------------',cname
        par_cname = data['form']['parent_emp_pay_acc']
        print'par_cname-----------------------',par_cname
        dname = data['form']['int_acc']
        print'dname------------------',dname
        bnk_acc = data['form']['bank_acc'] 
        print'bnk_acc---------------------',bnk_acc
        prc_fee = data['form']['proc_fee'] 
        print'bnk_acc---------------------',prc_fee        
        
        account = pooler.get_pool(cr.dbname).get('account.account')
        type = pooler.get_pool(cr.dbname).get("account.account.type")
        user = pooler.get_pool(cr.dbname).get("account.loan")
        
        lia_id = type.search(cr, uid, [('code','=','liability')])
        exp_id = type.search(cr, uid, [('code','=','expense')])
        ass_id = type.search(cr, uid, [('code','=','asset')])
        inc_id = type.search(cr, uid, [('code','=','income')])
        
        loan_id = user.read(cr, uid ,[data['id']], ['loan_id'])[0]['loan_id']
        name = user.read(cr, uid ,[data['id']], ['partner_id'])[0]['partner_id']
        print'name in wizard----------------------------------------',name
    
        credit_id = account.create(cr, uid, {
            'code': name[1] + '/' + loan_id,
            'name':cname,
            'parent_id':par_cname,
            'type':'other',
            'reconcile':True,
            'user_type':ass_id[0]
            })

       
        user.write(cr,uid,data['id'],{'cus_pay_acc' :credit_id, 'int_acc' : dname, 'bank_acc' : bnk_acc,'proc_fee':prc_fee})
                        
        return {}
    
    states = {
        'init': {
            'actions': [get_defaults],
            'result': {'type':'form', 'arch':acct_form, 'fields':acct_fields, 'state':[('create','Create'),('end','Cancel','gtk-cancel')]}
        },
        'create': {
            'actions': [create_cus_acct],
            'result': {'type':'state','state':'end'}
        }
    }
wizard_cus_acct('wizard_cus_acct')