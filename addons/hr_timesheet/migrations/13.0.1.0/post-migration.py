# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_unlink_by_xmlid = [
    'hr_timesheet.timesheet_rule_portal',
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(env, _unlink_by_xmlid)
    openupgrade.load_data(env.cr, 'hr_timesheet', 'migrations/13.0.1.0/noupdate_changes.xml')
