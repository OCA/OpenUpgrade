# Copyright 2018 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

column_copies = {
    'crm_team': [
        ('dashboard_graph_model', None, None),
    ],
}

_column_renames = {
    'crm_lead': [
        ('opt_out', None),
    ],
}


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    openupgrade.copy_columns(cr, column_copies)
    openupgrade.rename_columns(cr, _column_renames)
