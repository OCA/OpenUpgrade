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

from report.interface import report_rml
import pooler
class huissier_labels(report_rml):
    def create(self,cr, uid, ids, datas, context):
        pool = pooler.get_pool(cr.dbname)
        new_ids = pool.get('huissier.vignettes').search(cr, uid, [('first','<=',datas['form']['stop']),('last','>=', datas['form']['start'] )])
#       file('/tmp/terp.xml','wb+').write(xml)
        if not new_ids:
            raise Exception, "Il n'y a pas de vignettes entre ces deux chiffres!"
        return report_rml.create(self, cr,uid, new_ids, datas, context)

huissier_labels('report.huissier.labels.reprint', 'huissier.vignettes', 'addons/huissier/report/labels.xml', 'addons/huissier/report/labels.xsl')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

