from openupgradelib import openupgrade


def compute_product_template_attribute_line_value_count(env):
    # fast compute value_count
    if not openupgrade.column_exists(
        env.cr, "product_template_attribute_line", "value_count"
    ):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE product_template_attribute_line
            ADD COLUMN value_count integer
            """,
        )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_template_attribute_line al
        SET value_count = (
            SELECT COUNT(*)
            FROM product_attribute_value_product_template_attribute_line_rel
            WHERE product_template_attribute_line_id = al.id
        )""",
    )


def convert_text_to_html(env):
    openupgrade.convert_field_to_html(
        env.cr, "product_template", "description", "description"
    )


def compute_detailed_type_and_type(env):
    if openupgrade.column_exists(env.cr, "product_template", "detailed_type"):
        openupgrade.rename_columns(
            env.cr,
            {
                "product_template": [
                    ("detailed_type", None),
                ],
            },
        )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE product_template
        ADD COLUMN detailed_type varchar
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_template
        SET detailed_type = type
        """,
    )


def fill_product_attribute_value_color(env):
    # fast fill color
    if openupgrade.column_exists(env.cr, "product_attribute_value", "color"):
        openupgrade.rename_columns(
            env.cr,
            {
                "product_attribute_value": [
                    ("color", None),
                ],
            },
        )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE product_attribute_value
        ADD COLUMN color integer
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_attribute_value
        SET color = FLOOR(random() * 11 + 1)::int
        WHERE color IS NULL
        """,
    )
    if openupgrade.column_exists(env.cr, "product_template_attribute_value", "color"):
        openupgrade.rename_columns(
            env.cr,
            {
                "product_template_attribute_value": [
                    ("color", None),
                ],
            },
        )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE product_template_attribute_value
        ADD COLUMN color integer
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_template_attribute_value
        SET color = FLOOR(random() * 11 + 1)::int
        WHERE color IS NULL
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    compute_detailed_type_and_type(env)
    compute_product_template_attribute_line_value_count(env)
    convert_text_to_html(env)
    fill_product_attribute_value_color(env)
