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
class report_custom(report_rml):
    def create(self,cr, uid, ids, datas, context):
        # select all ranges which contain some labels in the (start, stop) range
        vignette_id=ids[0]
        vignettes_obj = pooler.get_pool(cr.dbname).get('huissier.vignettes')
        vign=vignettes_obj.browse(cr,uid,vignette_id)
        start=vign.first or 0.0
        stop=vign.last or 0.0

        new_ids = vignettes_obj.search(cr, uid, [('first','<=',stop),('last','>=', start )])
        
#       file('/tmp/terp.xml','wb+').write(xml)

        return report_rml.create(self,cr, uid, new_ids, datas, context)
report_custom('report.huissier.labels.print', 'huissier.vignettes', 'addons/huissier/report/labels.xml', 'addons/huissier/report/labels.xsl')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

