# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_company_id(cr):
    table_list = [
        'lunch_order',
        'lunch_product_category',
    ]
    for table in table_list:
        openupgrade.logged_query(
            cr, """
            UPDATE {table} tbl
            SET company_id = ru.company_id
            FROM res_users ru
            WHERE ru.id = tbl.create_uid AND tbl.company_id IS NULL
            """.format(table=table))


@openupgrade.migrate()
def migrate(env, version):
    fill_company_id(env.cr)
