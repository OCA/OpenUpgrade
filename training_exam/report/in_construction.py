# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
from report import report_sxw

class training_planned_exam_confirm_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(training_planned_exam_confirm_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.report.training.planned_exam.report',
                      'training.planned_exam',
                      'addons/training_exam/report/training_exam_confirm.rml',
                      parser=training_planned_exam_confirm_report,
                      header=True)

class training_planned_exam_cancel_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(training_planned_exam_cancel_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.training.planned_exam.cancel',
                      'training.planned_exam',
                      'addons/training_exam/report/training_exam_cancel.rml',
                      parser=training_planned_exam_cancel_report,
                      header=True)
class in_construction(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(in_construction, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })
#
#reports = [
#    ('report.training.planned_exam.cancel', 'training.planned_exam'),
#]
#
#for name, model in reports:
#    report_sxw.report_sxw(name, model,
#                          'addons/training/report/in_construction.rml',
#                          parser=in_construction,
#                          header=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

