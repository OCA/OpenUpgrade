# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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

from openupgrade import openupgrade


def post_case_claim_stage(cr):
    """
    Set 6.1 states as 7.0 stages
    """
    stage_state_renames = [
        ("draft", "draft"),
        ("open", "open"),
        ("open", "pending"),
        ("done", "done"),
        ("cancel", "cancel")
    ]
    # Point new stage_id according to old state_id
    for stage_rename in stage_state_renames:
        openupgrade.logged_query(cr, """
            UPDATE crm_claim
            SET stage_id = (SELECT id
                            FROM crm_claim_stage
                            WHERE state = %s)
            WHERE state = %s;
            """, stage_rename)


@openupgrade.migrate()
def migrate(cr, version):
    # Add stages to crm_claim_stage
    openupgrade.load_xml(
        cr, 'crm_claim',
        'migrations/7.0.1.0/data.xml')
    post_case_claim_stage(cr)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
