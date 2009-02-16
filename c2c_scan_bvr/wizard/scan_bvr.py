# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008-Now CampToCamp SA
#
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import wizard
import pooler
import time
from tools.misc import UpdateableStr
import pdb

FORM = UpdateableStr()
#
# TODO: check unit of measure !!!
#
class scan_bvr(wizard.interface):

    def _check_number(self,part_validation):
        nTab = [0, 9, 4, 6, 8, 2, 7, 1, 3, 5]
        resultnumber = 0;
        for number in part_validation:
            resultnumber = nTab[(resultnumber + int(number) - 0) % 10]
        return (10 - resultnumber) % 10

    def _get_invoice_address(self,cr,uid,partner_address):
                valid_address_id = ''
                for partner_address_object in partner_address:
                        if partner_address_object.type == "invoice":
                                valid_address_id = partner_address_object.id
                if not valid_address_id:
                        if len(partner_address) > 0:
                                valid_address_id = partner_address[0].id
                        else:
                                 raise wizard.except_wizard('AddressError', 
                                    'No Address Assign to this partner')
                return valid_address_id
    def _construct_bvrplus_in_chf(self,bvr_string):
            ##
            if len(bvr_string) <> 43:
                raise wizard.except_wizard('AccountError', 
                    'BVR CheckSum Error Première partie')
            elif self._check_number(bvr_string[0:2]) <> int(bvr_string[2]):
                raise wizard.except_wizard('AccountError', 
                    'BVR CheckSum Error Deuxième partie')
            elif self._check_number(bvr_string[4:30]) <> int(bvr_string[30]):
                raise wizard.except_wizard('AccountError', 
                    'BVR CheckSum Error troisème partie')
            elif self._check_number(bvr_string[33:41]) <> int(bvr_string[41]):
                raise wizard.except_wizard('AccountError', 
                    'BVR CheckSum Error 4 partie')
            else:
                    bvr_struct = {
                                  'type' : bvr_string[0:2],
                                  'amount' : 0.0,
                                  'reference' : bvr_string[4:31],
                                  'bvrnumber' : bvr_string[4:10],
                                  'beneficiaire' : self._create_bvr_account(
                                        bvr_string[33:42]
                                    ),
                                  'domain' : '',
                                  'currency' : ''
                                  }
                    return bvr_struct
        
    def _construct_bvr_in_chf(self,bvr_string):
            if len(bvr_string) <> 53:
                raise wizard.except_wizard('AccountError', 
                    'BVR CheckSum Error Première partie')
            elif self._check_number(bvr_string[0:12]) <> int(bvr_string[12]):
                raise wizard.except_wizard('AccountError', 
                    'BVR CheckSum Error Deuxième partie')
            elif self._check_number(bvr_string[14:40]) <> int(bvr_string[40]):
                raise wizard.except_wizard('AccountError', 
                    'BVR CheckSum Error troisème partie')
            elif self._check_number(bvr_string[43:51]) <> int(bvr_string[51]):
                raise wizard.except_wizard('AccountError', 
                    'BVR CheckSum Error 4 partie')
            else:
                    bvr_struct = {
                                  'type' : bvr_string[0:2],
                                  'amount' : float(bvr_string[2:12])/100,
                                  'reference' : bvr_string[14:41],
                                  'bvrnumber' : bvr_string[14:20],
                                  'beneficiaire' : self._create_bvr_account(
                                        bvr_string[43:52]
                                    ),
                                  'domain' : '',
                                  'currency' : ''
                                  }
                    return bvr_struct

    def _construct_bvr_postal_in_chf(self,bvr_string):
            ##
            
            if len(bvr_string) <> 42:
                raise wizard.except_wizard('AccountError', 
                    'BVR CheckSum Error Première partie')
            else:

                    bvr_struct = {
                                  'type' : bvr_string[0:2],
                                  'amount' : float(bvr_string[2:12])/100,
                                  'reference' : bvr_string[14:30],
                                  'bvrnumber' : '',
                                  'beneficiaire' : self._create_bvr_account(
                                        bvr_string[32:41]
                                    ),
                                  'domain' : '',
                                  'currency' : ''
                                  }
                    
                    return bvr_struct

    def _construct_bvr_postal_other_in_chf(self,bvr_string):
            ##
            
            if len(bvr_string) <> 41:
                raise wizard.except_wizard('AccountError', 
                    'BVR CheckSum Error Première partie')
            else:

                    bvr_struct = {
                                  'type' : bvr_string[0:2],
                                  'amount' : float(bvr_string[7:16])/100,
                                  'reference' : bvr_string[18:33],
                                  'bvrnumber' : '000000',
                                  'beneficiaire' : self._create_bvr_account(
                                        bvr_string[34:40]
                                    ),
                                  'domain' : '',
                                  'currency' : ''
                                  }
                    
                    return bvr_struct

    
    def _create_direct_invoice(self, cr, uid, data, context):
                    pool = pooler.get_pool(cr.dbname)
                    if data['form']['Account_list']:
                        account_info = pool.get('res.partner.bank').browse(cr,uid,data['form']['Account_list'])
                    ## We will now search the currency_id
                    #
                    
                    #
                    currency_search = pool.get('res.currency').search(cr,uid,[('code', '=',data['bvr_struct']['currency'])])
                    currency_id = pool.get('res.currency').browse(cr,uid,currency_search[0])
                    ## Account Modification
                    if data['bvr_struct']['domain'] == 'name':
                        pool.get('res.partner.bank').write(cr,uid,data['form']['Account_list'],{'bvr_number': data['bvr_struct']['beneficiaire']})
                    else:
                        pool.get('res.partner.bank').write(cr,uid,data['form']['Account_list'],{'bvr_adherent_num': data['bvr_struct']['bvrnumber'],'bvr_number': data['bvr_struct']['beneficiaire']})
                    date_due = time.strftime('%Y-%m-%d')
                    # We will now compute the due date and fixe the payment term
                    payment_term_id = account_info.partner_id.property_payment_term and account_info.partner_id.property_payment_term.id or False
                    if payment_term_id:
                        #We Calculate due_date
                        res = pool.get('account.invoice').onchange_payment_term_date_invoice(cr,uid,[],payment_term_id,time.strftime('%Y-%m-%d'))
                        date_due = res['value']['date_due']
                    ##
                    #
                    curr_invoice = {
                            'name': time.strftime('%Y-%m-%d'),
                            'partner_id': account_info.partner_id.id,
                            'address_invoice_id': self._get_invoice_address(cr,uid,account_info.partner_id.address),
                            'account_id': account_info.partner_id.property_account_payable.id,
                            'date_due': date_due,
                            'date_invoice': time.strftime('%Y-%m-%d'),
                            'payment_term': payment_term_id,
                            'reference_type': 'bvr',
                            'reference' :  data['bvr_struct']['reference'],
                            'amount_total' :  data['bvr_struct']['amount'],
                            'check_total' :  data['bvr_struct']['amount'],
                            'partner_bank' : account_info.id,
                            'comment': '',
                            'currency_id': currency_id.id,
                            'journal_id' : data['form']['invoice_journal'] ,
                            'type': 'in_invoice',
                    }
                    
                    last_invoice = pool.get('account.invoice').create(cr, uid, curr_invoice)
                    invoices = []
                    invoices.append(last_invoice)
                    return {
                    'domain': "[('id','in', ["+','.join(map(str,invoices))+"])]",
                    'name': 'Invoices',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'account.invoice',
                    'view_id': False,
                    'context': "{'type':'out_invoice'}",
                    'type': 'ir.actions.act_window',
                    'res_id':invoices
                    }
 
    def _create_bvr_account(self,account_unformated):
        
        account_formated = account_unformated[0:2] + '-' + str(int(account_unformated[2:len(account_unformated)-1])) + '-' +  account_unformated[len(account_unformated)-1:len(account_unformated)]
        
        return account_formated
    
    def _get_bvr_structurated(self,bvr_string):
        if bvr_string <> False:
            ## We will get the 2 frist digit of the BVr string in order
            ## to now the BVR type of this account
            bvr_type = bvr_string[0:2]
            if bvr_type == '01' and len(bvr_string) == 42:
                ## This BVr is the type of BVR in CHF
                # WE will call the function and Call
                

                bvr_struct =  self._construct_bvr_postal_in_chf(bvr_string)
                ## We will test if the BVR have an Adherent Number if not we 
                ## will make the search of the account base on
                ##his name non base on the BVR adherent number
                if (bvr_struct['bvrnumber'] == '000000'):
                    bvr_struct['domain'] = 'name'
                else:
                    bvr_struct['domain'] = 'bvr_adherent_num'
                ## We will set the currency , in this case it's allways CHF
                bvr_struct['currency'] = 'CHF'
            ##
            elif bvr_type == '01':
                ## This BVr is the type of BVR in CHF
                # WE will call the function and Call
                bvr_struct =  self._construct_bvr_in_chf(bvr_string)
                ## We will test if the BVR have an Adherent Number if not 
                ## we will make the search of the account base on
                ##his name non base on the BVR adherent number
                if (bvr_struct['bvrnumber'] == '000000'):
                    bvr_struct['domain'] = 'name'
                else:
                    bvr_struct['domain'] = 'bvr_adherent_num'
                ## We will set the currency , in this case it's allways CHF
                bvr_struct['currency'] = 'CHF'
            ##
            elif bvr_type == '03':
                ## It will be (At this time) the same work 
                ## as for a standard BVR with 01 code
                bvr_struct =  self._construct_bvr_postal_in_chf(bvr_string)
                ## We will test if the BVR have an Adherent Number 
                ## if not we will make the search of the account base on
                ##his name non base on the BVR adherent number
                if (bvr_struct['bvrnumber'] == '000000'):
                    bvr_struct['domain'] = 'name'
                else:
                    bvr_struct['domain'] = 'bvr_adherent_num'
                ## We will set the currency , in this case it's allways CHF
                bvr_struct['currency'] = 'CHF'
            ##
            elif bvr_type == '04':
                ## It the BVR postal in CHF
                bvr_struct =  self._construct_bvrplus_in_chf(bvr_string)
                ## We will test if the BVR have an Adherent Number
                ## if not we will make the search of the account base on
                ##his name non base on the BVR adherent number
                if (bvr_struct['bvrnumber'] == '000000'):
                    bvr_struct['domain'] = 'name'
                else:
                    bvr_struct['domain'] = 'bvr_adherent_num'
                ## We will set the currency , in this case it's allways CHF
                bvr_struct['currency'] = 'CHF'
            ##
            elif bvr_type == '21':
                ## It for a BVR in Euro
                bvr_struct =  self._construct_bvr_in_chf(bvr_string)
                ## We will test if the BVR have an Adherent Number if 
                ## not we will make the search of the account base on
                ##his name non base on the BVR adherent number
                if (bvr_struct['bvrnumber'] == '000000'):
                    bvr_struct['domain'] = 'name'
                else:
                    bvr_struct['domain'] = 'bvr_adherent_num'
                ## We will set the currency , in this case it's allways CHF
                bvr_struct['currency'] = 'EUR'
            ##
            elif bvr_type == '31':
                ## It the BVR postal in CHF
                bvr_struct =  self._construct_bvrplus_in_chf(bvr_string)
                ## We will test if the BVR have an Adherent Number if not 
                ## we will make the search of the account base on
                ##his name non base on the BVR adherent number
                if (bvr_struct['bvrnumber'] == '000000'):
                    bvr_struct['domain'] = 'name'
                else:
                    bvr_struct['domain'] = 'bvr_adherent_num'
                ## We will set the currency , in this case it's allways CHF
                bvr_struct['currency'] = 'EUR'

            elif bvr_type[0:1] == '<' and len(bvr_string) == 41:
                ## It the BVR postal in CHF
                
                bvr_struct =  self._construct_bvr_postal_other_in_chf(bvr_string)
                ## We will test if the BVR have an Adherent Number 
                ## if not we will make the search of the account base on
                ## his name non base on the BVR adherent number
                if (bvr_struct['bvrnumber'] == '000000'):
                    bvr_struct['domain'] = 'name'
                else:
                    bvr_struct['domain'] = 'bvr_adherent_num'
                ## We will set the currency , in this case it's allways CHF
                bvr_struct['currency'] = 'CHF'

            ##
            ##            
            else:
                raise wizard.except_wizard('BVR Type error', 
                    'This kind of BVR is not supported at this time')
            return bvr_struct

        
    def _validate_account(self, cr, uid, data, context):
        # BVR Standrard
        #0100003949753>120000000000234478943216899+ 010001628>
        # BVR without BVr Reference
        #0100000229509>000000013052001000111870316+ 010618955>
        # BVR + In CHF
        #042>904370000000000000007078109+ 010037882>
        # BVR In euro
        #2100000440001>961116900000006600000009284+ 030001625>
        #<060001000313795> 110880150449186+ 43435>
        #<010001000165865> 951050156515104+ 43435>
        #<010001000060190> 052550152684006+ 43435>
            pool = pooler.get_pool(cr.dbname)
            ##
            # Explode and check  the BVR Number and structurate it
            ##
            data['bvr_struct'] = self._get_bvr_structurated(
                                        data['form']['bvr_string']
                                    )
            ## We will now search the account linked with this BVR
            if data['bvr_struct']['domain'] == 'name':
                partner_bank_search = pool.get('res.partner.bank').search(
                    cr,
                    uid,
                    [('bvr_number', '=',data['bvr_struct']['beneficiaire'])]
                )
            else:
                partner_bank_search = pool.get('res.partner.bank').search(
                    cr,
                    uid,
                    [('bvr_adherent_num', '=',data['bvr_struct']['bvrnumber'])]
                )
            if partner_bank_search:
                    # we have found the account corresponding to the bvr_adhreent_number
                    # so we can directly create the account
                    # 
                partner_bank_result = pool.get('res.partner.bank').browse(
                                                        cr,
                                                        uid,
                                                        partner_bank_search[0]
                                                    )
                data['form']['Account_list'] = partner_bank_result.id
                return 'createdirectinvoice'
            else:
                # we haven't found a valid bvr_adherent_number
                # we will need to create or update 
                #
                FORM.string = '''<?xml version="1.0"?>
<form string="Need More informations">
    <separator string="Partner " colspan="4"/>
    <field name="Partner_list"/>
    <separator string="Partner Bank Account" colspan="4"/>
    <field name="Account_list"
    domain="[('partner_id', '=', Partner_list),('state', 'in', ['bvrbank','bvrpost'])]"/>
</form>''' 
                return 'createaccount'

 
    
    _transaction_add_fields = {
    'Partner_list': {
                        'string':'Partner', 
                        'type':'many2one', 
                        'relation':'res.partner', 
                        'required':True,
                        'help':"The supplier who send the invoice. \
If it is not set you have to create it"
                    },
    'Account_list': {
                        'string':'Partner Bank Account', 
                        'type':'many2one', 
                        'relation':'res.partner.bank', 
                        'required':True,
                        'help': "the bank account of the supplier. \
If it is not set you have to create it"
                    },
    'import_account_information': {'string':'Update Bvr Adherent number of this account with the one stored in the Bvr reference?', 'type':'boolean'},
    }

    _create_form = """<?xml version="1.0"?>
<form title="BVR Scanning">
    <separator string="Bvr Scanning Result" colspan="4"/>
    <field name="bvr_string" colspan="4"> </field>
    <separator string="Invoice Journal" colspan="4"/>
    <field name="invoice_journal"/>
</form>"""
    _create_fields = {
                        'bvr_string': {
                                        'string':'BVR String',
                                        'type':'char',
                                        'size':'128' ,
                                        'required':'true',
                                        'help':"The line at the bottom right \
of the BVR"
                                        },
                        'invoice_journal': {
                                            'string':'Journal', 
                                            'type':'many2one', 
                                            'relation':'account.journal', 
                                            'required':True
                                            },
                }
        
    states = {
                        'init' : {
                                'actions' : [], 
                                'result' : {
                                            'type':'form',
                                            'arch':_create_form, 
                                            'fields':_create_fields,
                                            'state': [
                                                    ('end','Cancel'),
                                                    ('create','Create invoice')
                                                    ]
                                            },
                        },
                         'create': {
                                'actions': [],
                                'result' : {
                                            'type': 'choice', 
                                            'next_state': _validate_account 
                                            }
                                },
                         'createaccount': {
                                 'actions': [],
                                 'result': {'type': 'form', 
                                            'arch':FORM, 
                                            'fields':_transaction_add_fields, 
                                            'state':[
                                                    ('end','Cancel'),
                                                    ('createdirectinvoice','Create invoice')
                                                    ]
                                            }              
                                },
                         'createdirectinvoice': {
                                'actions': [],
                                'result' : {
                                                'type': 'action', 
                                                'next_state': 'end',
                                                'action':_create_direct_invoice
                                            }
                                },
    }
scan_bvr('scan.bvr')