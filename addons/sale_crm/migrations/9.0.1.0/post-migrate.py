# coding: utf-8
# © 2016 Opener B.V. - Stefan Rijnhart
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


def get_sale_order_opportunity_id(env):
    """ Fetch sale order references from the obsolete reference
    fields from the crm module """
    env.cr.execute(
        """UPDATE sale_order so
        SET opportunity_id = cl.id
        FROM crm_lead cl
        WHERE cl.%s = 'sale.order,'||so.id
            OR cl.%s = 'sale.order,'||so.id""",
        (AsIs(openupgrade.get_legacy_name('ref')),
         AsIs(openupgrade.get_legacy_name('ref2'))))


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    get_sale_order_opportunity_id(env)
