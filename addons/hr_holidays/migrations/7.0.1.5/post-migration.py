# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This migration script copyright (C) 2015 Therp BV
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
from openupgrade import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    # write categories from crm.case.categ
    cr.execute('alter table crm_meeting_type add column %s integer',
               openupgrade.get_legacy_name('crm_meeting_type_id'))
    cr.execute(
        'insert into crm_meeting_type (name, %s) '
        'select name, id from crm_case_categ where object_id='
        "(select id from ir_model where model='crm.meeting')" %
        openupgrade.get_legacy_name('crm_meeting_type_id'))
    cr.execute(
        'update hr_holidays_status s '
        'set categ_id=t.id '
        'from crm_meeting_type t '
        'where t.%s=s.%s' % (
            openupgrade.get_legacy_name('crm_meeting_type_id'),
            openupgrade.get_legacy_name('categ_id'),
        ))
