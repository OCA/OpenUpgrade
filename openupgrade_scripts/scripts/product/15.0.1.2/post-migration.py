from openupgradelib import openupgrade


def _update_color_product_template_attribute_value(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_template_attribute_value
        SET color = FLOOR(random() * 11 + 1)
        WHERE color IS NULL
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _update_color_product_template_attribute_value(env)
