# -*- coding: utf-8 -*-
# © 2016 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.load_data(cr, 'survey',
                          'migrations/9.0.2.0/noupdate_changes.xml')
