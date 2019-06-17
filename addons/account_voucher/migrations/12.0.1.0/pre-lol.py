# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def assure_company(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE account_voucher av
        SET company_id = aj.company_id
        FROM account_journal aj
        WHERE av.journal_id = aj.id
            AND av.company_id IS NULL"""
    )


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(env.cr, 'account_voucher', 'company_id'):
        # In odoo v8, the company_id was stored. Thus, maybe some databases
        # that have been migrating since v8, may still have that column. Thus,
        # if new records have been created in newer versions, they may have
        # this field empty.
        assure_company(env.cr)
