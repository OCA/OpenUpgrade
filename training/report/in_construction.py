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

class training_subscription_cancel_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(training_subscription_cancel_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.training.subscription.cancel',
                      'training.subscription',
                      'addons/training/report/training_subscription_cancel.rml',
                      parser=training_subscription_cancel_report,
                      header=True)

class training_subscription_confirm_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(training_subscription_confirm_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.training.subscription.confirm',
                      'training.subscription',
                      'addons/training/report/training_subscription_confirm.rml',
                      parser=training_subscription_confirm_report,
                      header=True)

class training_seance_presence_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(training_seance_presence_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'present':self._present
        })
    def _present(self,subscription_id):
            res=[]
            self.cr.execute('select present from training_participation where subscription_id =%s',(subscription_id,))
            res=self.cr.fetchone()
            if res[0]==True:
                return 'Yes'
            return res and res[0] or 'No'

report_sxw.report_sxw('report.training.seance.presence',
                      'training.seance',
                      'addons/training/report/training_presence.rml',
                      parser=training_seance_presence_report,
                      header=True)


class training_course_material_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(training_course_material_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.training.course.material.report',
                      'training.course',
                      'addons/training/report/training_course.rml',
                      parser=training_seance_presence_report,
                      header=True)

class training_subscription_presence_certificate_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(training_subscription_presence_certificate_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.training.subscription.presence.certificate.report',
                      'training.subscription',
                      'addons/training/report/training_presence_certificate.rml',
                      parser=training_subscription_presence_certificate_report,
                      header=True)


class training_dummy_support_delivery_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(training_dummy_support_delivery_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.dummy.support.delivery.report',
                      'dummy.support.delivery',
                      'addons/training/report/delivery_support.rml',
                      parser=training_dummy_support_delivery_report,
                      header=True)

class training_seance_cancel_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(training_seance_cancel_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.training.seance.cancel.report',
                      'training.seance',
                      'addons/training/report/training_seance_cancel.rml',
                      parser=training_seance_cancel_report,
                      header=True)

class training_session_cancel_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(training_session_cancel_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.training.session.cancel.report',
                      'training.session',
                      'addons/training/report/training_session_cancel.rml',
                      parser=training_session_cancel_report,
                      header=True)

class training_dummy_training_hiring_form_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(training_dummy_training_hiring_form_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.dummy.training.hiring.form.report',
                      'dummy.support.delivery',
                      'addons/training/report/training_hiring_form.rml',
                      parser=training_dummy_training_hiring_form_report,
                      header=True)

class training_dummy_training_evaluation_skateholder_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(training_dummy_training_evalation_skateholder_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.training.evaluation.skateholder.report',
                      'dummy.support.delivery',
                      'addons/training/report/evaluation_from_skateholder.rml',
                      parser=training_dummy_training_evaluation_skateholder_report,
                      header=True)

class training_dummy_training_evaluation_participant_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(training_dummy_training_evalation_participant_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.training.evaluation.participant.report',
                      'dummy.support.delivery',
                      'addons/training/report/evaluation_from_participant.rml',
                      parser=training_dummy_training_evaluation_participant_report,
                      header=True)

class in_construction(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(in_construction, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })

reports = [
    ('report.training.seance.booking.support', 'training.seance'),
    ('report.training.seance.booking.classroom', 'training.seance'),
    ('report.training.course.financial.report', 'training.course')
]

for name, model in reports:
    report_sxw.report_sxw(name, model,
                          'addons/training/report/in_construction.rml',
                          parser=in_construction,
                          header=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

