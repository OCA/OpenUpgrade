# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

def account_type(cr):
    openupgrade.logged_query(cr, """
    ALTER TABLE account_analytic_account RENAME COLUMN type TO account_type
    """)

def set_account_type(cr):
    openupgrade.logged_query(cr, """
    UPDATE account_analytic_account SET account_type = 'normal'
    """)

@openupgrade.migrate()
def migrate(cr, version):
    account_type(cr)
    set_account_type(cr)
