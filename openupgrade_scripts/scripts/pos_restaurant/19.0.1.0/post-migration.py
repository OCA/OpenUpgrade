# Copyright 2026 Heliconia Solutions Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _column_exists(cr, table_name, column_name):
    cr.execute(
        """
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = %s AND column_name = %s
        )
        """,
        (table_name, column_name),
    )
    return cr.fetchone()[0]


def _check_legacy_columns(cr):
    return {
        "order_takeaway": _column_exists(cr, "pos_order", "takeaway"),
        "self_takeaway": _column_exists(cr, "pos_config", "self_ordering_takeaway"),
        "rest_takeaway": _column_exists(cr, "pos_config", "takeaway"),
        "fp_id": _column_exists(cr, "pos_config", "takeaway_fp_id"),
        "service_mode": _column_exists(cr, "pos_config", "self_ordering_service_mode"),
        "preset_self": _column_exists(cr, "pos_preset", "available_in_self"),
    }


def _was_takeaway_enabled(cr, config_id, cols):
    was_self = False
    was_rest = False
    if cols["self_takeaway"]:
        cr.execute(
            "SELECT self_ordering_takeaway FROM pos_config WHERE id = %s",
            (config_id,),
        )
        row = cr.fetchone()
        if row and row[0]:
            was_self = True
    if cols["rest_takeaway"]:
        cr.execute("SELECT takeaway FROM pos_config WHERE id = %s", (config_id,))
        row = cr.fetchone()
        if row and row[0]:
            was_rest = True
    return was_self, (was_self or was_rest)


def _resolve_config_takeout_preset(env, config, takeout_preset, cols):
    if not takeout_preset:
        return None

    was_self_takeaway, is_enabled = _was_takeaway_enabled(env.cr, config.id, cols)
    if not is_enabled:
        return None

    config_takeout_preset = takeout_preset
    created_new_preset = False

    if cols["fp_id"]:
        env.cr.execute(
            "SELECT takeaway_fp_id FROM pos_config WHERE id = %s",
            (config.id,),
        )
        fp_row = env.cr.fetchone()
        fp_id = fp_row[0] if fp_row else None
        if fp_id:
            takeout_preset.invalidate_recordset(["fiscal_position_id"])
            current_fp_id = takeout_preset.fiscal_position_id.id
            if not current_fp_id:
                takeout_preset.write({"fiscal_position_id": fp_id})
            elif current_fp_id != fp_id:
                config_takeout_preset = env["pos.preset"].create(
                    {
                        "name": f"Takeout ({config.name})",
                        "fiscal_position_id": fp_id,
                    }
                )
                created_new_preset = True

    if cols["preset_self"]:
        if created_new_preset:
            env.cr.execute(
                "UPDATE pos_preset SET available_in_self = %s WHERE id = %s",
                (was_self_takeaway, config_takeout_preset.id),
            )
        elif was_self_takeaway:
            # One-way OR ratchet: keep available_in_self = True if any config needs it
            env.cr.execute(
                "UPDATE pos_preset SET available_in_self = TRUE WHERE id = %s",
                (takeout_preset.id,),
            )

    return config_takeout_preset


def _determine_default_preset(
    config, service_mode, presets_to_add, takeout_preset, takein_preset
):
    if (
        service_mode == "counter"
        and takeout_preset
        and takeout_preset.id in presets_to_add
    ):
        return takeout_preset
    if service_mode == "table" and takein_preset and takein_preset.id in presets_to_add:
        return takein_preset
    return config.env["pos.preset"].browse(presets_to_add[0])


def _update_config_presets(
    env, config, takein_preset, takeout_preset, delivery_preset, cols
):
    if config.available_preset_ids:
        return None

    config_takeout_preset = _resolve_config_takeout_preset(
        env, config, takeout_preset, cols
    )
    presets_to_add = []
    if takein_preset:
        presets_to_add.append(takein_preset.id)
    if delivery_preset:
        presets_to_add.append(delivery_preset.id)
    if config_takeout_preset:
        presets_to_add.append(config_takeout_preset.id)

    if not presets_to_add:
        return config_takeout_preset

    vals = {"available_preset_ids": [(6, 0, presets_to_add)]}
    if not config.default_preset_id:
        service_mode = getattr(config, "self_ordering_service_mode", None)
        if not service_mode and cols["service_mode"]:
            env.cr.execute(
                "SELECT self_ordering_service_mode FROM pos_config WHERE id = %s",
                (config.id,),
            )
            sm_row = env.cr.fetchone()
            if sm_row:
                service_mode = sm_row[0]

        default_preset = _determine_default_preset(
            config,
            service_mode,
            presets_to_add,
            config_takeout_preset,
            takein_preset,
        )
        vals["default_preset_id"] = default_preset.id

    config.write(vals)
    return config_takeout_preset


def link_presets_and_migrate_takeaway(env):
    """Link presets to existing pos.config records and migrate legacy
    takeaway settings and orders from 18.0 to 19.0.
    """
    takein = env.ref("pos_restaurant.pos_takein_preset", raise_if_not_found=False)
    takeout = env.ref("pos_restaurant.pos_takeout_preset", raise_if_not_found=False)
    delivery = env.ref("pos_restaurant.pos_delivery_preset", raise_if_not_found=False)
    cols = _check_legacy_columns(env.cr)

    for config in env["pos.config"].search([]):
        config_takeout = _update_config_presets(
            env, config, takein, takeout, delivery, cols
        )

        if cols["order_takeaway"] and config_takeout:
            openupgrade.logged_query(
                env.cr,
                """
                UPDATE pos_order
                SET preset_id = %s
                WHERE config_id = %s
                  AND takeaway IS TRUE
                  AND preset_id IS NULL
                """,
                (config_takeout.id, config.id),
            )


@openupgrade.migrate()
def migrate(env, version):
    link_presets_and_migrate_takeaway(env)
