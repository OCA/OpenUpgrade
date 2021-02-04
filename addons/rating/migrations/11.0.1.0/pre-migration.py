# -*- coding: utf-8 -*-
# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

COLUMN_COPIES = {
    'rating_rating': [
        ('res_model', None, None),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, COLUMN_COPIES)

    # Precreate and populate mail_message's new stored field rating_value
    openupgrade.add_fields(env, [
        ("rating_value", "mail.message",
         "mail_message", "float", False, "rating", 0)])
    openupgrade.logged_query(
        env.cr,
        """UPDATE mail_message mm
        SET rating_value = rr.rating
        FROM rating_rating rr
        WHERE rr.message_id = mm.id""")
