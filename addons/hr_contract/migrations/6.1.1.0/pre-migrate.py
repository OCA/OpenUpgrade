# -*- coding: utf-8 -*-
from openerp.openupgrade import openupgrade

#@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(
      cr,
      {
        'hr_contract':
        [
          ('advantages_gross', openupgrade.get_legacy_name('advantages_gross')),
          ('advantages_net', openupgrade.get_legacy_name('advantages_net'))
        ]
      })
