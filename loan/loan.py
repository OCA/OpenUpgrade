
import time
import datetime
from datetime import date
#import osv;
from osv import osv
from osv import fields

class loan_customer(osv.osv):
    _name = 'res.partner';
    _inherit = 'res.partner';
    _columns = {
        'incom': fields.float('Monthly Incom',digits=(12,3)),
    }
#end class
loan_customer();

class account_loan(osv.osv):

    def _loan_period_get(self, cr, uid, context={}):
        obj = self.pool.get('loan.installment.period')
        ids = obj.search(cr, uid,[('name','ilike','')])
        res = obj.read(cr, uid, ids, ['name','period'], context)
        return [(r['name'], r['name']) for r in res]

    def _loan_type_get(self, cr, uid, context={}):
        obj = self.pool.get('account.loan.loantype')
        ids = obj.search(cr, uid,[('name','ilike','')])
        res = obj.read(cr, uid, ids, ['name','calculation'], context)
        return [(r['name'], r['name']) for r in res]

    _name = 'account.loan'
    _columns = {
        'loan_id': fields.char('Loan Id', size=32, required=True),
        'proof_id':fields.one2many('account.loan.proof','loan_id','Proof Detail'),
        'auto_id': fields.integer('Auto Id', size=32),
        'name': fields.char('Description', size=128, required=True),
        'partner_id': fields.many2one('res.partner', 'Customer'),
        'proof_1': fields.many2one('res.partner', 'Gaurenter 1'),
        'proof_2': fields.many2one('res.partner', 'Gaurenter 2'),
        'contact': fields.many2one('res.partner.address', 'Contact'),
        'loan_type':fields.selection(_loan_type_get,'Loan Type',select=True, required=True),
        'loan_period':fields.selection(_loan_period_get,'Loan Period',select=True, required=True),
        'loan_amount': fields.float('Loan Amount',digits=(12,2), states={'draft':[('readonly',False)]}),
        'approve_amount': fields.float('Approve Amount',digits=(12,2),readonly=True),
        'process_fee': fields.float('Processing Fee',digits=(12,2)),
        'total_installment': fields.integer('Total Installment', readonly=False),
        'interest_rate': fields.float('Interest Rate',digits=(10,2),readonly=True),
        'apply_date': fields.date('Apply Date', states={'draft':[('readonly',False)]}),
        'approve_date': fields.date('Approve Date',readonly=True),
        'cheque_ids':fields.one2many('account.loan.bank.cheque','loan_id','Cheque Detail'),
        'state': fields.selection([
           ('draft','Quotation'),
           ('proof approval','Proof Approved'),
           ('apply','Applied'),
           ('done','Approved'),
           ('cancel','Reject'),
        ],'State', readonly=True, select=True),
        'return_type': fields.selection([
           ('cash','By Cash'),
           ('cheque','By Cheque'),
           ('automatic','Automatic Payment'),
        ],'Payment Type', select=True),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', required=False, readonly=True, states={'draft':[('readonly',False)]}),
        'running_loan' : fields.many2many('account.loan', 'account_loan_running','loan_id','auto_id', 'Current Loans'),
        #'papers' : fields.many2one('letter.letter', 'Loan Papers'),
        'installment_id' :fields.one2many('account.loan.installment','loan_id','Installments'),
        'interest' : fields.float('Interest'),
        'invoice_id': fields.many2one('account.invoice', 'Invoice',readonly=True),
        'notes' : fields.text('Description')
    }
    _defaults = {
         'auto_id': lambda obj, cr, uid, context: int(obj.pool.get('ir.sequence').get(cr, uid, 'loan.id')),
         'loan_id': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'loan.number'),
         'state': lambda *a: 'draft',
         'apply_date': lambda *a: time.strftime('%Y-%m-%d'),
         'total_installment':lambda *a: 0.0,
         'return_type':lambda *a:'cheque',
    }

    def onchange_partner_id(self, cr, uid, ids, part):
        if not part:
            return {'value':{'contact': False}}
        addr = self.pool.get('res.partner').address_get(cr, uid, [part], ['default','invoice'])
        return {'value':{'contact': addr['default']}}
    #end def

    def onchange_loan_period(self, cr, uid, ids, part):
        sear_list = self.pool.get('loan.installment.period').search(cr,uid,[('name','=',part)])
        value_period = self.pool.get('loan.installment.period').browse(cr, uid, sear_list[0]).period
        return {'value':{'total_installment': value_period}}
    #end def


    def loan_interest_get(self,cr, uid, ids,context={}):
        loan = self.pool.get('account.loan').read(cr,uid,ids)
        loantype =  loan[0]['loan_type']
        self.pool.get('account.loan').write(cr,uid,ids,{'approve_amount':loan[0]['loan_amount'] - loan[0]['process_fee']});
        self.pool.get('account.loan').write(cr,uid,ids,{'approve_date':time.strftime('%Y/%m/%d')});
        if loantype != '':
            search_loantype = self.pool.get('account.loan.loantype').search(cr,uid,[('name','=',loan[0]['loan_type'])])
            available_versions = self.pool.get('account.loan.loantype').browse(cr,uid,search_loantype[0]).interestversion_ids
            if available_versions:
                search_validversion = self.pool.get('account.loan.loantype.interestversion').search(cr,uid,[('loantype_id','=',search_loantype[0]),('start_date','<=',loan[0]['apply_date']),('end_date','>=',loan[0]['apply_date'])])
                if search_validversion:
                    available_versionlines = self.pool.get('account.loan.loantype.interestversion').browse(cr,uid,search_validversion[0]).interestversionline_ids
                    if available_versionlines:
                        search_validversionlines = self.pool.get('account.loan.loantype.interestversionline').search(cr,uid,[('interestversion_id','=',search_validversion[0]),('min_month','<=',loan[0]['total_installment']),('max_month','>=',loan[0]['total_installment']),('min_amount','<=',loan[0]['loan_amount']),('max_amount','>=',loan[0]['loan_amount'])])
                        if search_validversionlines:
                            valid_versionline = self.pool.get('account.loan.loantype.interestversionline').browse(cr,uid,search_validversionlines[0]).rate
                            if valid_versionline:
                                self.pool.get('account.loan').write(cr, uid,ids, {'interest_rate':valid_versionline})
                            else:
                                raise osv.except_osv('Information Required','Interest Rate is Not Defined')
                        #end if
                        else:

                            raise osv.except_osv('Information Required','There is not valid interest versionlines availble. so please check it')
                        #end else
                    #end if
                    else:
                        raise osv.except_osv('Information Required','There is no versions Defined.')
                #end If
                else:
                    raise osv.except_osv('Information Required','Interest version is Not Defined')
            #end if
            else:
                raise osv.except_osv('Information Required','Interest version is Not Defined')
            #end else
        #end if
        else:
            raise osv.except_osv('Information Required','Loan Type is Not Defined')
        #end else
    #end def

    def _simple_interest_get(self, cr, uid, ids, inter_rate):
        loan = self.pool.get('account.loan').read(cr,uid,ids)
        installment_cr = self.pool.get('account.loan.installment')
        cheque_cr = self.pool.get('account.loan.bank.cheque')
        #/////////////////////////partner_id checking/////////////////////////////////////////////////////
        if loan[0]['partner_id']:
            part_id = loan[0]['partner_id'][0]
        else:
            raise osv.except_osv('Field Required','Please select Customer');
        #end if
        #/////////////////////////bank_i'loan_id': fields.many2one('account.loan', 'loan_id'),d, account_id checking////////////////////////////////////////////
        acc_ids = False
        if loan[0]['return_type'] == 'cheque':
            bank_ids=self.pool.get('res.partner.bank').search(cr,uid,[('partner_id','=',part_id)])
            if bank_ids:
                acc_ids=self.pool.get('res.partner.bank').read(cr, uid, bank_ids,['acc_number'])[0]['acc_number']
            else:
                raise osv.except_osv('Field Required','Please select Bank Account For '+loan[0]['partner_id'][1])
            #end if
        #end if
        #///////////////////////////interest calculation process//////////////////////////////////
        rate_interest = inter_rate / 100
        total = loan[0]['loan_amount'] #- loan[0]['process_fee']
        installment = ((total*(rate_interest/12))/(1-((1+rate_interest/12)**-(loan[0]['total_installment']))))
        i = 1
        interest = 0
        date_update = datetime.date(2000,01,07)
        date_new = date.today()
        if date_update != date_new:
            new_month = date_new.month
            new_year = date_new.year
            date_update = date_update.replace(month=new_month)
            date_update = date_update.replace(year=new_year)
        present_month = date_update.month
        while i <= loan[0]['total_installment']:
            interest_month = ((total*rate_interest)/12)
            principle_amount = installment - interest_month
            remain_amount = total - principle_amount
            if loan[0]['return_type'] == 'cheque':
                for j in range(1,loan[0]['total_installment']):
                    present_month +=1
                    if present_month>12:
                        present_month = 1;
                        s = date_update.year + 1
                        date_update=date_update.replace(year=s);
                    #end if
                    date_update=date_update.replace(month=present_month);
                    cheque_cr.create(cr, uid, {'name':'cheque'+str(i),'date':date_update,'loan_id':ids[0],'code':'cheque'+str(i),'partner_id':part_id,'loan_bank_id':bank_ids[0],'account_id': acc_ids[0],'cheque_amount':installment,'loan':principle_amount,'interest':interest_month})
                    break
                #end for
            #end if
            installment_cr.create(cr,uid,{'name':'installment'+str(i),'loan_id':ids[0],'capital':principle_amount,'interest':interest_month,'total':installment})
            total = remain_amount
            interest += interest_month
            i+= 1;
        #end while
        self.pool.get('account.loan').write(cr,uid,ids,{'interest':interest});
    #end def

    # for invoice of loan
    def reject_loan(self, cr, uid, ids,context = {}):
        for loan in self.browse(cr, uid, ids):
            if loan.invoice_id and loan.invoice_id.state not in ('draft','cancel'):
                raise osv.except_osv(
                   'Could not Reject Loan !',
                   'You must first cancel invoice attaced to this loan.')


        installment_cr = self.pool.get('account.loan.installment')
        install_ids = installment_cr.search(cr,uid,[('loan_id','=',ids[0])]);
        installment_cr.unlink(cr,uid,install_ids);

        cheque_cr = self.pool.get('account.loan.bank.cheque')
        chq_ids = cheque_cr.search(cr,uid,[('loan_id','=',ids[0])]);
        cheque_cr.unlink(cr,uid,chq_ids);
        return True


    def proof_approval(self, cr, uid, ids,context = {}):
        loan = self.pool.get('account.loan').read(cr,uid,ids)
        loantype =  loan[0]['loan_type']
        if loantype != '':
            search_loantype = self.pool.get('account.loan.loantype').search(cr,uid,[('name','=',loantype)])
            prooftype_req = self.pool.get('account.loan.loantype').browse(cr,uid,search_loantype[0]).prooftypes
            for pt in prooftype_req:
                avail_proof_docs = self.pool.get('account.loan.proof').search(cr,uid,[('loan_id','=',ids[0]),('type','=',pt.name),('state','=','done')])
                if not avail_proof_docs:
                     raise osv.except_osv('Field Required','This loan object has not valid ' + pt.name + ' proofs so please submit proof again and valid it')
            #end for
            self.pool.get('account.loan').write(cr,uid,ids,{'state':'apply'})
        #end if
        else:
            raise osv.except_osv('Information Required','Loan Type is Not Defined')
    #end def

    def apply_loan(self, cr, uid, ids,context = {}):
            loan = self.pool.get('account.loan').read(cr,uid,ids)
            inter_rate = loan[0]['interest_rate']
    #/////////////////////////////////interest calculation method////////////////////////////////////
            inter_sed=self.pool.get('account.loan.loantype').search(cr,uid,[('name','=',loan[0]['loan_type'])])
            if inter_sed:
                inter_cal_type = self.pool.get('account.loan.loantype').browse(cr, uid, inter_sed[0]).calculation
                if inter_cal_type:
                    if inter_cal_type == 'simple':
                        interest_rate1= self.pool.get('account.loan')._simple_interest_get(cr, uid,ids,inter_rate)
                    elif inter_cal_type == 'compound':
                        raise osv.except_osv('Function Left','Compound interest calculation is left')
                #end if
                else:
                    raise osv.except_osv('Field Required','Interest Type Not Selected')
            #end if
            else:
                raise osv.except_osv('Field Required','Interest Type Not Defined')
        #end if
    #end def

    def loan_clear(self,cr,uid,ids,context={}):

        res = False
        invoices = {}
        invoice_ids = []

        def make_invoice(loan):
            a = loan.partner_id.property_account_receivable.id
            b = loan.partner_id.property_account_payable.id
            #print loan
            if loan.partner_id and loan.partner_id.property_payment_term:
                pay_term = loan.partner_id.property_payment_term.id
            else:
                pay_term = False
            create_ids=[]
            inv_id = self.pool.get('account.invoice.line').create(cr, uid, {
                    'name': loan.name,
                    'account_id': b,
                    'price_unit': loan.loan_amount,
                    'quantity': 1,
                    'discount': False,
                    'uos_id': False,
                    'product_id': False,
                    'invoice_line_tax_id': False,
                    'note':False,
            })

            create_ids.append(inv_id)
            inv = {
                'name': loan.name,
                'origin': loan.name,
                'type': 'out_invoice',
                'reference': "P%dSO%d"%(loan.partner_id.id,loan.id),
                'account_id': a,
                'partner_id': loan.partner_id.id,
                'address_invoice_id': loan.contact.id,
                'address_contact_id': False,
                #'project_id': False,
                'invoice_line': [(6,0,create_ids)],
                'currency_id' : 1,
                'comment': "",
                'payment_term': pay_term,
            }
            print inv['invoice_line']

            inv_obj = self.pool.get('account.invoice')
            inv_id = inv_obj.create(cr, uid, inv)

            for o in self.pool.get('account.loan').browse(cr,uid,ids):
                self.write(cr, uid, [o.id], {'invoice_id': inv_id})

            inv_obj.button_compute(cr, uid, [inv_id])
            return inv_id

        for o in self.pool.get('account.loan').browse(cr,uid,ids):
            res = make_invoice(o)
            print res
        return res
    #end def
#end class
account_loan();
