from osv import fields,osv
import tools
import ir
import pooler

class generalize_account_report(osv.osv):
    _name = "generalize.account.report"
    _description = "Generalize Account Report"
    
    def onchange_fiscal_year(self, cr, uid, ids, fis_year):
        val={}
        if fis_year:
            date_obj=self.pool.get('account.fiscalyear').browse(cr, uid, [fis_year])[0]
            val['st_date']=date_obj.date_start
            val['end_date']=date_obj.date_stop  
        return {'value': val}

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'final_type':fields.selection([
            ('pl','Profit & Loss Account'),
            ('bs','Balance sheet'),
            ],'Final Account Type', select=True,required=True),
        'type': fields.selection([
            ('horizontal','Horizontal'),
            ('vertical','Vertical'),
            ],'Report type', select=True,required=True),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'fiscal_year':fields.many2one('account.fiscalyear','Fiscal Year',required=True),
        'st_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'gr_detail':fields.one2many('group.detail.configuration','gdc_id','Documents'),
        'profit_tran_acc':fields.many2one('account.account','Profit Transfer Account'), 
        'Loss_tran_acc':fields.many2one('account.account','Loss Transfer Account'),
    }
    _defaults = {
                 'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
                 'fiscal_year':lambda self,cr,uid,c: self.pool.get('account.fiscalyear').find(cr, uid),
                 'final_type':lambda *a: 'pl',
                 'type':lambda *a:'horizontal'
                 }
    
    def to_horizontal(self,cr, uid, ids, context={}):
        change_dict1 ={}
        change_dict2 ={}
        req_l=self.read(cr,uid,ids,['type','gr_detail'])
        if req_l[0]['type'] == 'vertical':
            change_dict1['type'] = 'horizontal'
        self.write(cr,uid,[req_l[0]['id']],change_dict1)
        grd_pos_data = self.pool.get('group.detail.configuration').read(cr,uid,req_l[0]['gr_detail'],['pos_name'])
        for grd_pos in grd_pos_data:
            if grd_pos['pos_name'] == 'top':
                change_dict2['pos_name'] = 'left'
            if grd_pos['pos_name'] == 'bottom':
                change_dict2['pos_name'] = 'right'
            self.pool.get('group.detail.configuration').write(cr,uid,[grd_pos['id']],change_dict2)
        return True

    def to_vertical(self,cr, uid, ids, context={}):
        change_dict1 ={}
        change_dict2 ={}
        req_l=self.read(cr,uid,ids,['type','gr_detail'])
        if req_l[0]['type'] == 'horizontal':
            change_dict1['type'] = 'vertical'
        self.write(cr,uid,[req_l[0]['id']],change_dict1)
        grd_pos_data = self.pool.get('group.detail.configuration').read(cr,uid,req_l[0]['gr_detail'],['pos_name'])
        for grd_pos in grd_pos_data:
            if grd_pos['pos_name'] == 'left':
                change_dict2['pos_name'] = 'top'
            if grd_pos['pos_name'] == 'right':
                change_dict2['pos_name'] = 'bottom'
            self.pool.get('group.detail.configuration').write(cr,uid,[grd_pos['id']],change_dict2)
        return True

generalize_account_report()

class group_detail_configuration(osv.osv):
    _name = "group.detail.configuration"
    _description = "Group Configuration"

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'gdc_id':fields.many2one('generalize.account.report','Geralize Account'), 
        'acc_gr_name':fields.many2one('account.account','Account',required=True),
        'pos_name': fields.selection([
            ('left','Left'),
            ('right','Right'),
            ('top','Top'),
            ('bottom','Bottom'),
            ],'Position Name', select=True,required=True),
        'sequence': fields.integer('Sequence',required=True),
    }
    _sql_constraints = [
        ('name', 'UNIQUE(name)', 'The name must be unique!'),
    ]
    _order = 'sequence'
group_detail_configuration()   