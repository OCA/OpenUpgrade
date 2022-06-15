from openupgradelib import openupgrade


def compute_product_template_attribute_line_value_count(env):
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
        SET value_count = (SELECT COUNT(product_template_attribute_line_id)
        FROM   product_attribute_value_product_template_attribute_line_rel
        WHERE  product_template_attribute_line_id = al.id)
        """,
    )


def convert_text_to_html(env):
    openupgrade.convert_field_to_html(
        env.cr, "product_template", "description", "description"
    )


def compute_detailed_type_and_type(env):
    if not openupgrade.column_exists(env.cr, "product_template", "detailed_type"):
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
        WHERE type = 'consu' OR type = 'service'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    compute_detailed_type_and_type(env)
    compute_product_template_attribute_line_value_count(env)
    convert_text_to_html(env)
