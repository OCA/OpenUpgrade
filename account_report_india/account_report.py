import time
import mx.DateTime
import netsvc
from osv import fields, osv


class account_detail(osv.osv):
    _name = "account.detail"
    _description = "Account Calculation"
    
    _columns = {
    'name': fields.char('Name', size=128, required=True, translate=True, select=True), 
    'type': fields.char('Type', size=128, required=True),
    'company_id': fields.many2one('res.company', 'Company', required=True),
    'level':fields.integer('Level', required=True),
    'debit'  : fields.float('Debit', digits=(16,2)),    
    'credit'  : fields.float('Credit', digits=(16,2)),           
    'balance'  : fields.float('Balance', digits=(16,2)),
    }
    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }
  
account_detail()


class account_report_india(osv.osv):
    _name = "account.report.india"
    _description = "Account Report"
    
    def sum_bal(self,line,year_start_date,year_end_date,st_date,end_date):
        debit=0.0
        credit=0.0
        balance=0.0
        if st_date >= year_start_date and end_date <= year_end_date:
            for l in line:
                if l.date >= st_date and l.date <= end_date:
                    debit += l.debit
                    credit += l.credit
            balance = debit - credit
        return balance
    
    def get_child(self,cr,uid,child_obj):
        child_ids = self.pool.get('account.account').search(cr, uid,[('parent_id','child_of',[child_obj.id])])
        child_objs=self.pool.get('account.account').browse(cr, uid, child_ids)
        child_objs.remove(child_obj)
        return child_objs
    
    def get_child_detail(self,cr,uid,st_date,end_date,acc_child,year_start_date,year_end_date):
        res1={}
        total_balance=0.0
        for acc_c in acc_child:
            res1={}
            move_id = self.pool.get('account.move.line').search(cr, uid, [('account_id','=', acc_c.id)])
            move = self.pool.get('account.move.line').browse(cr, uid, move_id)
            balance=self.sum_bal(move,year_start_date,year_end_date,st_date,end_date)
            total_balance += balance
        res1['balance']= total_balance
        return res1

    def get_cal(self,cr,uid,st_date,end_date,year_start_date,year_end_date):
        type_list=['expense','income']
        gp_list_group=['Opening Stock','Purchase','Direct Expenses','Sales Account','Goods Given Account']
        gp_total=0.0
        np_total=0.0
        res={}
        total_list=['Opening Stock','Purchase','Direct Expenses','Indirect Expenses','Sales Account','Goods Given Account','Direct Incomes','Indirect Incomes']
        acc_id=self.pool.get('account.account').search(cr, uid, [('name','in', total_list)])
        list_obj=self.pool.get('account.account').browse(cr, uid, acc_id)
        for aobj in list_obj:
            total_bal=0.0
            if aobj.type in type_list:
                res={}
                move_id = self.pool.get('account.move.line').search(cr, uid, [('account_id','=', aobj.id)])
                move = self.pool.get('account.move.line').browse(cr, uid, move_id)
                balance=self.sum_bal(move,year_start_date,year_end_date,st_date,end_date)
                acc_child=self.get_child(cr,uid,aobj)
                if acc_child== []:
                    if aobj.name in gp_list_group:
                        gp_total += balance
                    if aobj.name in total_list:
                        np_total += balance
                else:
                    result_temp=self.get_child_detail(cr,uid,st_date,end_date,acc_child,year_start_date,year_end_date)
                    total_bal += result_temp['balance']
                    if aobj.name in gp_list_group:
                        gp_total += total_bal
                    if aobj.name in total_list:
                        np_total += total_bal
            else:
                gp_total=0.0
                np_total=0.0
        res['gp']= gp_total
        res['np']= np_total 
        return res
    
    def _get_fiscal_year(self, cr, uid, context={}):
        return self.pool.get('account.fiscalyear').find(cr,uid)
    
    def _get_start_date(self, cr, uid, context={}):
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscal_year = fiscalyear_obj.find(cr, uid)
        year_start_date = fiscalyear_obj.browse(cr, uid, fiscal_year ).date_start
        return mx.DateTime.strptime(year_start_date,"%Y-%m-%d").strftime("%Y-%m-%d")
    
    def _get_end_date(self, cr, uid, context={}):
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscal_year = fiscalyear_obj.find(cr, uid)
        year_end_date = fiscalyear_obj.browse(cr, uid, fiscal_year ).date_stop
        return mx.DateTime.strptime(year_end_date,"%Y-%m-%d").strftime("%Y-%m-%d")
    
    def dict_account_detail(self,line,year_start_date,year_end_date,st_date,end_date):
        res={}
        debit=0.0
        credit=0.0
        balance=0.0
        if st_date >= year_start_date and end_date <= year_end_date:
            for l in line:
                if l.date >= st_date and l.date <= end_date:
                    debit += l.debit
                    credit += l.credit
            balance = debit - credit
        res['debit']=debit
        res['credit']=credit
        res['balance']=balance
        return res
    
    def get_child_list(self,cr,uid,vals,acc_child,year_start_date,year_end_date):
        result=[]
        for acc_c in acc_child:
            res1={}
            res1['name']=acc_c.name
            res1['type']=acc_c.user_type.code
            move_id = self.pool.get('account.move.line').search(cr, uid, [('account_id','=', acc_c.id)])
            move = self.pool.get('account.move.line').browse(cr, uid, move_id)
            list_acc_child=self.dict_account_detail(move,year_start_date,year_end_date,vals['start_date'],vals['end_date'])
            res1['debit']=list_acc_child['debit']
            res1['credit']=list_acc_child['credit']
            res1['balance']=list_acc_child['balance']
            res1['level']=1
            if acc_c.parent_id:
                for r in result:
                    if r['name']== acc_c.parent_id.name:
                        res1['level'] = r['level'] + 1
                        break
            result.append(res1)
        return result

    def get_account_detail(self,cr, uid,vals):
        result1=[]
        if vals['group_type'] == 'pl_accounts_group':
            gr_list=['expense','income']
        else:
            gr_list=['liability','asset']
        for group in gr_list:
            result=[]
            result_temp=[]
            result_temp1=[]
            final_result={}
            res={}
            acc_ids=[]
            if group=='expense':
                list_acc=['Opening Stock','Purchase','Direct Expenses','Indirect Expenses']
            if group=='income':
                list_acc=['Sales Account','Goods Given Account','Direct Incomes','Indirect Incomes']
            if group=='liability':
                list_acc=['Share Holder/Owner Fund','Loan(Liability) Account','Current Liabilities','Suspense Account']
            if group=='asset':
                list_acc=['Fixed Assets','Investment','Current Assets','Misc. Expenses(Asset)']
            for lacc in list_acc:
                acc_ids +=self.pool.get('account.account').search(cr, uid, [('name','=', lacc)])
            acc_objs=self.pool.get('account.account').browse( cr,  uid, acc_ids)
            fiscalyear_obj =  self.pool.get('account.fiscalyear')
            date_obj=fiscalyear_obj.browse(cr, uid, vals['fiscal_year'])
            year_start_date = date_obj.date_start
            year_end_date = date_obj.date_stop  
            for aobj in acc_objs:
                res={}
                total_bal=0.0
                total_bal1=0.0
                res['name']=aobj.name
                res['type']=aobj.user_type.code
                move_id = self.pool.get('account.move.line').search(cr, uid, [('account_id','=', aobj.id)])
                move = self.pool.get('account.move.line').browse(cr, uid, move_id)
                list_res=self.dict_account_detail(move,year_start_date,year_end_date,vals['start_date'],vals['end_date'])
                res['level']=0
                res['debit']=list_res['debit']
                res['credit']=list_res['credit']
                acc_child=self.get_child(cr,uid,aobj)
                if acc_child== []:
                    res['balance']=list_res['balance']
                    result.append(res)
                else:
                    result_temp=self.get_child_list(cr,uid,vals,acc_child,year_start_date,year_end_date)
                    result_temp1=result_temp
                    pos={}
                    res['balance']=0.0
                    for rt in result_temp:
                        if rt['level'] == 1:
                            total_bal1=0.0
                            pos=rt
                            total_bal += rt['balance']
                        if rt['level'] > 1:
                            total_bal1 += rt['balance']
                            if pos in result_temp1:
                                d=result_temp1.index(pos)
                                result_temp1[d]['balance'] = total_bal1
                                total_bal += result_temp1[d]['balance']
                    res['balance']=total_bal
                    result.append(res)
                    result += result_temp1
            final_result['gr_name']=group
            final_result['list']=result
            result1.append(final_result)
        return result1
    
    def create(self, cr, uid, vals, context={}):
        res={}
        res_list=[]
        total_list=[]
        list_ids=[]
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        date_obj=fiscalyear_obj.browse(cr, uid, vals['fiscal_year'])
        year_start_date = date_obj.date_start
        year_end_date = date_obj.date_stop  
        group_list=self.get_account_detail(cr, uid,vals)
        for g in group_list:
            total_list += g['list']
        if vals['group_type']== 'pl_accounts_group':
            cr.execute('delete from account_detail where type = %s or type = %s',('expense','income'))
        else:
            cr.execute('delete from account_detail where type = %s or type = %s',('liability','asset'))
        for t in total_list:
            t['company_id']=vals['company_id']
            id_ad=self.pool.get('account.detail').create(cr, uid, t)
            list_ids.append(id_ad)
        vals['acc_detail']=[[ 6, 0, list_ids]]
        result_dict=self.get_cal(cr,uid,vals['start_date'],vals['end_date'],year_start_date,year_end_date)
        vals['gp_cal']=result_dict['gp']*-1
        vals['np_cal']=result_dict['np']*-1
        ret_id=super(account_report_india, self).create(cr, uid, vals, context)
        for ids in list_ids:
            cr.execute('insert into account_detail_rel (acc_id, accountid) values (%d, %d)',(int(ret_id),int(ids)))
        return ret_id
    
    def write(self, cr, uid, ids, vals, context=None):
        if vals.has_key('group_type') or vals.has_key('fiscal_year') or vals.has_key('start_date') or vals.has_key('end_date'):
            total_list=[]
            list_ids=[]
            obj=self.pool.get('account.report.india').browse(cr,uid,ids)
            vals['accid']=obj[0].id
            if not vals.has_key('group_type'):
                vals['group_type']=obj[0].group_type
            if not vals.has_key('fiscal_year'):
                vals['fiscal_year']=obj[0].fiscal_year.id
            if not vals.has_key('start_date'):
                vals['start_date']=obj[0].start_date
            if not vals.has_key('end_date'):
                vals['end_date']=obj[0].end_date
            cr.execute('delete from account_detail_rel where acc_id = '+str(obj[0].id)+'')
            res={}
            res_list=[]
            fiscalyear_obj = self.pool.get('account.fiscalyear')
            date_obj=fiscalyear_obj.browse(cr, uid, vals['fiscal_year'])
            year_start_date = date_obj.date_start
            year_end_date = date_obj.date_stop  
            group_list=self.get_account_detail(cr, uid,vals)
            for g in group_list:
                total_list += g['list']
            for t in total_list:
                t['company_id']=vals['company_id']
                id_ad=self.pool.get('account.detail').create(cr, uid, t)
                list_ids.append(id_ad)
            vals['acc_detail']=[[ 6, 0, list_ids]]
            result_dict=self.get_cal(cr,uid,vals['start_date'],vals['end_date'],year_start_date,year_end_date)
            vals['gp_cal']=result_dict['gp']*-1
            vals['np_cal']=vals['gp_cal'] + (result_dict['np']*-1)
            ret_id=super(account_report_india, self).write(cr, uid, ids, vals, context=context)
            for ids in list_ids:
                cr.execute('insert into account_detail_rel (acc_id, accountid) values (%d, %d)',(vals['accid'],ids))
        else:
            ret_id=super(account_report_india, self).write(cr, uid, ids, vals, context=context)
        return ret_id

    def onchange_fiscal_year(self, cr, uid, ids, fiscal_year):
        res={}
        if fiscal_year:
            fiscalyear_obj = self.pool.get('account.fiscalyear')
            fobj=fiscalyear_obj.browse(cr, uid, fiscal_year)
            year_start_date = fobj.date_start
            year_end_date = fobj.date_stop  
            res['start_date']=mx.DateTime.strptime(year_start_date,"%Y-%m-%d").strftime("%Y-%m-%d")
            res['end_date']=mx.DateTime.strptime(year_end_date,"%Y-%m-%d").strftime("%Y-%m-%d")
        return { 'value' : res }
    
    _columns = {
        'group_type': fields.selection([
            ('pl_accounts_group','PL_Accounts_Group'),
            ('balance_sheet_accounts_group','Balance_Sheet_Accounts_Group'),
            ],'Group_Type' , size=128),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'acc_detail':fields.many2many('account.detail','account_detail_rel', 'acc_id', 'accountid', 'Accounts Detail'),
        'fiscal_year': fields.many2one('account.fiscalyear','Fiscal Year'),
        'start_date': fields.date('Start Date', required=True),
        'end_date'  : fields.date('End Date', required=True),
        'gp_cal'  : fields.float('Gross Profit (+)/Loss (-)', digits=(16,2)),
        'np_cal'  : fields.float('Net Profit (+)/Loss (-)', digits=(16,2)),
    
    }
    
    _defaults = {
        'group_type': lambda *a: 'pl_accounts_group',
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
        'fiscal_year': _get_fiscal_year,
        'start_date':  _get_start_date,
        'end_date':  _get_end_date,
    }


account_report_india()

