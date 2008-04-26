import time
import pooler
from report import report_sxw


STATE = [
    ('none', 'Non Member'),
    ('canceled', 'Canceled Member'),
    ('old', 'Old Member'),
    ('waiting', 'Waiting Member'),
    ('invoiced', 'Invoiced Member'),
    ('associated', 'Associated Member'),
    ('free', 'Free Member'),
    ('paid', 'Paid Member'),
]

class account_invoice_draft(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_invoice_draft, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'partner_info':self.partner_info,
            'member_type':self.member_type,
            'nationality':self.nationality,
            'lines':self.lines,
            'sum_amt_untaxed':self.sum_amt_untaxed,
            'sum_amt_tax':self.sum_amt_tax,
            'sum_total':self.sum_total,
        })
        self.sum_untaxed=0.00
        self.sum_tax=0.00
        self.sum_tot=0.00

    def partner_info(self, object):

        list_fileds=['title','name','street','street2']
        address_info=''
        if object.address:
            for ads in object.address:
                if ads.type=='default':
                    if ads.title:
                        address_info +=ads.title
                    if ads.name:
                        address_info +=' ' +ads.name
                    if ads.street:
                        address_info +='\n' +ads.street
                    if ads.street2:
                        address_info +=' '+ ads.street2
                    if ads.zip_id:
                        address_info +='\n' +pooler.get_pool(self.cr.dbname).get('res.partner.zip').name_get(self.cr,self.uid,[ads.zip_id.id])[0][1]
                    if ads.state_id:
                        address_info += '\n' + ads.state_id.name
                    if ads.country_id:
                        address_info +='\n' + ads.country_id.code
                    if ads.phone:
                        address_info +='\nTel: ' + ads.phone
                    if ads.fax:
                        address_info +='\nFAX: ' + ads.fax
        if object.vat:
            address_info +='\nVAT: '+ object.vat

        return address_info

    def member_type(self, object):
        membership=object.membership_state
        for member_type in STATE:
            if membership==member_type[0]:
                membership=member_type[1]
                break
        return membership

    def nationality(self, object):
        nationality='Not Mentioned'
        if object.address:
            for ads in object.address:
                if ads.type=='default':
                  if ads.country_id:
                        if ads.country_id.code=='BE':
                            nationality='Belgian'
                        else:
                            nationality='Non-Belgian'

        return nationality

    def lines(self, object):
        result=[]
        obj_inv=pooler.get_pool(self.cr.dbname).get('account.invoice')
        list_ids=obj_inv.search(self.cr,self.uid,[('state','=','draft'),('partner_id','=',object.id)])
        invoices=obj_inv.browse(self.cr,self.uid,list_ids)

        for invoice in invoices:
            res={}
            res['name']=invoice.name
            #invoice no. - a confusing character
            res['invoice_no']=invoice.number
            res['date']=invoice.date_invoice
            res['amt_untaxed']=invoice.amount_untaxed
            self.sum_untaxed +=invoice.amount_untaxed

            res['vat']=invoice.amount_tax
            self.sum_tax +=invoice.amount_tax

            res['total']=invoice.amount_total
            self.sum_tot +=invoice.amount_total

            res['gen_acc']=invoice.account_id.name
            # analytic account -- Is it related to invoice?
            res['analytic_acc']=''
            result.append(res)

        return result

    def sum_amt_untaxed(self):
        return self.sum_untaxed

    def sum_amt_tax(self):
        return self.sum_tax

    def sum_total(self):
        return self.sum_tot

report_sxw.report_sxw('report.partner.draft_invoices', 'res.partner', 'addons/cci_account/report/cci_draft_invoice_info.rml', parser=account_invoice_draft)