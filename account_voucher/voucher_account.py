import time
import netsvc
from osv import fields, osv
import ir
import pooler
import mx.DateTime
from mx.DateTime import RelativeDateTime
from tools import config


class Account(osv.osv):
    _inherit = "account.account"

#    def _diff(self, cr, uid, ids, field_name, arg, context={}):
#
#        res={}
#        dr_total=0.0
#        cr_total=0.0
#        difference=0.0
#        for id in ids:
#            open=self.browse(cr, uid, id, context)
#            if open.type1 == 'dr':
#                dr_total+=open.open_bal
#            elif open.type1 == 'cr':
#                cr_total+=open.open_bal
#            else:
#                difference=0.0
#        difference=dr_total-cr_total
#        for id in ids:
#            res[id]=difference
#        return res
    
    def _get_level(self, cr, uid, ids, field_name, arg, context={}):
        res={}
        acc_obj=self.browse(cr,uid,ids)
        for aobj in acc_obj:
            level = 0
            if aobj.parent_id :
                obj=self.browse(cr,uid,aobj.parent_id.id)
                level= obj.level + 1
            res[aobj.id] = level
        return res
    
    _columns = {

        'journal_id':fields.many2one('account.journal', 'Journal',domain=[('type','=','situation')]),
        'open_bal' : fields.float('Opening Balance',digits=(16,2)),
#        'diff' : fields.function(_diff, digits=(16,2),method=True,string='Difference of Opening Bal.'),
        'level': fields.function(_get_level, string='Level', method=True, store=True, type='integer'),
        'type1':fields.selection([('dr','Debit'),('cr','Credit'),('none','None')], 'Dr/Cr',store=True),

    }
    
    def compute_total(self, cr, uid, ids, yr_st_date, yr_end_date, st_date, end_date, field_names, context={}, query=''):
        #compute the balance/debit/credit accordingly to the value of field_name for the given account ids
        mapping = {
            'credit': "COALESCE(SUM(l.credit), 0) as credit ",
            'balance': "COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance ",
            'debit': "COALESCE(SUM(l.debit), 0) as debit ",
        }
        #get all the necessary accounts
        ids2 = self._get_children_and_consol(cr, uid, ids, context)
        acc_set = ",".join(map(str, ids2))
        #compute for each account the balance/debit/credit from the move lines
        if not (st_date >= yr_st_date and end_date <= yr_end_date):
            return {}
        accounts = {}
        if ids2:
            query = self.pool.get('account.move.line')._query_get(cr, uid,
                    context=context)
            cr.execute("SELECT l.account_id as id, "  \
                    +  ' , '.join(map(lambda x: mapping[x], field_names.keys() ))  + \
                    "FROM account_move_line l " \
                    "WHERE l.account_id IN ("+ acc_set +") " \
                        "AND " + query + " " \
                        " AND l.date >= "+"'"+ st_date +"'"+" AND l.date <= "+"'"+ end_date +""+"'"" " \
                    "GROUP BY l.account_id ")
            for res in cr.dictfetchall():
                accounts[res['id']] = res
        #for the asked accounts, get from the dictionnary 'accounts' the value of it
        res = {}
        for id in ids:
            res[id] = self._get_account_values(cr, uid, id, accounts, field_names, context)
        return res

    def create(self, cr, uid, vals, context={}):
        name=self.search(cr,uid,[('name','ilike',vals['name']),('company_id','=',vals['name'])])
        if name:
            raise osv.except_osv('Error', 'Account is Already Created !')
        #if vals.has_key('parent_id'):
         #   vals['code']=self.account_code_gen(cr, uid, vals['parent_id'],vals['name'])
        obj=self.pool.get('account.account.type').browse(cr,uid,vals['user_type'])
        if obj.code in ('cash','asset','expense'):
            vals['type1'] = 'dr'
        elif obj.code in ('equity','income','liability') : 
             vals['type1'] = 'cr'
        else:
             vals['type1'] = 'none'
        #vals = self.get_level(vals)
        account_id = super(Account, self).create(cr, uid, vals, context)
        if vals.get('type1', False) != False:
            journal_id = vals.get('journal_id',False)
            if journal_id:
                journal = self.pool.get('account.journal').browse(cr, uid, [journal_id])
                if journal and journal[0].sequence_id:
                    name = self.pool.get('ir.sequence').get_id(cr, uid, journal[0].sequence_id.id)
                move=self.pool.get('account.move').search(cr,uid,[('journal_id','=',journal_id)])
                if not move:
                    move = False
                    move_data = {'name': name, 'journal_id': journal_id}
                    move_id=self.pool.get('account.move').create(cr,uid,move_data)
                    move_obj=self.pool.get('account.move').browse(cr,uid,move_id)
                else:
                    move_obj=self.pool.get('account.move').browse(cr,uid,move[0])
                self_obj=self.browse(cr,uid,account_id)
                move_line = {
                     'name':journal[0].name,
                     'debit':self_obj.debit or False,
                     'credit':self_obj.credit or False,
                     'account_id':account_id or False,
                     'move_id':move and move[0] or move_id,
                     'journal_id':journal_id ,
                     'period_id':move_obj.period_id.id,
             }
                if vals['type1'] == 'dr':
                    move_line['debit'] = vals['open_bal'] or False
                elif vals['type1'] == 'cr':
                    move_line['credit'] = vals['open_bal'] or False
                self.pool.get('account.move.line').create(cr,uid,move_line)
        return account_id

    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        res_temp={}
#        if (vals.has_key('parent_id') and vals['parent_id'] != [[6, 0, []]]) or vals.has_key('name') :
#            id=self.browse(cr,uid,ids)
#            if id[0].parent_id or id[0].name:
#                if not vals.has_key('name') : 
#                    res_temp['name']=id[0].name
#                    res_temp['parent_id']=vals['parent_id']
#                if not vals.has_key('parent_id'):
#                    res_temp['parent_id']=[[0,6,[id[0].parent_id[0].id]]]
#                    res_temp['name']=vals['name']
#            vals['code']=self.account_code_gen(cr, uid, res_temp['parent_id'],res_temp['name'])
        if vals.has_key('name'):
            name=self.search(cr,uid,[('name','ilike',vals['name']),('company_id','=',vals['company_id'])])
            if name:
                raise osv.except_osv('Error', 'Same Account Name is Already present !')
        if vals.has_key('user_type'):
            obj=self.pool.get('account.account.type').browse(cr,uid,vals['user_type'])
            if obj.code in ('cash','asset','expense'):
                vals['type1'] = 'dr'
            elif obj.code in ('equity','income','liability') : 
                 vals['type1'] = 'cr'
            else:
                 vals['type1'] = 'none'
#        if vals.has_key('parent_id'):
#            vals = self.get_level(vals)
        super(Account, self).write(cr, uid,ids, vals, context)
        self_obj= self.browse(cr,uid,ids)
        move_pool=self.pool.get('account.move')
        if vals:
            for obj in self_obj:
                flg=0
                if obj.journal_id and obj.journal_id.type == 'situation':
                    move=move_pool.search(cr,uid,[('journal_id','=',obj.journal_id.id)])
                    if move:
                        move_obj=move_pool.browse(cr,uid,move[0])
                        move=move[0]
                    else:
                        name = self.pool.get('ir.sequence').get_id(cr, uid, obj.journal_id.sequence_id.id)
                        move_data = {'name': name, 'journal_id': obj.journal_id.id}
                        move=self.pool.get('account.move').create(cr,uid,move_data)
                        move_obj=move_pool.browse(cr,uid,move)
                    move_line_data={'name':obj.journal_id.name,
                                           'debit':obj.debit or False,
                                           'credit':obj.credit or False,
                                           'account_id':obj.id,
                                           'move_id':move,
                                           'journal_id':obj.journal_id.id,
                                           'period_id':move_obj.period_id.id,
                                           }
                    if obj.type1:
                        if obj.type1 == 'dr':
                            move_line_data['debit'] = obj.open_bal
                        elif obj.type1 == 'cr':
                            move_line_data['credit'] = obj.open_bal
                    if move_obj and move:
                        for move_line in move_obj.line_id:
                            if move_line.account_id.id == obj.id:
                                self.pool.get('account.move.line').write(cr,uid,[move_line.id],move_line_data)
                                flg=1
                        if not flg:
                            self.pool.get('account.move.line').create(cr,uid,move_line_data)
        return True

    def onchange_type(self, cr, uid, ids,user_type,type1):
        if not type:
            return {'value' : {}}
        type_obj=self.pool.get('account.account.type').browse(cr,uid,user_type)
        if type_obj.code in ('receivable','cash','asset','expense'):
            type1 = 'dr'
        elif type_obj.code in ('payable','equity','income','tax','liability') :
            type1 = 'cr'
        else:
            type1 = 'none'

        return {
            'value' : {'type1' : type1}
    }

#    def account_code_gen(self,cr, uid, parent_id, name):
#        account = self.pool.get('account.account')
#        name1=name.split(" ")
#        if len(name1) > 1:
#            name2=name1[0][0] + name1[1][0]
#        else:
#            name2=name1[0][0]
#        if parent_id == [[6, 0, []]] :
#            return False
#        else:
#            id=parent_id[0][2][0] 
#            parent_code = account.read(cr, uid, [id], ['code'])[0]['code']
#            acccode = str(parent_code) + "/" + name2
#            acccode = acccode.upper()
#            return acccode                   

Account()


class AccountMove(osv.osv):
    _inherit = "account.move"
    _columns = {
        'name':fields.char('Name', size=256, required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'voucher_type': fields.selection([
            ('pay_voucher','Cash Payment Voucher'),
            ('bank_pay_voucher','Bank Payment Voucher'),
            ('rec_voucher','Cash Receipt Voucher'),
            ('bank_rec_voucher','Bank Receipt Voucher'),
            ('cont_voucher','Contra Voucher'),
            ('journal_sale_vou','Journal Sale Voucher'),
            ('journal_pur_voucher','Journal Purchase Voucher'),
            ('journal_voucher','Journal Voucher'),
            ],'Voucher Type', readonly=True, select=True, states={'draft':[('readonly',False)]})
    }

AccountMove()

class res_currency(osv.osv):
    _inherit = "res.currency"

    _columns = {
                'sub_name': fields.char('Sub Currency', size=32, required=True)

            }
    _defaults = {
        'sub_name': lambda *a: 'cents',

    }
res_currency()

class account_account_template(osv.osv):
        _inherit = "account.account.template"
        
        _columns = {
        'type1':fields.selection([('dr','Debit'),('cr','Credit'),('none','None')], 'Dr/Cr',store=True),
    }

account_account_template()


