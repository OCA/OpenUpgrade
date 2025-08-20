# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def _fill_restaurant_table_table_number(env):
    # Update when name is numeric
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE restaurant_table
        SET table_number = name::integer
        WHERE name ~ '^[0-9]+$';
        """,
    )
    # Generate numbering by floor_id when 'name' is not numeric
    openupgrade.logged_query(
        env.cr,
        """
        WITH numbered AS (
            SELECT id,
                ROW_NUMBER() OVER (PARTITION BY floor_id ORDER BY id) AS rn
            FROM restaurant_table
            WHERE name !~ '^[0-9]+$'
        )
        UPDATE restaurant_table t
        SET table_number = n.rn
        FROM numbered n
        WHERE t.id = n.id;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _fill_restaurant_table_table_number(env)
    openupgrade.delete_records_safely_by_xml_id(
        env,
        ["pos_restaurant.pos_config_main_restaurant"],
    )
