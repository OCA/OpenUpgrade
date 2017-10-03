# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2.extensions import AsIs
from openupgradelib import openupgrade


def map_ir_actions_server_fields(cr):
    """Map field menu_ir_values_id with the help of field model_id to field
    binding_model_id. Use value 'action' for field binding_type. Delete
    ir.values record at the end."""
    cr.execute("""
        SELECT id, model_id, %(menu_ir_values_id)s FROM ir_act_server
        WHERE menu_ir_values_id IS NOT NULL; """)
    query = ("UPDATE ir_act_server SET binding_model_id = %s "
             "AND binding_type = 'action' WHERE id = %s;"
             "DELETE FROM ir_values WHERE id = %s;")
    for r in cr.fetchall():
        cr.execute(query, (r[1], r[0], r[2]))


def set_currency_rate_dates(cr):
    """ Set currency rate date per company's most popular timezone.
    Rates without a company will be cast to UTC date automatically. """
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


@openupgrade.migrate()
def migrate(env, version):
    map_ir_actions_server_fields(env.cr)
    set_currency_rate_dates(env.cr)
    openupgrade.load_data(
        env.cr, 'base', 'migrations/11.0.1.3/noupdate_changes.xml',
    )
