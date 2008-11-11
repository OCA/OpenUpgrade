# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
import wizard
import datetime
error = '''<?xml version="1.0"?>
<form string="Select period">
    <label string="Error in Data !!"/>
</form>'''

info = '''<?xml version="1.0"?>
<form string="Select period">
    <label string="Bank Account no!!"/>
</form>'''

form1 = '''<?xml version="1.0"?>
<form string="Select period">
            <separator string="Employees" colspan="4" />
            <field name="emp_ids" colspan="2" nolabel="1"/>
            <newline/>
            <field name="active1"/>
            <newline/>
            <group col="4" colspan="4">
            <field name="month"/>
            <field name="year"/>
            </group>
            <newline/>
            <field name="active2"/>
            <newline/>
            <group col="4" colspan="4">
            <field name="fromdate"/>
            <field name="todate"/>
            </group>
</form>'''
def _get_months(sel, cr, uid, context):
    i=0
    res=[]
    while i<12:
        t=()
        t=(i+1,i+1)
        res.append(t)
        i+=1
    return res
field1 = {
    'emp_ids': {'string':'Employees', 'type':'many2many', 'relation':'hr.employee'},
    'month': {'string':'Month','type':'selection', 'selection':_get_months},
    'year':{'string':'Year','type':'integer'},
    'fromdate': {'string':'From', 'type':'date'},
    'todate': {'string':'To', 'type':'date'},
    'active1':{'string':'Month Wise','type':'boolean'},
    'active2':{'string':'Date Wise','type':'boolean'}
}


class hr_holidays_report(wizard.interface):
    def year_get(self, cr, uid, data, context):
       p=int(time.strftime('%Y'))
       return {'year':p}
    def _riase_error(self, cr, uid, data, context):
        form=data['form']
        if not form['emp_ids'][0][2] :
            raise wizard.except_wizard('Error', 'You must select Employee(s) For report !')
        
        if form['active1'] and form['active2']:
            raise wizard.except_wizard('TyepError', 'You must select only one type For report !')
        if form['active1']:
            temp=form['year']
            if not form['month']:
                raise wizard.except_wizard('MonthError', 'You must select month For month-wise report !')
            
                
        elif form['active2']:
            temp=0
            if not form['fromdate'] or not form['todate']:
                raise wizard.except_wizard('DateError', 'You must select Dates For date-wise report !')
            else:
                d=form['fromdate']
                dd=form['todate']
                d1=d.split('-')
                d2=dd.split('-')
                d1[2]=d1[2].split(' ')
                d2[2]=d2[2].split(' ')
                a=datetime.date(int(d1[0]),int(d1[1]),int(d1[2][0]))
                b=datetime.date(int(d2[0]),int(d2[1]),int(d2[2][0]))
                if  a>b :
                    raise wizard.except_wizard('DateError', 'You must select Dates proparly !')
        else:
            raise wizard.except_wizard('typeError', 'You must select Type !')
        return {'year':temp}
    states = {
        'init': {
            'actions': [year_get],
            'result': {'type':'form', 'arch':form1, 'fields':field1,  'state' : [('print', 'Ok'),('end', 'Cancel')]}
        },
         'print': {
            'actions': [_riase_error],
            'result': {'type':'print', 'report':'hr.holiday.req.report','state':'end'}
        }
        
    }
hr_holidays_report('hr_holiday_req')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

