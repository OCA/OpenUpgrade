# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# Copyright 2020 Andrii Skrypka <andrijskrypa@ukr.net>
# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_unlink_by_xmlid = [
    'mrp.sequence_mrp_unbuild',
]


def fill_bom_product_template_attribute_value(env):
    openupgrade.logged_query(env.cr, """
    INSERT INTO mrp_bom_line_product_template_attribute_value_rel
        (mrp_bom_line_id, product_template_attribute_value_id)
    SELECT mbl_pav_rel.mrp_bom_line_id, ptav.id
    FROM mrp_bom_line_product_attribute_value_rel mbl_pav_rel
    JOIN product_attribute_value pav ON pav.id = mbl_pav_rel.product_attribute_value_id
    JOIN mrp_bom_line mbl ON mbl.id = mbl_pav_rel.mrp_bom_line_id
    JOIN mrp_bom mb ON mbl.bom_id = mb.id
    JOIN product_template_attribute_value ptav ON (
            mb.product_tmpl_id = ptav.product_tmpl_id
            AND pav.id = ptav.product_attribute_value_id
            AND pav.attribute_id = ptav.attribute_id)
    GROUP BY mbl_pav_rel.mrp_bom_line_id, ptav.id
    """)


def fill_propagate_date_minimum_delta(env):
    # mrp production
    openupgrade.logged_query(
        env.cr, """
        UPDATE mrp_production mp
        SET propagate_date_minimum_delta = rc.propagation_minimum_delta
        FROM res_company rc
        WHERE mp.company_id = rc.id AND
            mp.propagate_date_minimum_delta IS NULL
            AND rc.propagation_minimum_delta IS NOT NULL
        """
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE mrp_production mp
        SET propagate_date = TRUE
        FROM ir_config_parameter icp
        WHERE mp.propagate_date IS NULL
            AND icp.key = 'stock.use_propagation_minimum_delta'
            AND icp.value = 'True'
        """
    )


def mapped_reservation_state(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE mrp_production
        SET reservation_state = NULL
        WHERE reservation_state = 'none'
        """
    )
    # in v12 reservation state is not NULL when MO was done or cancel
    openupgrade.logged_query(
        env.cr, """
        UPDATE mrp_production
        SET reservation_state = NULL
        WHERE state in ('done', 'cancel')
        """
    )

    # convert 'partially_available' according to
    # _compute_state function of mrp_production model

    # get MO ids which need mapped value according to _get_ready_to_produce_state function
    openupgrade.logged_query(
        env.cr, """
        SELECT mo.id as id
        FROM mrp_production mo
            JOIN mrp_routing_workcenter operation
                ON mo.routing_id = operation.routing_id
            JOIN mrp_bom bom
                ON mo.bom_id = bom.id AND bom.ready_to_produce = 'asap'
        WHERE mo.routing_id IS NOT NULL AND mo.reservation_state = 'partially_available'
        GROUP BY mo.id
        """
    )
    mo_ids = tuple(x[0] for x in env.cr.fetchall())
    if mo_ids:
        reservation_state = {}
        for mo in env['mrp.production'].browse(mo_ids):
            reservation_state.setdefault(
                mo._get_ready_to_produce_state(), []).append(mo.id)
        for value, ids in reservation_state.items():
            openupgrade.logged_query(
                env.cr, """
                UPDATE mrp_production
                SET reservation_state = %s
                WHERE id in %s
                """, (value, tuple(ids))
            )
    # set 'confirm' for record which not in mo_ids
    openupgrade.logged_query(
        env.cr, """
        UPDATE mrp_production mo
        SET reservation_state = 'confirm'
        WHERE mo.reservation_state = 'partially_available'
        """
    )
    # manual update related store=True field
    openupgrade.logged_query(
        env.cr, """
        UPDATE mrp_workorder wo
        SET production_availability = mo.reservation_state
        FROM mrp_production mo
        WHERE wo.production_id = mo.id
        """
    )


def convert_many2one_field(env):
    openupgrade.m2o_to_x2m(
        env.cr,
        env['stock.move.line'], 'stock_move_line',
        'lot_produced_ids', openupgrade.get_legacy_name('lot_produced_id')
    )


def fill_mrp_workcenter_productivity_company_id(env):
    # from mrp_workorder
    openupgrade.logged_query(
        env.cr, """
        UPDATE mrp_workcenter_productivity mwp
        SET company_id = mp.company_id
        FROM mrp_workorder mw
        JOIN mrp_production mp ON mw.production_id = mp.id
        WHERE mwp.workorder_id = mw.id AND mp.company_id IS NOT NULL
        """
    )
    # from mrp_workcenter
    openupgrade.logged_query(
        env.cr, """
        UPDATE mrp_workcenter_productivity mwp
        SET company_id = mw.company_id
        FROM mrp_workcenter mw
        WHERE mwp.workcenter_id = mw.id AND mw.company_id IS NOT NULL
        """
    )


def fill_unbuild_company_id(cr):
    # from mrp_bom
    openupgrade.logged_query(
        cr, """
        UPDATE mrp_unbuild mu
        SET company_id = mb.company_id
        FROM mrp_bom mb
        WHERE mu.bom_id = mb.id AND mb.company_id IS NOT NULL
            AND mu.company_id IS DISTINCT FROM mb.company_id"""
    )
    # from stock_move/res_users
    openupgrade.logged_query(
        cr, """
        UPDATE mrp_unbuild mu
        SET company_id = COALESCE(
            (SELECT sm.company_id FROM stock_move sm
             WHERE mu.id = sm.unbuild_id AND sm.company_id IS NOT NULL
             LIMIT 1), ru.company_id)
        FROM res_users ru
        WHERE ru.id = mu.create_uid AND mu.company_id IS NULL
        """
    )


def fill_stock_picking_type_sequence_code(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_picking_type spt
        SET sequence_code = CASE
          WHEN spt.id = wh.pbm_type_id THEN 'PC'
          WHEN spt.id = wh.sam_type_id THEN 'SFP'
          WHEN spt.id = wh.manu_type_id THEN 'MO'
          END
        FROM stock_warehouse wh
        WHERE sequence_code = 'TO_FILL' AND spt.id in (wh.pbm_type_id, wh.sam_type_id, wh.manu_type_id)
        """
    )


def handle_unbuild_sequence(env):
    # although later the 'mrp.sequence_mrp_unbuild' sequence will be deleted,
    # we need to nullify its code (if having one) here
    # because we want a new autogenerated sequence
    openupgrade.logged_query(
        env.cr, """
        UPDATE ir_sequence seq
        SET code = NULL
        FROM ir_model_data imd
        WHERE imd.res_id = seq.id AND imd.module = 'mrp'
            AND imd.name = 'sequence_mrp_unbuild'"""
    )
    # force execute this function (it is noupdate=1 in xml data)
    env['res.company'].create_missing_unbuild_sequences()


def fill_manufacture_mto_pull(env):
    warehouses = env['stock.warehouse'].with_context(active_test=False).search([
        ('manufacture_to_resupply', '=', True),
        ('manufacture_mto_pull_id', '=', False),
    ])
    for wh in warehouses:
        rule_details = wh._get_global_route_rules_values()['manufacture_mto_pull_id']
        values = rule_details.get('update_values', {})
        values.update(rule_details['create_values'])
        values.update({'warehouse_id': wh.id})
        wh['manufacture_mto_pull_id'] = env['stock.rule'].create(values)


def fill_mrp_workorder_product_uom_id(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE mrp_workorder mw
        SET product_uom_id = mp.product_uom_id
        FROM mrp_production mp
        WHERE mw.production_id = mp.id AND mw.product_uom_id IS NULL
        """
    )


def update_consumption(env):
    """ Create column and pre-fill 'flexible' because In Odoo 12 work like 'flexible'"""
    openupgrade.logged_query(
        env.cr, """
        UPDATE mrp_bom
        SET consumption = 'flexible'
        """,
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE mrp_workorder
        SET consumption = 'flexible'
        """,
    )


def enable_group_mrp_byproducts(env):
    if env['mrp.bom.byproduct'].search([], limit=1):
        config = env['res.config.settings'].create({'group_mrp_byproducts': True})
        config.execute()


def generate_wo_line(env):
    """ Convert active_move_line_ids to raw_workorder_line_ids """
    openupgrade.logged_query(env.cr, """
    SELECT id, workorder_id
    FROM stock_move_line
    WHERE workorder_id IS NOT NULL AND done_wo = False and state NOT IN ('done', 'cancel')
    """)
    active_sml_ids = []
    wo_ids = set()
    for sml_id, wo_id in env.cr.fetchall():
        wo_ids.add(wo_id)
        active_sml_ids.append(sml_id)
    for workorder in env['mrp.workorder'].browse(list(wo_ids)):
        workorder._refresh_wo_lines()
    env['stock.move.line'].browse(active_sml_ids).unlink()


def fill_planned_datetime(env):
    openupgrade.logged_query(env.cr, """
    UPDATE mrp_workorder wo
    SET date_planned_start = mo.date_planned_start, date_planned_finished = mo.date_planned_finished
    FROM mrp_production mo
    WHERE wo.state NOT IN ('done', 'cancel') AND wo.production_id = mo.id
        AND wo.date_planned_finished IS NULL AND wo.date_planned_start IS NULL
    """)


def _get_main_company(cr):
    cr.execute("""SELECT id, name FROM res_company ORDER BY id""")
    return cr.fetchone()


def map_mrp_locations(env, main_company):
    conditions = {
        'location_inventory':
            "sl2.usage = 'inventory' AND sl2.scrap_location IS NOT TRUE",
        'location_production': "sl2.usage = 'production'",
        'stock_location_scrapped':
            "sl2.usage = 'inventory' AND sl2.scrap_location IS TRUE",
    }
    affected_models = {
        'mrp.production': ['location_src_id', 'location_dest_id'],
        'mrp.unbuild': ['location_id', 'location_dest_id'],
    }
    for model, locations in affected_models.items():
        table = env[model]._table
        for location in locations:
            for xmlid_name, condition in conditions.items():
                openupgrade.logged_query(
                    env.cr, """
            UPDATE {table} tab
            SET {location} = (
                SELECT sl2.id
                FROM stock_location sl2
                LEFT JOIN ir_model_data imd2 ON (imd2.module = 'stock' and
                    imd2.model = 'stock.location' and imd2.res_id = sl2.id)
                LEFT JOIN res_users ru2 ON ru2.id = sl2.create_uid
                WHERE {condition}
                    AND imd2.name IS NULL AND
                    COALESCE(sl2.company_id, ru2.company_id) =
                        COALESCE(tab.company_id, ru.company_id)
                LIMIT 1
                )
            FROM stock_location sl
            JOIN ir_model_data imd ON (imd.module = 'stock' and
                imd.model = 'stock.location' and imd.res_id = sl.id)
            LEFT JOIN res_users ru ON sl.create_uid = ru.id
            WHERE tab.{location} = sl.id AND
                tab.company_id != {main_company_id} AND
                imd.name = '{xmlid_name}'
                        """.format(table=table, main_company_id=main_company[0],
                                   location=location,
                                   xmlid_name=xmlid_name, condition=condition)
                )


@openupgrade.migrate()
def migrate(env, version):
    fill_bom_product_template_attribute_value(env)
    fill_propagate_date_minimum_delta(env)
    mapped_reservation_state(env)
    convert_many2one_field(env)
    fill_mrp_workcenter_productivity_company_id(env)
    fill_unbuild_company_id(env.cr)
    fill_stock_picking_type_sequence_code(env)
    handle_unbuild_sequence(env)
    fill_manufacture_mto_pull(env)
    fill_mrp_workorder_product_uom_id(env.cr)
    update_consumption(env)
    main_company = _get_main_company(env.cr)
    map_mrp_locations(env, main_company)
    openupgrade.load_data(env.cr, 'mrp', 'migrations/13.0.2.0/noupdate_changes.xml')
    openupgrade.delete_records_safely_by_xml_id(env, _unlink_by_xmlid)
    enable_group_mrp_byproducts(env)
    generate_wo_line(env)
    fill_planned_datetime(env)
