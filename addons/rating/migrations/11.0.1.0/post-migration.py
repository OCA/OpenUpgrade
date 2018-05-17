# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


def update_res_model_id(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE rating_rating rr
        SET res_model_id = im.id
        FROM ir_model im
        WHERE im.name=rr.%s """,
        (AsIs(openupgrade.get_legacy_name('res_model')),),
    )


@openupgrade.migrate()
def migrate(env, version):
    update_res_model_id(env)
