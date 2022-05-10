# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2 import sql
from openupgradelib import openupgrade


def update_repair_fee_invoice_relation(env):
    openupgrade.logged_query(
        env.cr, sql.SQL(
            """UPDATE repair_fee rf
            SET invoice_line_id = aml.id
            FROM account_move_line aml
            WHERE rf.{} = aml.old_invoice_line_id"""
        ).format(
            sql.Identifier(openupgrade.get_legacy_name("invoice_line_id"))
        ),
    )


def update_repair_line_invoice_relation(env):
    openupgrade.logged_query(
        env.cr, sql.SQL(
            """UPDATE repair_line rl
            SET invoice_line_id = aml.id
            FROM account_move_line aml
            WHERE rl.{} = aml.old_invoice_line_id"""
        ).format(
            sql.Identifier(openupgrade.get_legacy_name("invoice_line_id"))
        ),
    )


def update_repair_order_invoice_relation(env):
    openupgrade.logged_query(
        env.cr, sql.SQL(
            """UPDATE repair_order ro
            SET invoice_id = am.id
            FROM account_move am
            WHERE ro.{} = am.old_invoice_id"""
        ).format(
            sql.Identifier(openupgrade.get_legacy_name("invoice_id"))
        ),
    )


def update_repair_order_user_id(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE repair_order
        SET user_id = create_uid""",
    )


def _get_main_company(cr):
    cr.execute("""SELECT id, name FROM res_company ORDER BY id""")
    return cr.fetchone()


def map_repair_locations(env, main_company):
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE repair_line
        ADD COLUMN IF NOT EXISTS company_id integer""",
    )
    # is added later in v14, so no problem by adding it now.
    openupgrade.logged_query(
        env.cr, """
        UPDATE repair_line rl
        SET company_id = ro.company_id
        FROM repair_order ro
        WHERE rl.repair_id = ro.id AND rl.company_id IS NULL
            AND ro.company_id IS NOT NULL""",
    )
    conditions = {
        'location_inventory':
            "sl2.usage = 'inventory' AND sl2.scrap_location IS NOT TRUE",
        'location_production': "sl2.usage = 'production'",
        'stock_location_scrapped':
            "sl2.usage = 'inventory' AND sl2.scrap_location IS TRUE",
    }
    affected_models = {
        'repair.order': ['location_id'],
        'repair.line': ['location_id', 'location_dest_id'],
    }
    for model, locations in affected_models.items():
        table = env[model]._table
        for location in locations:
            for xmlid_name, condition in conditions.items():
                openupgrade.logged_query(
                    env.cr, """
            UPDATE {table} tab
            SET {location} = (
                SELECT sl2.id
                FROM stock_location sl2
                LEFT JOIN ir_model_data imd2 ON (imd2.module = 'stock' and
                    imd2.model = 'stock.location' and imd2.res_id = sl2.id)
                LEFT JOIN res_users ru2 ON ru2.id = sl2.create_uid
                WHERE {condition}
                    AND imd2.name IS NULL AND
                    COALESCE(sl2.company_id, ru2.company_id) =
                        COALESCE(tab.company_id, ru.company_id)
                LIMIT 1
                )
            FROM stock_location sl
            JOIN ir_model_data imd ON (imd.module = 'stock' and
                imd.model = 'stock.location' and imd.res_id = sl.id)
            LEFT JOIN res_users ru ON sl.create_uid = ru.id
            WHERE tab.{location} = sl.id AND
                tab.company_id != {main_company_id} AND
                imd.name = '{xmlid_name}'
                        """.format(table=table, main_company_id=main_company[0],
                                   location=location,
                                   xmlid_name=xmlid_name, condition=condition)
                )


@openupgrade.migrate()
def migrate(env, version):
    main_company = _get_main_company(env.cr)
    map_repair_locations(env, main_company)
    update_repair_fee_invoice_relation(env)
    update_repair_line_invoice_relation(env)
    update_repair_order_invoice_relation(env)
    update_repair_order_user_id(env)
    openupgrade.load_data(
        env.cr, "repair",
        "migrations/13.0.1.0/noupdate_changes.xml"
    )
