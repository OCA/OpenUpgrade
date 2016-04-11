# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import pooler, SUPERUSER_ID
from openupgradelib import openupgrade, openupgrade_80


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    uid = SUPERUSER_ID
    openupgrade_80.set_message_last_post(cr, uid, pool, ['crm.claim'])
    openupgrade.map_values(
        cr, 'priority', openupgrade.get_legacy_name('priority'),
        [('1', '2'), ('3', '1'), ('4', '0'), ('5', '0')], table='crm_claim')
    openupgrade.load_data(
        cr, 'crm_claim', 'migrations/8.0.1.0/noupdate_changes.xml')
