# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This migration script copyright (C) 2010-2014 Akretion
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from openerp.openupgrade import openupgrade
from openerp import pooler, SUPERUSER_ID


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    interview_obj = pool['hr.evaluation.interview']
    survey_id = pool['ir.model.data'].xmlid_to_res_id(
        cr, SUPERUSER_ID,
        'hr_evaluation.appraisal_form',
        raise_if_not_found=True)
    for interview_id in interview_obj.search(cr, SUPERUSER_ID, [], context={}):
        interview = interview_obj.browse(
            cr, SUPERUSER_ID, interview_id, context={})
        interview.request_id.write({"survey_id": survey_id})

