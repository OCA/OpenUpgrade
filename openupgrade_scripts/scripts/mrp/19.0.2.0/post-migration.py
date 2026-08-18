# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def mrp_production_group(env):
    """
    Create production groups from procurement groups
    """
    link_column = openupgrade.get_legacy_name("procurement_group_id")
    env.cr.execute(
        f"ALTER TABLE mrp_production_group ADD COLUMN IF NOT EXISTS {link_column} int"
    )
    env.cr.execute(
        f"""
        INSERT INTO mrp_production_group
        (name, {link_column})
        SELECT
        stock_reference.name, stock_reference.id
        FROM
        stock_reference
        WHERE id IN (
            SELECT procurement_group_id FROM
            mrp_production
        )
        """
    )
    env.cr.execute(
        f"""
        UPDATE mrp_production
        SET production_group_id=mrp_production_group.id
        FROM
        mrp_production_group
        WHERE {link_column}=procurement_group_id
        """
    )
    env.cr.execute(
        f"""
        UPDATE stock_move
        SET production_group_id=mrp_production_group.id
        FROM
        mrp_production_group
        WHERE {link_column}=group_id
        """
    )


def mrp_workorder_state(env):
    """
    Map mrp.workorder#state values
    """
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("state"),
        "state",
        [("pending", "blocked"), ("waiting", "blocked")],
        table="mrp_workorder",
    )


def mrp_workcenter_capacity_product_uom_id(env):
    """
    Fill mrp.workcenter.capacity#product_uom_id
    """
    env.cr.execute(
        f"""
        UPDATE mrp_workcenter_capacity
        SET
        product_uom_id=COALESCE(
            product_template.uom_id,
            {env.ref("uom.product_uom_unit").id}
        )
        FROM
        product_product,
        product_template
        WHERE
        mrp_workcenter_capacity.product_id=product_product.id
        AND
        product_product.product_tmpl_id=product_template.id
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env,
        "mrp",
        "19.0.2.0/noupdate_changes.xml",
        xml_transformation_filename="19.0.2.0/noupdate_changes-transformation.xml",
    )
    openupgrade.m2o_to_x2m(
        env.cr,
        env["mrp.production"],
        "mrp_production",
        "lot_producing_ids",
        "lot_producing_id",
    )
    openupgrade.m2o_to_x2m(
        env.cr,
        env["mrp.production"],
        "mrp_production",
        "reference_ids",
        "procurement_group_id",
    )
    mrp_production_group(env)
    mrp_workorder_state(env)
    mrp_workcenter_capacity_product_uom_id(env)
