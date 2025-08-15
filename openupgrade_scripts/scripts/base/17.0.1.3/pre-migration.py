# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

from odoo import tools

from odoo.addons.openupgrade_scripts.apriori import (  # pylint: disable=odoo-addons-relative-import
    merged_modules,
    renamed_modules,
)

_logger = logging.getLogger(__name__)

_xmlids_renames = [
    (
        "mail.model_res_users_settings",
        "base.model_res_users_settings",
    ),
    (
        "mail.access_res_users_settings_all",
        "base.access_res_users_settings_all",
    ),
    (
        "mail.access_res_users_settings_user",
        "base.access_res_users_settings_user",
    ),
    (
        "mail.res_users_settings_rule_admin",
        "base.res_users_settings_rule_admin",
    ),
    (
        "mail.res_users_settings_rule_user",
        "base.res_users_settings_rule_user",
    ),
    (
        "mail.constraint_res_users_settings_unique_user_id",
        "base.constraint_res_users_settings_unique_user_id",
    ),
]
_column_renames = {
    "res_partner": [("display_name", "complete_name")],
}


def _handle_l10n_de_mis_reports_xmlids(cr):
    """Before executing the merged modules, we need to rename some XML-IDs with the same
    name of l10n_de_skr03_mis_reports/l10n_de_skr04_mis_reports into
    l10n_de_mis_reports.
    """
    if not openupgrade.is_module_installed(
        cr, "l10n_de_skr03_mis_reports"
    ) and not openupgrade.is_module_installed(cr, "l10n_de_skr04_mis_reports"):
        return
    _xmlids_renames = []
    # fmt: off
    bs_names = ["anlagevermoegen", "immaterielle", "schutzrechte", "konzessionen", "firmenwert", "geleistetet_anzahlungen", "total_immaterielle", "grundstueck", "maschinen", "ausstattung", "anlagen_im_bau", "total_sachanlagen", "anteile", "ausleihungen", "beteiligungen", "ausleihungen_beteiligung", "wertpapiere_av", "sonstige_ausleihungen", "total_finanzanlagen", "total_anlagevermoegen", "umlaufvermoegen", "i_vorraete", "roh_hilfs_betriebsstoffe", "unfertige_leistungen", "fertige_erzeugnisse", "anzahlungen", "total_vorraete", "ii_forderungen", "forderungen_ll", "forderungen_unternehmen", "forderungen_beteiligungen", "total_forderungen", "iii_wertpapiere", "wertpapiere_uv_anteile", "wertpapiere_uv_sonstige", "total_wertpapiere_uv", "liquide_mittel", "total_umlaufvermoegen", "rechnungsabgrenzung_aktiva", "aktive_latente_steuern", "fehlbetrag", "aktivseite", "eigenkapital", "gezeichnetes_kapital", "variables_kapital", "gewinnruecklage", "ruecklage_gesetzlich", "ruecklage_eigene_anteile", "ruecklage_satzung", "ruecklage_andere_gewinne", "gewinn_des_jahres", "total_gewinnruecklage", "gewinn_verlustvortrag", "jahresgewinn_verlust", "sopo_mit_ruecklage", "total_eigenkapital", "rueckstellungen", "rueckstellungen_pensionen", "rueckstellungen_steuern", "rueckstellungen_sonstige", "total_rueckstellungen", "verbindlichkeiten", "verbindlichkeiten_anleihen", "verbindlichkeiten_bank", "verbindlichkeiten_ll", "verbindlichkeiten_wechsel", "verbindlichkeiten_sonstige", "total_verbindlichkeiten", "rechnungsabgrenzung_passiva", "passive_latente_steuern", "passivseite"]  # noqa: E501
    pl_names = ["betriebliche_erloese", "umsatzerloese", "bestandsveraenderungen", "eigenleistungen", "sonstige_ertraege", "total_erloese", "betriebsaufwand", "materialaufwand", "materialaufwand_a", "materialaufwand_b", "personalaufwand", "personalaufwand_a", "personalaufwand_b", "abschreibungen", "abschreibungen_a", "abschreibungen_b", "sonstige_aufwendungen", "total_aufwendungen", "total_betriebsergebnis", "ertraege_beteiligungen", "ertraege_wertpapiere", "zinsertraege", "zinsaufwendungen", "ergebnis_gewoehnliche", "ao_ergebnis", "ao_ergebnis_erloese", "ao_ergebnis_aufwendungen", "total_ao_ergebnis", "steuern", "steuern_ertrag", "sonstige_steuern", "gewinn_verlust", "gewinnvortrag_vj", "entnahme_kapitalruecklage", "entnahme_gewinnruecklage", "einstellung_ruecklage", "bilanzgewinn"]  # noqa: E501
    # fmt: on
    for coa in ("skr03", "skr04"):
        for report in ("mis_report_bs", "mis_report_pl"):
            for name in [""] + bs_names + pl_names:
                _xmlids_renames.append(
                    (
                        f"l10n_de_{coa}_mis_reports.{report}{'_' if name else ''}{name}",  # noqa: E501
                        f"l10n_de_mis_reports.{report}_{coa}{'_' if name else ''}{name}",  # noqa: E501
                    )
                )
    openupgrade.rename_xmlids(cr, _xmlids_renames)


def _fill_ir_server_object_lines_into_action_server(cr):
    openupgrade.logged_query(
        cr,
        """
        ALTER TABLE ir_act_server
            ADD COLUMN IF NOT EXISTS old_ias_id INTEGER,
            ADD COLUMN IF NOT EXISTS evaluation_type VARCHAR,
            ADD COLUMN IF NOT EXISTS resource_ref VARCHAR,
            ADD COLUMN IF NOT EXISTS selection_value INTEGER,
            ADD COLUMN IF NOT EXISTS update_boolean_value VARCHAR,
            ADD COLUMN IF NOT EXISTS update_field_id INTEGER,
            ADD COLUMN IF NOT EXISTS update_m2m_operation VARCHAR,
            ADD COLUMN IF NOT EXISTS update_path VARCHAR,
            ADD COLUMN IF NOT EXISTS update_related_model_id INTEGER,
            ADD COLUMN IF NOT EXISTS value TEXT;
        """,
    )
    # Update operations
    openupgrade.logged_query(
        cr,
        """
        WITH sub AS (
            INSERT INTO ir_act_server
            (
                old_ias_id,
                evaluation_type,
                update_field_id,
                update_path,
                update_related_model_id,
                value,
                resource_ref,
                selection_value,
                update_boolean_value,
                update_m2m_operation,
                binding_type,
                state,
                type,
                usage,
                model_id,
                name
            )
            SELECT
                ias.id,
                CASE
                    WHEN isol.evaluation_type = 'equation' then 'equation'
                    ELSE 'value'
                END,
                imf.id,
                imf.name,
                im.id,
                CASE WHEN isol.evaluation_type = 'equation'
                    THEN isol.value
                    ELSE NULL
                END,
                CASE WHEN imf.ttype in ('many2one', 'many2many')
                    THEN imf.relation || ',' || isol.value
                    ELSE NULL
                END,
                imfs.id,
                CASE WHEN imf.ttype = 'boolean'
                    THEN isol.value::bool
                    ELSE NULL
                END,
                'add',
                'action',
                'object_write',
                'ir.actions.server',
                'ir_actions_server',
                ias.model_id,
                ias.name
            FROM ir_act_server ias
            JOIN ir_server_object_lines isol ON isol.server_id = ias.id
            JOIN ir_model_fields imf ON imf.id = isol.col1
            LEFT JOIN ir_model im ON im.model = imf.relation
            LEFT JOIN ir_model_fields_selection imfs
                ON imf.id = imfs.field_id AND imfs.value = isol.value
            WHERE ias.state = 'object_write'
            RETURNING id, old_ias_id
        )
        INSERT INTO rel_server_actions (action_id, server_id)
        SELECT sub.id as action_id, sub.old_ias_id as server_id
        FROM sub
        """,
    )
    openupgrade.logged_query(
        cr,
        """UPDATE ir_act_server ias
        SET state = 'multi'
        FROM ir_server_object_lines isol
        WHERE ias.state = 'object_write'
        AND isol.server_id = ias.id
        """,
    )
    # Create operations
    openupgrade.logged_query(
        cr,
        """UPDATE ir_act_server ias
        SET value = isol.value
        FROM ir_server_object_lines isol
        JOIN ir_model_fields imf ON imf.id = isol.col1
        WHERE ias.state = 'object_create'
        AND isol.server_id = ias.id
        AND isol.evaluation_type = 'value'
        AND imf.name = 'name'
        """,
    )


def _fill_empty_country_codes(cr):
    openupgrade.logged_query(
        cr,
        """
        WITH dummy_codes AS (
            SELECT LPAD(i::text, 2, '0') AS code
            FROM generate_series(0, 99) AS i
        ),
        available_codes AS (
            SELECT dc.code, ROW_NUMBER() OVER () AS rn
            FROM dummy_codes dc
            LEFT JOIN res_country rc ON rc.code = dc.code
            WHERE rc.code IS NULL
        ),
        null_countries AS (
            SELECT id, ROW_NUMBER() OVER () AS rn
            FROM res_country
            WHERE code IS NULL
        )
        UPDATE res_country AS rc
        SET code = ac.code
        FROM available_codes ac
        JOIN null_countries nc ON nc.rn = ac.rn
        WHERE rc.id = nc.id
        """,
    )


def _handle_partner_private_type(cr):
    # Copy private records into a new table
    openupgrade.logged_query(
        cr,
        """
        CREATE TABLE ou_res_partner_private AS
        SELECT * FROM res_partner
        WHERE type = 'private'
        """,
    )
    # Copy column for preserving the old type values
    _column_copies = {"res_partner": [("type", None, None)]}
    openupgrade.copy_columns(cr, _column_copies)
    # Change contact type and erase sensitive information
    query = "type = 'contact'"
    for field in [
        "street",
        "street2",
        "city",
        "zip",
        "vat",
        "function",
        "phone",
        "mobile",
        "email",
        "website",
        "comment",
    ]:
        query += f", {field} = CASE WHEN {field} IS NULL THEN NULL ELSE '*****' END"
    openupgrade.logged_query(
        cr,
        f"""
        UPDATE res_partner
        SET {query},
        country_id = NULL,
        state_id = NULL
        WHERE type = 'private'
        """,
    )


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    """
    Don't request an env for the base pre-migration as flushing the env in
    odoo/modules/registry.py will break on the 'base' module not yet having
    been instantiated.
    """
    if "openupgrade_framework" not in tools.config["server_wide_modules"]:
        _logger.error(
            "openupgrade_framework is not preloaded. You are highly "
            "recommended to run the Odoo with --load=openupgrade_framework "
            "when migrating your database."
        )
    openupgrade.update_module_names(cr, renamed_modules.items())
    _handle_l10n_de_mis_reports_xmlids(cr)
    openupgrade.update_module_names(cr, merged_modules.items(), merge_modules=True)
    openupgrade.clean_transient_models(cr)
    openupgrade.rename_xmlids(cr, _xmlids_renames)
    openupgrade.rename_columns(cr, _column_renames)
    _fill_ir_server_object_lines_into_action_server(cr)
    _fill_empty_country_codes(cr)
    _handle_partner_private_type(cr)
