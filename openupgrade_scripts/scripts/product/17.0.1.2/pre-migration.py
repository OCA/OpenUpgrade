# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# Copyright 2024 Hunki enterprises - Holger Brunn
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _clean_incorrect_packaging_records(env):
    """If there's any record of this kind, it's invalid and maybe a leftover of a
    non-cascade removal operation. Let's clean the table. There's a chance that this
    package was used elsewhere, so this will crash, but in that case, it seems legit to
    do it, for checking what's going on.
    """
    openupgrade.logged_query(
        env.cr, "DELETE FROM product_packaging WHERE product_id IS NULL"
    )


@openupgrade.migrate()
def migrate(env, version):
    _clean_incorrect_packaging_records(env)
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE product_tag
            ALTER COLUMN color TYPE VARCHAR USING color::VARCHAR;

        UPDATE product_tag
        SET color = CASE
            WHEN color = '1' THEN '#F06050'
            WHEN color = '2' THEN '#F4A460'
            WHEN color = '3' THEN '#F7CD1F'
            WHEN color = '4' THEN '#6CC1ED'
            WHEN color = '5' THEN '#814968'
            WHEN color = '6' THEN '#EB7E7F'
            WHEN color = '7' THEN '#2C8397'
            WHEN color = '8' THEN '#475577'
            WHEN color = '9' THEN '#D6145F'
            WHEN color = '10' THEN '#30C381'
            WHEN color = '11' THEN '#9365B8'
            ELSE '#3C3C3C'
        END;
        """,
    )
