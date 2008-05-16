##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting FROM its eventual inadequacies AND bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees AND support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it AND/or
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

import pooler
import time
from report import report_sxw

class cci_crossovered_analytic(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(cci_crossovered_analytic, self).__init__(cr, uid, name, context)
        self.localcontext.update( {
            'time': time,
            'lines': self._lines,
        })



    def _lines(self,form,ids={}):
        if not ids:
            ids = self.ids

        acc_id=[]
        final=[]
        journal=form['journal']
        acc_pool = self.pool.get('account.analytic.account')
        line_pool=self.pool.get('account.analytic.line')

        dict_acc_ref={}
        if form['journal']:
            journal=" in (" + str(form['journal']) + ")"
        else:
            journal= 'is not null'

        query_general="select id from account_analytic_line where (journal_id " + journal +") AND date>='"+ str(form['date1']) +"'"" AND date<='" + str(form['date2']) + "'"

        self.cr.execute(query_general)
        l_ids=self.cr.fetchall()
        line_ids=[x[0] for x in l_ids]

        obj_line=line_pool.browse(self.cr,self.uid,line_ids)

        for obj in obj_line:
            dict_acc_ref[obj.account_id.id]=[]

        for obj in obj_line:
            for id in dict_acc_ref:
                if obj.account_id.id==id:
                    dict_acc_ref[id].append(obj.move_id.id)

        # adding parent entries in dict_acc_ref
        done_ids=[]
        for obj in obj_line:
            if obj.account_id.id in done_ids:
                continue
            done_ids.append(obj.account_id.id)
            if (obj.account_id.parent_id) and (obj.account_id.parent_id.id in dict_acc_ref):
                dict_acc_ref[obj.account_id.parent_id.id] +=dict_acc_ref[obj.account_id.id]

        # distinct entries for lists
        for entry in dict_acc_ref:
           dict_acc_ref[entry] = list(set([x for x in dict_acc_ref[entry]]))

        obj_acc=acc_pool.browse(self.cr,self.uid,form['ref'])
        child_ids=[]
        self.list_ids=[]
        self.final_list=[]

        def find_children(ref_id):

            for id in ref_id:
                child_ids=acc_pool.search(self.cr,self.uid,[('parent_id','=',id)])
                self.final_list +=child_ids
                if child_ids:
                    self.list_ids=find_children(child_ids)
            return self.final_list

        child_ids=find_children(ids)

        self.final_list=child_ids + ids

        selected_ids=line_pool.search(self.cr,self.uid,[('account_id','in',self.final_list),('move_id','in',dict_acc_ref[form['ref']])])
        query="SELECT sum(aal.amount) AS amt, sum(aal.unit_amount) AS qty,aaa.name as acc_name,aal.account_id as id  FROM account_analytic_line AS aal, account_analytic_account AS aaa \
            WHERE aal.account_id=aaa.id AND aal.id IN ("+','.join(map(str,selected_ids))+")  GROUP BY aal.account_id,aaa.name ORDER BY aal.account_id"

        self.cr.execute(query)
        res = self.cr.dictfetchall()

        for item in res:
            obj_acc=acc_pool.browse(self.cr,self.uid,item['id']).parent_id
            if obj_acc:
                item['acc_name']=obj_acc.name + '/' + item['acc_name']
            final.append(item)
        return final

report_sxw.report_sxw('report.account.analytic.account.crossovered.analytic', 'account.analytic.account', 'addons/cci_account/report/cci_crossovered_analytic.rml',parser=cci_crossovered_analytic, header=False)

