# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_field_renames = [
    ('hr.employee', 'hr_employee', 'vehicle_distance', 'km_home_work'),
]

xmlid_renames = [
    ('hr.employee_root', 'hr.employee_admin'),
]


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(env.cr, 'hr_employee', 'vehicle_distance'):
        openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_xmlids(env.cr, xmlid_renames)
