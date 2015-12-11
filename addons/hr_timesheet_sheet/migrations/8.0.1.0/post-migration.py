# -*- coding: utf-8 -*-
# © 2015 - Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import pooler, SUPERUSER_ID
from openupgradelib import openupgrade, openupgrade_80


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    openupgrade_80.set_message_last_post(
        cr, SUPERUSER_ID, pool, ['hr_timesheet_sheet.sheet'])
