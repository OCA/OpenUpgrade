# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import json

from odoo.tools import pickle

from openupgradelib import openupgrade

from psycopg2.extensions import AsIs


def map_ir_actions_server_fields(cr):
    """Map field menu_ir_values_id with the help of field model_id to field
    binding_model_id. Use value 'action' for field binding_type. Delete
    ir.values record at the end."""
    cr.execute("""
        SELECT id, model_id, menu_ir_values_id FROM ir_act_server
        WHERE menu_ir_values_id IS NOT NULL; """)
    query = """
        UPDATE ir_act_server
        SET binding_model_id = %s, binding_type = 'action'
        WHERE id = %s;
        DELETE FROM ir_values WHERE id = %s;"""
    for r in cr.fetchall():
        cr.execute(query, (r[1], r[0], r[2]))


def set_currency_rate_dates(cr):
    """Set currency rate date per company's most popular timezone.
    Rates without a company will be cast to UTC date automatically."""
    cr.execute("SELECT id FROM res_company")
    for company_id, in cr.fetchall():
        cr.execute(
            """
            SELECT rp.tz, count(rp) as cnt
            FROM res_users ru
            JOIN res_partner rp ON ru.partner_id = rp.id
            WHERE ru.company_id = %s
            GROUP BY rp.tz ORDER BY cnt DESC LIMIT 1""",
            (company_id,))
        tz = cr.fetchone()[0] or 'UTC'
        cr.execute(
            """
            UPDATE res_currency_rate
            SET name = (
                %s::TIMESTAMP at TIME ZONE 'UTC'
                AT TIME ZONE %s)::DATE
            WHERE company_id = %s""", (
                AsIs(openupgrade.get_legacy_name('name')),
                tz, company_id))


def merge_default_ir_values(cr):
    """Merge 'default' ir.values records into ir.default records. We only
    consider 'default' ir.values with non empty values. Delete ir.values record
    at the end."""
    cr.execute("""
        SELECT id, create_date, write_date, create_uid, write_uid, user_id,
            company_id, name, model, value
        FROM ir_values WHERE key = 'default' AND value IS NOT NULL;""")
    query = """
        INSERT INTO ir_default (
            create_date, write_date, create_uid, write_uid, user_id, company_id
            field_id, json_value)
        VALUES %s;
        DELETE FROM ir_values WHERE id = %s;"""
    for r in cr.fetchall():
        cr.execute("""
            SELECT id FROM ir_model_fields WHERE name = %s AND model = %s;
        """, (r[7], r[8]))
        model_field = cr.fetchone()

        if model_field and model_field[0]:
            # taken from odoo 10 to get pickled value and odoo 11 to store JSON
            # value
            value = str(pickle.loads(r[9]))
            json_value = json.dumps(value, ensure_ascii=False)
            values = tuple([r[1], r[2], r[3], r[4], r[5], r[6], model_field[0],
                            json_value])
            cr.execute(query, (values, r[0]))
    return True


@openupgrade.migrate()
def migrate(env, version):
    map_ir_actions_server_fields(env.cr)
    set_currency_rate_dates(env.cr)
    merge_default_ir_values(env.cr)
    openupgrade.load_data(
        env.cr, 'base', 'migrations/11.0.1.3/noupdate_changes.xml',
    )
