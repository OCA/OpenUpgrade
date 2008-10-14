# -*- encoding: utf-8 -*-
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

class cci_vcs_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(cci_vcs_report, self).__init__(cr, uid, name, context)
        self.localcontext.update( {
            'time': time,
            'find_vcs': self.find_vcs,
        })

    def find_vcs(self,ids={}):
        if not ids:
            ids = self.ids
        result=[]

        for item in pooler.get_pool(self.cr.dbname).get('account.invoice').browse(self.cr,self.uid,ids):

            res={}
            vcs1='0'+ str(item.date_invoice[2:4])
            vcs3=str(item.number).split('/')[1]

            if len(str(vcs3))>=5:
                vcs2=str(item.number[3]) + str(vcs3[0:5])
            elif len(str(vcs3))==4:
                vcs2=str(item.number[3]) + '0' +str(vcs3)
            else:
                vcs2=str(item.number[3]) + '00' +str(vcs3)

            vcs4= vcs1 + vcs2 + '0'

            vcs5=int(vcs4)
            check_digit=vcs5%97

            if check_digit==0:
                check_digit='97'
            if check_digit<=9:
                check_digit='0'+str(check_digit)

            res['inv_no']=item.number
            res['vcs']=vcs1+'/'+vcs2+'/'+ '0' +str(check_digit)

            result.append(res)
        return result

report_sxw.report_sxw('report.cci.vcs', 'account.invoice', 'addons/cci_account/report/cci_vcs_report.rml',parser=cci_vcs_report,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

