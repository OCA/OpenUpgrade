# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2009 P. Christeas. All Rights Reserved
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

from osv import fields, osv
from report_engine import posprint_report
import netsvc

class report_postxt(osv.osv):
    # no.. _inherit = "ir.actions.report.custom"
    _name = 'ir.actions.report.postxt'
    _columns = {
        'name': fields.char('Report Name', size=64, required=True, translate=True),
        'type': fields.char('Report Type', size=32, required=True),
        'model':fields.char('Object', size=64, required=True),
        'usage': fields.char('Action Usage', size=32),
	'code': fields.char('Code', size=32, help="This code is used so that modules can lookup some specific report"),
        'multi': fields.boolean('On multiple doc.', help="If set to true, the action will not be displayed on the right toolbar of a form view."),
        'groups_id': fields.many2many('res.groups', 'res_groups_report_rel', 'uid', 'gid', 'Groups'),
	'printer': fields.char('Printer', size=50, help="Preferred printer for this report. Useful for server-side printing."),
	'copies': fields.integer('Copies', help="Default number of copies."),
	'soft_copies': fields.boolean('Soft copies', help="If set to true, copies will be done through the\"num_copies\" variable of the content. Else, by the printing system."),
	'txt_content': fields.text('Content of report in text'),
        }
    
    _defaults = {
        'multi': lambda *a: False,
        'type': lambda *a: 'ir.actions.report.postxt',
	'copies': lambda  *a: 1,
	'soft_copies': lambda *a: False
    }
    
    def pprint(self, cr,uid, report , data, context):
	"""This should print the report using the dictionary in data
	"""
	import tempfile
	import os

	logger = netsvc.Logger()
	copies=report['copies']
	if not copies:
		copies=1
	if report['soft_copies']:
		data['num_copies']=copies
	str_report= self._do_report(report['txt_content'],data)
	if (report['printer']):
		logger.notifyChannel("pos_print", netsvc.LOG_INFO, 'Trying to print %s on %s ref. ' % \
			(report['name'],report['printer']))
		try:
			import cups
		except:
			raise Exception(_('Cannot talk to cups, please install pycups'))
		ccon = cups.Connection()
		(fileno, fp_name) = tempfile.mkstemp('.raw', 'openerp_')
		fp = file(fp_name, 'wb+')
		#fp.write(content.encode('iso8859-7'))
		fp.write(str_report)
		fp.close()
		os.close(fileno)
		if report['soft_copies']:
			copies=1
		job = ccon.printFile(report['printer'],fp_name,"Openerp: "+report['name'],{'copies': str(copies), 'raw': 'raw'})
		os.unlink(fp_name)
		if job:
			logger.notifyChannel("pos_print", netsvc.LOG_INFO, 'Created job %d'% job)
			return True
		else:
			raise Exception(_('Cannot print at printer %s')%report['printer'])
			return False
	else:
		print "Report:\n",str_report ,"\n\n"

    
    def _do_report(self, report, pdict):
	return posprint_report(report,pdict)



report_postxt()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: