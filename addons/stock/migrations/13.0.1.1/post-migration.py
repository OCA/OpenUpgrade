# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# Copyright 2020 ForgeFlow <https://www.forgeflow.com>
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
import re


def _get_main_company(cr):
    cr.execute("""SELECT id, name FROM res_company ORDER BY id""")
    return cr.fetchone()


def fill_company_id(cr):
    # stock.move.line
    openupgrade.logged_query(
        cr, """
        UPDATE stock_move_line sml
        SET company_id = sm.company_id
        FROM stock_move sm
        WHERE sml.move_id = sm.id AND sml.company_id IS NULL"""
    )
    openupgrade.logged_query(
        cr, """
        UPDATE stock_move_line sml
        SET company_id = sp.company_id
        FROM stock_picking sp
        WHERE sml.picking_id = sp.id AND sml.company_id IS NULL"""
    )
    openupgrade.logged_query(
        cr, """
        UPDATE stock_move_line sml
        SET company_id = sqp.company_id
        FROM stock_quant_package sqp
        WHERE sml.package_id = sqp.id AND sml.company_id IS NULL"""
    )
    # stock.picking.type
    openupgrade.logged_query(
        cr, """
        UPDATE stock_picking_type spt
        SET company_id = sw.company_id
        FROM stock_warehouse sw
        WHERE spt.warehouse_id = sw.id"""
    )
    # stock.picking
    openupgrade.logged_query(
        cr, """
        UPDATE stock_picking sp
        SET company_id = spt.company_id
        FROM stock_picking_type spt
        WHERE sp.picking_type_id = spt.id AND sp.company_id IS NULL"""
    )
    # stock.package_level
    openupgrade.logged_query(
        cr, """
        UPDATE stock_package_level spl
        SET company_id = sqp.company_id
        FROM stock_quant_package sqp
        WHERE spl.package_id = sqp.id AND spl.company_id IS NULL"""
    )
    # stock.scrap
    openupgrade.logged_query(
        cr, """
        UPDATE stock_scrap ss
        SET company_id = COALESCE(sm.company_id, ru.company_id)
        FROM stock_scrap ss2
        JOIN res_users ru ON ru.id = ss2.create_uid
        LEFT JOIN stock_move sm ON ss2.move_id = sm.id
        WHERE ss2.id = ss.id"""
    )
    # stock.putaway.rule
    openupgrade.logged_query(
        cr, """
        UPDATE stock_putaway_rule spr
        SET company_id = ru.company_id
        FROM res_users ru
        WHERE ru.id = spr.create_uid AND spr.company_id IS NULL"""
    )
    # stock.production.lot
    openupgrade.logged_query(
        cr, """
        UPDATE stock_production_lot spl
        SET company_id = sm.company_id
        FROM stock_move_line sml
        JOIN stock_move sm ON sm.id = sml.move_id
        WHERE sml.lot_id = spl.id AND spl.company_id IS NULL"""
    )
    openupgrade.logged_query(
         cr, """
         UPDATE stock_production_lot spl
         SET company_id = pt.company_id
         FROM product_product pp
         JOIN product_template pt ON pt.id = pp.product_tmpl_id
         WHERE pp.id = spl.product_id AND spl.company_id IS NULL"""
    )
    openupgrade.logged_query(
         cr, """
         UPDATE stock_production_lot spl
         SET company_id = ru.company_id
         FROM res_users ru
         WHERE ru.id = spl.create_uid AND spl.company_id IS NULL"""
    )


def fill_stock_putaway_rule_location_in_id(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_putaway_rule spr
        SET location_in_id = sl.id
        FROM stock_location sl
        WHERE sl.putaway_strategy_id = spr.putaway_id
            AND spr.location_in_id IS NULL"""
    )
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO stock_putaway_rule (product_id, category_id,
            location_in_id, location_out_id, sequence, company_id,
            create_uid, create_date, write_uid, write_date)
        SELECT spr.product_id, spr.category_id, sl.id, spr.location_out_id,
            spr.sequence, spr.company_id, spr.create_uid, spr.create_date,
            spr.write_uid, spr.write_date
        FROM stock_putaway_rule spr
        JOIN stock_location sl ON sl.putaway_strategy_id = spr.putaway_id
        WHERE spr.location_in_id != sl.id"""
    )


def fill_propagate_date_minimum_delta(env):
    # stock move
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_move sm
        SET propagate_date_minimum_delta = rc.propagation_minimum_delta
        FROM res_company rc
        WHERE sm.company_id = rc.id
            AND rc.propagation_minimum_delta IS NOT NULL"""
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_move sm
        SET propagate_date = TRUE
        FROM ir_config_parameter icp
        WHERE sm.propagate_date IS NULL
            AND icp.key = 'stock.use_propagation_minimum_delta'
            AND icp.value::boolean"""
    )
    # stock rule
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_rule sr
        SET propagate_date_minimum_delta = rc.propagation_minimum_delta
        FROM res_company rc
        WHERE sr.company_id = rc.id
            AND rc.propagation_minimum_delta IS NOT NULL"""
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_rule sr
        SET propagate_date = FALSE
        FROM ir_config_parameter icp
        WHERE sr.propagate_date IS NULL
            AND icp.key = 'stock.use_propagation_minimum_delta'
            AND NOT icp.value::boolean"""
    )


def fill_stock_inventory_start_empty(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_inventory
        SET start_empty = TRUE
        WHERE {} = 'partial'
        """.format(openupgrade.get_legacy_name('filter'))
    )


def map_stock_location_usage(env):
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name('usage'),
        'usage',
        [('procurement', 'transit'),
         ],
        table='stock_location',
    )


def map_stock_picking_responsible_responsible_id_to_user_id(env):
    """
    responsible_id (partner_id) field in stock_picking_responsible is replaced by user_id (res.users)
    We create a deactivated user for partners without user and then
    map the partner to their user in the stock picking.
    """
    if not openupgrade.column_exists(env.cr, "stock_picking", "responsible_id"):
        return

    env.cr.execute(
        f"""
        SELECT distinct rp.id,
                        rp.name,
                        rp.company_id,
                        rp.email
        FROM stock_picking sp
                 JOIN res_partner rp ON rp.id = sp.responsible_id
                 LEFT JOIN res_users ru ON rp.id = ru.partner_id
        WHERE ru.id IS NULL
    """
    )
    partners_wo_user = env.cr.fetchall()

    user_vals_list = []
    for partner_id, name, company_id, email in partners_wo_user:
        login = email if email else name
        login = openupgrade.get_legacy_name(login).replace(" ", "_")
        user_vals_list.append({
            "login": login,
            "partner_id": partner_id,
            "company_id": company_id,
            "active": False,
        })

    if user_vals_list:
        env["res.users"].create(user_vals_list)

    # map responsible_id to user_id
    openupgrade.logged_query(
        env.cr,
        f"""
        WITH partner_user AS (
            SELECT sp.id AS picking_id,
                   rp.id AS partner_id,
                   ru.id AS user_id
            FROM stock_picking sp
                JOIN res_partner rp ON rp.id = sp.responsible_id
                LEFT join res_users ru ON rp.id = ru.partner_id)
        UPDATE stock_picking
        SET user_id = partner_user.user_id
        FROM partner_user
        WHERE stock_picking.id = partner_user.picking_id;
    """
    )


def fill_stock_picking_type_sequence_code(env):
    """Deduce sequence code from current sequence pattern """
    picking_types = env["stock.picking.type"].with_context(active_text=False).search([])
    spt_seq_codes = []
    for picking_type in picking_types:
        prefix = picking_type.sequence_id.prefix
        if picking_type.warehouse_id:
            groups = re.findall(r"(.*)\/(.*)\/", prefix)
            if groups and len(groups[0]) == 2:
                spt_seq_codes += [(picking_type.id, groups[0][1])]
        else:
            spt_seq_codes += [(picking_type.id, prefix)]
    for picking_type_id, prefix in spt_seq_codes:
        env.cr.execute("""
            UPDATE stock_picking_type spt
            SET sequence_code = %s
            WHERE spt.id = %s
            """, (prefix, picking_type_id)
        )


def convert_many2one_stock_inventory_product_and_location(env):
    openupgrade.m2o_to_x2m(
        env.cr,
        env['stock.inventory'], 'stock_inventory',
        'location_ids', openupgrade.get_legacy_name('location_id')
    )
    openupgrade.m2o_to_x2m(
        env.cr,
        env['stock.inventory'], 'stock_inventory',
        'product_ids', openupgrade.get_legacy_name('product_id')
    )


def handle_stock_scrap_sequence(env, main_company):
    # assign on main company
    openupgrade.logged_query(
        env.cr, """
        UPDATE ir_sequence seq
        SET company_id = %s, name = %s || ' Sequence scrap'
        FROM ir_model_data imd
        WHERE imd.res_id = seq.id AND imd.module = 'stock'
            AND imd.name = 'sequence_stock_scrap' AND seq.company_id IS NULL
        """, main_company
    )
    # xmlid is deprecated in v13
    openupgrade.logged_query(env.cr, """
    DELETE FROM ir_model_data imd
    WHERE imd.module = 'stock' AND imd.name = 'sequence_stock_scrap'
    """)
    # force execute this function (it is noupdate=1 in xml data)
    env['res.company'].create_missing_scrap_sequence()


def map_stock_locations(env, main_company):
    # assign properties on main company
    openupgrade.logged_query(
        env.cr, """
        UPDATE ir_property ip
        SET company_id = %s, name = ip.name || '_' || %s
        FROM ir_model_fields imf, stock_location sl
        JOIN ir_model_data imd ON (imd.module = 'stock' AND
            imd.model = 'stock.location' AND imd.res_id = sl.id)
        WHERE ip.fields_id = imf.id AND imf.model = 'product.template' AND
            imf.name IN ('property_stock_inventory',
                'property_stock_production') AND
            imd.name IN ('location_inventory', 'location_production') AND
             ip.value_reference = 'stock.location,' || sl.id
        """, main_company
    )
    # assign locations on main company
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_location sl
        SET company_id = %s, name = %s || ': ' || sl.name
        FROM ir_model_data imd
        WHERE imd.res_id = sl.id AND imd.module = 'stock'
            AND imd.model = 'stock.location'
            AND imd.name IN ('location_inventory', 'location_production', 'stock_location_scrapped')
        """, main_company
    )

    # force execute this functions (they are noupdate=1 in xml data)
    env['res.company'].create_missing_transit_location()
    env['res.company'].create_missing_warehouse()
    env['res.company'].create_missing_inventory_loss_location()
    env['res.company'].create_missing_production_location()
    env['res.company'].create_missing_scrap_location()

    # company of quant is related to company of its location_id
    # but the specific locations we are dealing don't have company!
    # thus, we put temporarily a company from their product/lots
    openupgrade.logged_query(env.cr, """
        UPDATE stock_quant sq
        SET company_id = pt.company_id
        FROM product_product pp
        JOIN product_template pt ON pp.product_tmpl_id = pt.id
        WHERE sq.product_id = pp.id AND pt.company_id IS NOT NULL
            AND sq.company_id IS NULL""")
    openupgrade.logged_query(env.cr, """
        UPDATE stock_quant sq
        SET company_id = ppl.company_id
        FROM stock_production_lot ppl
        WHERE sq.lot_id = ppl.id AND sq.company_id IS NULL""")

    conditions = {
        'location_inventory':
            "sl2.usage = 'inventory' AND sl2.scrap_location IS NOT TRUE",
        'location_production': "sl2.usage = 'production'",
        'stock_location_scrapped':
            "sl2.usage = 'inventory' AND sl2.scrap_location IS TRUE",
    }
    affected_models = {
        'ir.property': ['value_reference'],  # special case
        'stock.picking': ['location_id', 'location_dest_id'],
        'stock.move': ['location_id', 'location_dest_id'],
        'stock.move.line': ['location_id', 'location_dest_id'],
        'stock.inventory': [openupgrade.get_legacy_name('location_id')],
        'stock.putaway.rule': ['location_in_id', 'location_out_id'],
        'stock.scrap': ['scrap_location_id'],
        'stock.rule': ['location_src_id', 'location_id'],
        'stock.warehouse.orderpoint': ['location_id'],
        'stock.quant': ['location_id'],
    }
    for model, locations in affected_models.items():
        table = env[model]._table
        for location in locations:
            value = ""
            if model == "ir.property":
                value = "'stock.location,' || "
            for xmlid_name, condition in conditions.items():
                openupgrade.logged_query(
                    env.cr, """
        UPDATE {table} tab
        SET {location} = {value}(
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
        WHERE tab.{location} = {value}sl.id AND
            tab.company_id != {main_company_id} AND
            imd.name = '{xmlid_name}'
                    """.format(table=table, main_company_id=main_company[0],
                               location=location, value=value,
                               xmlid_name=xmlid_name, condition=condition)
                )

    # Update related / computed fields
    openupgrade.logged_query(env.cr, """
        UPDATE stock_quant sq
        SET company_id = sl.company_id
        FROM stock_location sl
        WHERE sq.location_id = sl.id""")
    env["stock.quant.package"].search([])._compute_package_info()


def stock_production_lot_multi_company_migration(env):
    rule = env.ref("stock.stock_production_lot_rule", raise_if_not_found=False)
    if 'user' in rule.domain_force:
        rule.write({"name": "Stock Production Lot multi-company",
                    "domain_force": "[('company_id','in', company_ids)]"})


def stock_putaway_rule_multi_company_migration(env):
    # once location_in_id is correctly set and company of locations are correctly set
    # in previous methods, we can safely proceed with:
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_putaway_rule spr
        SET company_id = sl.company_id
        FROM stock_location sl
        WHERE spr.location_in_id = sl.id AND sl.company_id IS NOT NULL"""
    )


def recompute_stock_location_complete_name(env):
    # In 12.0, the displayed name of the locations was obtained by the
    # name_get method. This method limited the location path up to a parent
    # location of type view is found. In 13.0, complete_name is used for
    # this purpose, and this one used to be stored with full path in v12.
    # We need to recompute it.
    locations = env["stock.location"].search([])
    locations._compute_complete_name()


def update_sml_index(env):
    # As company_id is a new indexed column for stock_move_line we must update
    # the index according to the upstream config.
    openupgrade.logged_query(
        env.cr,
        "DROP INDEX stock_move_line_free_reservation_index"
    )
    openupgrade.logged_query(
        env.cr,
        """
        CREATE INDEX stock_move_line_free_reservation_index
        ON
            stock_move_line (
                id, company_id, product_id, lot_id,
                location_id, owner_id, package_id
            )
        WHERE
            (state IS NULL OR state NOT IN ('cancel', 'done'))
            AND product_qty > 0"""
    )


@openupgrade.migrate()
def migrate(env, version):
    main_company = _get_main_company(env.cr)
    fill_company_id(env.cr)
    fill_stock_putaway_rule_location_in_id(env)
    fill_propagate_date_minimum_delta(env)
    fill_stock_inventory_start_empty(env)
    map_stock_location_usage(env)
    map_stock_picking_responsible_responsible_id_to_user_id(env)
    fill_stock_picking_type_sequence_code(env)
    handle_stock_scrap_sequence(env, main_company)
    map_stock_locations(env, main_company)
    convert_many2one_stock_inventory_product_and_location(env)
    openupgrade.load_data(env.cr, 'stock', 'migrations/13.0.1.1/noupdate_changes.xml')
    stock_production_lot_multi_company_migration(env)
    stock_putaway_rule_multi_company_migration(env)
    if openupgrade.table_exists(env.cr, 'delivery_carrier'):
        openupgrade.load_data(
            env.cr, "stock", "migrations/13.0.1.1/noupdate_changes2.xml")
        # This mail.template came from the module delivery to stock, so the translated
        # terms will have the old module set. We need to change it so we can delete
        # the translations properly
        template = env.ref("stock.mail_template_data_delivery_confirmation")
        env["ir.translation"].search(
            [
                ("name", "ilike", "mail.template,"), ("res_id", "=", template.id)
            ]
        ).module = "stock"
        openupgrade.delete_record_translations(
            env.cr, 'stock', [
                'mail_template_data_delivery_confirmation',
            ],
        )
    recompute_stock_location_complete_name(env)
    update_sml_index(env)
