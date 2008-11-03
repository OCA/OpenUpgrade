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


import pooler
import time
from report import report_sxw

class huissier_attestation(report_sxw.rml_parse):
    def _get_obj(self, data):
        print data
        return self.pool.get('huissier.lots').browse(self.cr, self.uid, data['form']['attest_ids'])
    def __init__(self, cr, uid, name, context):
        super(huissier_attestation, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            '_get_obj': self._get_obj
        })
report_sxw.report_sxw('report.huissier.lots_attestation', 'huissier.lots', 'addons/huissier/report/attestation.rml',parser=huissier_attestation, header= False)

report_sxw.report_sxw('report.huissier.lots_attestation2', 'huissier.lots', 'addons/huissier/report/attestation2.rml',parser=huissier_attestation, header= False)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

