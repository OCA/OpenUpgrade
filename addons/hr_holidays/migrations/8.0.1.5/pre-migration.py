# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
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


@openupgrade.migrate()
def migrate(cr, version):
    cr.execute(
        "ALTER TABLE hr_holidays DROP CONSTRAINT hr_holidays_meeting_id_fkey"
    )
    cr.execute(
        '''update hr_holidays
        set meeting_id=calendar_event.id
        from calendar_event where meeting_id=%s''' % (
            openupgrade.get_legacy_name('crm_meeting_id'),
        )
    )
