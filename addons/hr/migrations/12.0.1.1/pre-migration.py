# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

xmlid_renames = [
    ('hr.employee_root', 'hr.employee_admin'),
]


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    openupgrade.rename_xmlids(cr, xmlid_renames)
