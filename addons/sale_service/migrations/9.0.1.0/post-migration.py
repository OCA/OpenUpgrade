# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Vicent Cubells
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


def map_product_template(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE product_template
        SET track_service = 'task'
        WHERE %s
        """, (AsIs(openupgrade.get_legacy_name('auto_create_task')), )
    )


@openupgrade.migrate()
def migrate(cr, version):
    map_product_template(cr)
