from openupgradelib import openupgrade, openupgrade_merge_records


def merge_event_sale_into_event_product(env):
    if not openupgrade.is_module_installed(env.cr, "event_product"):
        return

    # Step 1: Get references
    event_sale_category = env.ref(
        "event_sale.product_category_events", raise_if_not_found=False
    )
    event_product_category = env.ref(
        "event_product.product_category_events", raise_if_not_found=False
    )
    event_sale_product = env.ref(
        "event_sale.product_product_event", raise_if_not_found=False
    )
    event_product_product = env.ref(
        "event_product.product_product_event", raise_if_not_found=False
    )

    # Step 2: Merge product categories
    if (
        event_sale_category
        and event_product_category
        and event_sale_category.id != event_product_category.id
    ):
        openupgrade_merge_records.merge_records(
            env,
            "product.category",
            [event_sale_category.id],
            event_product_category.id,
            method="sql",
        )

    # Step 3: Merge product variants and templates
    if (
        event_sale_product
        and event_product_product
        and event_sale_product.id != event_product_product.id
    ):
        tmpl_id_src = event_sale_product.product_tmpl_id.id
        tmpl_id_dest = event_product_product.product_tmpl_id.id

        openupgrade_merge_records.merge_records(
            env,
            "product.product",
            [event_sale_product.id],
            event_product_product.id,
            method="sql",
        )

        if tmpl_id_src != tmpl_id_dest:
            openupgrade_merge_records.merge_records(
                env, "product.template", [tmpl_id_src], tmpl_id_dest, method="sql"
            )


def cleanup_ir_model_data(env):
    """
    Remove obsolete ir.model.data entries for event_sale
    so XML ID renaming doesn't fail.
    """
    env.cr.execute(
        """
        DELETE FROM ir_model_data
        WHERE (module, name) IN (('event_sale', 'product_category_events'),
        ('event_sale', 'product_product_event'))
    """
    )


def safe_rename_xmlid(cr, old, new):
    # Check if the new XMLID already exists
    cr.execute(
        """
        SELECT 1 FROM ir_model_data WHERE module = %s AND name = %s
    """,
        tuple(new.split(".")),
    )
    if cr.fetchone():
        return
    openupgrade.rename_xmlids(cr, [(old, new)])


@openupgrade.migrate()
def migrate(env, version):
    merge_event_sale_into_event_product(env)
    cleanup_ir_model_data(env)
    safe_rename_xmlid(
        env.cr,
        "event_sale.product_category_events",
        "event_product.product_category_events",
    )
    safe_rename_xmlid(
        env.cr,
        "event_sale.product_product_event",
        "event_product.product_product_event",
    )
