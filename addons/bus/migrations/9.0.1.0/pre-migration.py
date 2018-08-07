# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    if openupgrade.table_exists(cr, 'im_chat_presence'):
        openupgrade.rename_models(cr, [('im_chat.presence', 'bus.presence')])
        openupgrade.rename_tables(cr, [('im_chat_presence', 'bus_presence')])
