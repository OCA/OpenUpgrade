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
    execute = openupgrade.logged_query
    user_input_obj = pool['survey.user_input']
    execute(cr, "SELECT id FROM hr_evaluation_interview")
    for interview_id in cr.fetchall():
        ret = user_input_obj.create(cr, SUPERUSER_ID, {
            'survey_id': 1,
            'type': 'link',
        }, context={})
        execute(
            cr,
            "UPDATE hr_evaluation_interview\n"
            "SET request_id = %d WHERE id = %d\n" %
            (ret, interview_id[0])
        )

