# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

def set_partner_id(cr):
    openupgrade.logged_query(cr, """
    UPDATE account_analytic_line a 
    SET partner_id = s.partner_id 
    FROM res_users s 
    WHERE a.user_id = s.id
    """)

@openupgrade.migrate()
def migrate(cr, version):
    set_partner_id(cr)