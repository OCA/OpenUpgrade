# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from psycopg2.extensions import AsIs
from openupgradelib import openupgrade


def migrate_iface_tax_included(env):
    field = AsIs(openupgrade.get_legacy_name('iface_tax_included'))
    openupgrade.logged_query(
        env.cr, """
            UPDATE pos_config
            SET iface_tax_included =
              CASE
                WHEN %s = False
                THEN 'subtotal'
                ELSE 'total'
              END
        """ % field)


def migrate_rescue(env):
    openupgrade.logged_query(
        env.cr, """
            UPDATE pos_session
            SET rescue = True
            WHERE name LIKE '%%RESCUE FOR%%'
        """)


def set_default_values(env):
    """ Update with default values for new required fields """
    openupgrade.set_defaults(
        env.cr, env, {
            'pos.config': [
                ('customer_facing_display_html', None),
            ]
        }, use_orm=True,
    )


@openupgrade.migrate()
def migrate(env, version):
    set_default_values(env)
    migrate_iface_tax_included(env)
    migrate_rescue(env)
    openupgrade.load_data(
        env.cr, 'point_of_sale', 'migrations/11.0.1.0.1/noupdate_changes.xml',
    )
