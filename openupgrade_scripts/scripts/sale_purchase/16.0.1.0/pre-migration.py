from openupgradelib import openupgrade


def delete_obsolete_constraints(env):
    openupgrade.delete_sql_constraint_safely(
        env, "sale_purchase", "product_template", "service_to_purchase"
    )


@openupgrade.migrate()
def migrate(env, version):
    delete_obsolete_constraints(env)
