# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

from odoo import models

from odoo.addons.base.models.ir_property import TYPE2FIELD as ir_property_TYPE2FIELD

_deleted_xml_records = [
    "account.tax_group_taxes",
    "account.account_invoice_send_rule_group_invoice",
    "account.sequence_reconcile_seq",
]


COA_MAPPING = {
    "l10n_ae.uae_chart_template_standard": "ae",
    "l10n_ar.l10nar_base_chart_template": "ar_base",
    "l10n_ar.l10nar_ex_chart_template": "ar_ex",
    "l10n_ar.l10nar_ri_chart_template": "ar_ri",
    "l10n_at.l10n_at_chart_template": "at",
    "l10n_au.l10n_au_chart_template": "au",
    "l10n_be.l10nbe_chart_template": "be_comp",
    "l10n_bg.l10n_bg_chart_template": "bg",
    "l10n_bo.bo_chart_template": "bo",
    "l10n_br.l10n_br_account_chart_template": "br",
    "l10n_ca.ca_en_chart_template_en": "ca_2023",
    "l10n_ch.l10nch_chart_template": "ch",
    "l10n_cl.cl_chart_template": "cl",
    "l10n_cn.l10n_chart_china_small_business": "cn",
    "l10n_co.l10n_co_chart_template_generic": "co",
    "l10n_cr.account_chart_template_0": "cr",
    "l10n_cz.cz_chart_template": "cz",
    "l10n_de.l10n_de_chart_template": "de_skr03",
    "l10n_de.l10n_chart_de_skr04": "de_skr04",
    "l10n_de_skr03.l10n_de_chart_template": "de_skr03",
    "l10n_de_skr04.l10n_chart_de_skr04": "de_skr04",
    "l10n_dk.dk_chart_template": "dk",
    "l10n_do.do_chart_template": "do",
    "l10n_dz.l10n_dz_pcg_chart_template": "dz",
    "l10n_ec.l10n_ec_ifrs": "ec",
    "l10n_ee.l10nee_chart_template": "ee",
    "l10n_eg.egypt_chart_template_standard": "eg",
    "l10n_es.account_chart_template_assoc": "es_assec",
    "l10n_es.account_chart_template_common": "es_common",
    "l10n_es.account_chart_template_full": "es_full",
    "l10n_es.account_chart_template_pymes": "es_pymes",
    "l10n_et.l10n_et": "et",
    "l10n_fi.fi_chart_template": "fi",
    "l10n_fr.l10n_fr_pcg_chart_template": "fr",
    "l10n_generic_coa.configurable_chart_template": "generic_coa",
    "l10n_gr.l10n_gr_chart_template": "gr",
    "l10n_gt.cuentas_plantilla": "gt",
    "l10n_hk.l10n_hk_chart_template": "hk",
    "l10n_hn.cuentas_plantilla": "hn",
    "l10n_hr.l10n_hr_chart_template_rrif": "hr",
    "l10n_hr.l10n_hr_euro_chart_template": "hr",
    "l10n_hr_kuna.l10n_hr_kuna_chart_template_rrif": "hr_kuna",
    "l10n_hu.hungarian_chart_template": "hu",
    "l10n_id.l10n_id_chart": "id",
    "l10n_ie.l10n_ie": "ie",
    "l10n_il.il_chart_template": "il",
    "l10n_in.indian_chart_template_standard": "in",
    "l10n_it.l10n_it_chart_template_generic": "it",
    "l10n_jp.l10n_jp1": "jp",
    "l10n_jp.l10n_jp_chart_template": "jp",
    "l10n_ke.l10nke_chart_template": "ke",
    "l10n_kz.l10nkz_chart_template": "kz",
    "l10n_lt.account_chart_template_lithuania": "lt",
    "l10n_lu.lu_2011_chart_1": "lu",
    "l10n_lv.chart_template_latvia": "lv",
    "l10n_ma.l10n_ma_chart_template": "ma",
    "l10n_mn.mn_chart_1": "mn",
    "l10n_mx.mx_coa": "mx",
    "l10n_my.l10n_my_chart_template": "my",
    "l10n_mz.l10n_mz_chart_template": "mz",
    "l10n_nl.l10nnl_chart_template": "nl",
    "l10n_no.no_chart_template": "no",
    "l10n_nz.l10n_nz_chart_template": "nz",
    "l10n_pa.l10npa_chart_template": "pa",
    "l10n_pe.pe_chart_template": "pe",
    "l10n_ph.l10n_ph_chart_template": "ph",
    "l10n_pk.l10n_pk_chart_template": "pk",
    "l10n_pl.pl_chart_template": "pl",
    "l10n_pt.pt_chart_template": "pt",
    "l10n_ro.ro_chart_template": "ro",
    "l10n_rs.l10n_rs_chart_template": "rs",
    "l10n_sa.sa_chart_template_standard": "sa",
    "l10n_se.l10nse_chart_template": "se",
    "l10n_se.l10nse_chart_template_K2": "se_K2",
    "l10n_se.l10nse_chart_template_K3": "se_K3",
    "l10n_sg.sg_chart_template": "sg",
    "l10n_si.gd_chart": "si",
    "l10n_sk.sk_chart_template": "sk",
    "l10n_syscohada.syscohada_chart_template": "syscohada",
    "l10n_th.chart": "th",
    "l10n_tr.chart_template_common": "tr",
    "l10n_tr.l10n_tr_chart_template": "tr",
    "l10n_tw.l10n_tw_chart_template": "tw",
    "l10n_ua.l10n_ua_ias_chart_template": "ua_ias",
    "l10n_ua.l10n_ua_psbo_chart_template": "ua_psbo",
    "l10n_uk.l10n_uk": "uk",
    "l10n_uy.uy_chart_template": "uy",
    "l10n_ve.ve_chart_template_amd": "ve",
    "l10n_vn.vn_template": "vn",
    "l10n_za.default_chart_template": "za",
}


def _am_update_invoice_pdf_report_file(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_attachment ia
        SET res_field = 'invoice_pdf_report_file',
            res_id = am.id
        FROM account_move am
        WHERE am.message_main_attachment_id = ia.id
        """,
    )


def _onboarding_state_migration(env):
    """
    Following pr: https://github.com/odoo/odoo/pull/104223/
    """
    env.cr.execute(
        """
        SELECT id, account_onboarding_create_invoice_state_flag,
        account_onboarding_invoice_layout_state,
        account_onboarding_sale_tax_state, account_setup_bank_data_state,
        account_setup_bill_state, account_setup_coa_state, account_setup_fy_data_state,
        account_setup_taxes_state FROM res_company
        """
    )
    for (
        company_id,
        account_onboarding_create_invoice_state_flag,
        account_onboarding_invoice_layout_state,
        account_onboarding_sale_tax_state,
        account_setup_bank_data_state,
        account_setup_bill_state,
        account_setup_coa_state,
        account_setup_fy_data_state,
        account_setup_taxes_state,
    ) in env.cr.fetchall():
        OnboardingStep = env["onboarding.onboarding.step"].with_company(company_id)
        company = env["res.company"].browse(company_id)
        if company.street and company.street.strip():
            # Same behaviour for this base setup company data in v16
            # Check method 'action_save_onboarding_company_step' in v16
            # Note in v17 you only need to save it then it will be done
            OnboardingStep.action_validate_step(
                "account.onboarding_onboarding_step_company_data"
            )
        if account_onboarding_create_invoice_state_flag:
            step = env.ref(
                "account.onboarding_onboarding_step_create_invoice",
                raise_if_not_found=False,
            )
            if step and step.current_step_state == "not_done":
                if env["account.move"].search(
                    [
                        ("company_id", "=", company_id),
                        ("move_type", "=", "out_invoice"),
                    ],
                    limit=1,
                ):
                    step.with_company(company_id).action_set_just_done()
        if account_onboarding_invoice_layout_state in ("just_done", "done"):
            step = env.ref(
                "account.onboarding_onboarding_step_base_document_layout",
                raise_if_not_found=False,
            )
            if step:
                step.with_company(company_id).action_set_just_done()
        if account_onboarding_sale_tax_state in ("just_done", "done"):
            OnboardingStep.action_validate_step(
                "account.onboarding_onboarding_step_sales_tax"
            )
        if account_setup_bank_data_state in ("just_done", "done"):
            OnboardingStep.action_validate_step(
                "account.onboarding_onboarding_step_bank_account"
            )
        if account_setup_bill_state in ("just_done", "done"):
            OnboardingStep.action_validate_step(
                "account.onboarding_onboarding_step_setup_bill"
            )
        if account_setup_coa_state in ("just_done", "done"):
            OnboardingStep.action_validate_step(
                "account.onboarding_onboarding_step_chart_of_accounts"
            )
        if account_setup_fy_data_state in ("just_done", "done"):
            OnboardingStep.action_validate_step(
                "account.onboarding_onboarding_step_fiscal_year"
            )
        if account_setup_taxes_state in ("just_done", "done"):
            OnboardingStep.action_validate_step(
                "account.onboarding_onboarding_step_default_taxes"
            )


def _account_payment_term_migration(env):
    """
    Switch balance lines to percent and compute the remaining percentage, and convert
    old multiple column system to the new delay_type + nb_days.

    https://github.com/odoo/odoo/pull/110274
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_payment_term_line
        SET value = 'percent',
            value_amount = 100.0 - COALESCE(percentages.percentage, 0)
        FROM (
            SELECT
                payment_id,
                SUM(
                    CASE WHEN l.value='percent' THEN l.value_amount
                    ELSE 0 END
                ) percentage
            FROM account_payment_term_line l
            GROUP BY payment_id
        ) percentages
        WHERE
        value = 'balance' AND
        percentages.payment_id = account_payment_term_line.payment_id
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_payment_term_line
        SET delay_type = CASE
            WHEN end_month AND COALESCE(months, 0) = 0
                AND COALESCE(days, 0) = 0
                THEN 'days_after_end_of_month'
            WHEN end_month AND months = 1 AND COALESCE(days, 0) = 0
                THEN 'days_after_end_of_next_month'
            WHEN end_month AND COALESCE(months, 0) <= 1 AND days > 0
                THEN 'days_end_of_month_on_the'
            ELSE 'days_after'
        END,
        nb_days = CASE
            WHEN end_month AND months <= 1
                THEN COALESCE(days, 0) + COALESCE(days_after, 0)
            ELSE
                COALESCE(months, 0)*30 + COALESCE(days, 0) +
                COALESCE(days_after, 0)
        END
        """,
    )


def _account_payment_term_early_payment_discount(env):
    """Only payment terms with one line and the early payment discount activated are
    valid now, so we are going to discard other previous configurations.
    """
    openupgrade.logged_query(
        env.cr,
        """
        WITH sub AS (
            SELECT * FROM (
                SELECT *,
                    row_number() over (partition BY payment_id ORDER BY id) AS rnum
                FROM account_payment_term_line
            ) t
            WHERE t.rnum = 1
            AND t.discount_days IS NOT NULL
            AND t.discount_percentage > 0
        )
        UPDATE account_payment_term apt
        SET early_discount = True,
            discount_days = sub.discount_days,
            discount_percentage = sub.discount_percentage
        FROM sub
        WHERE sub.payment_id = apt.id
        """,
    )


def convert_from_company_dependent(
    env,
    model_name,
    origin_field_name,
    destination_field_name,
    origin_id_column_name,
    model_table_name=None,
):
    """
    Move a company-dependent field back to the model table.

    The usual setting is: A model didn't have a company_id field in version
    (n-1), but got company-aware in version (n). Then company-dependent fields
    don't make sense, and are replaced with plain database columns.

    You're responsible for duplicating records for all companies in whatever way
    makes sense for the model before calling this function, and link the
    duplicate to the original record in column `origin_id_column_name`, which
    you have to create yourself beforehand.

    :param model_name: Name of the model.
    :param origin_field_name: Name of the company-dependent field
    :param destination_field_name: Name of plain field
    :param origin_id_column_name: Name of the column you created to link record
      duplicates to the record they were duplicated from
    :param model_table_name: Name of the table. Optional. If not provided
      the table name is taken from the model (so the model must be
      registered previously).
    """
    # If you want to recycle this function for your own migration, better
    # add it to openupgradelib
    table_name = model_table_name or env[model_name]._table

    env.cr.execute(
        "SELECT id, ttype FROM ir_model_fields "
        f"WHERE model='{model_name}' AND name='{origin_field_name}'"
    )
    field_id, field_type = env.cr.fetchone()

    value_expression = ir_property_TYPE2FIELD.get(field_type)
    if value_expression == "value_reference":
        value_expression = "SPLIT_PART(ip.value_reference, ',', 2)::integer"

    return openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE {table_name}
        SET {destination_field_name} = (
            SELECT {value_expression}
            FROM ir_property ip
            WHERE ip.fields_id={field_id} --- {origin_field_name}
            AND (
                ip.res_id = '{model_name}.' || COALESCE(
                    {table_name}.{origin_id_column_name}, {table_name}.id
                )
                OR ip.res_id IS NULL
            )
            AND (
                ip.company_id = {table_name}.company_id
                OR ip.company_id IS NULL
            )
            ORDER BY ip.company_id NULLS LAST, ip.res_id NULLS LAST
            LIMIT 1
        )
        """,
    )


def _account_tax_group_migration(env):
    """
    In v17 tax groups are company-aware (company_id added):

    - Find which tax groups have accounts with different companies,
      duplicate them for each of that company
    - Update accounts to point to the newly created groups for their
      companies
    - Rename ir model data (xml_id), the format will be
      "{module_name}.{company_id}_xml_id"
    - Fill new fields tax_receivable_account_id, tax_payable_account_id,
      advance_tax_payment_account_id with the value of the properties
      they replace

    Example in v16:
    2 VN CoA company: tax 0, tax 5, tax 10
    2 Generic CoA company tax 15
    1 Belgium CoA company tax 6, 12, 21

    -> After migration we will have 2 tax 0, 2 tax 5, 2 tax 10
    and 2 tax 15 of course with only different company_id
    Also the new one will have their own xml_id using create method
    of ir.model.data
    And then in each l10n module, only need to perform rename xml_id like
    https://github.com/Viindoo/OpenUpgrade/pull/655
    """
    origin_id_column = "original_tax_group_id"
    openupgrade.logged_query(
        env.cr,
        f"""
        ALTER TABLE account_tax_group
            ADD COLUMN IF NOT EXISTS {origin_id_column} INTEGER;
        """,
    )

    env.cr.execute(
        """
        SELECT tax_group_id, array_agg(DISTINCT(company_id))
            FROM account_tax
        GROUP BY tax_group_id
        """
    )

    for tax_group_id, company_ids in env.cr.fetchall():
        tax_group = env["account.tax.group"].browse(tax_group_id)
        first_company_id = min(company_ids)
        tax_group.company_id = first_company_id

        imd = env["ir.model.data"].search(
            [("res_id", "=", tax_group.id), ("model", "=", "account.tax.group")],
            limit=1,
        )
        tax_group_name = imd.name
        imd.write(
            {
                "name": f"{first_company_id}_{imd.name}",
                "noupdate": True,
                "module": "account",
            }
        )
        for company_id in company_ids:
            if company_id == first_company_id:
                continue
            new_tax_group = tax_group.copy({"company_id": company_id})

            openupgrade.logged_query(
                env.cr,
                f"""
                UPDATE account_tax_group
                SET {origin_id_column} = {tax_group.id}
                WHERE id = {new_tax_group.id}
                """,
            )

            if tax_group_name:
                models.BaseModel.copy(
                    imd,
                    {
                        "res_id": new_tax_group.id,
                        "name": f"{company_id}_{tax_group_name}",
                    },
                )

            openupgrade.logged_query(
                env.cr,
                f"""
                UPDATE account_tax
                SET tax_group_id = {new_tax_group.id}
                WHERE tax_group_id = {tax_group.id} AND company_id = {company_id}
                """,
            )

    convert_from_company_dependent(
        env,
        "account.tax.group",
        "property_tax_receivable_account_id",
        "tax_receivable_account_id",
        origin_id_column,
    )
    convert_from_company_dependent(
        env,
        "account.tax.group",
        "property_tax_payable_account_id",
        "tax_payable_account_id",
        origin_id_column,
    )
    convert_from_company_dependent(
        env,
        "account.tax.group",
        "property_advance_tax_payment_account_id",
        "advance_tax_payment_account_id",
        origin_id_column,
    )


def _force_install_account_payment_term_module_module(env):
    """
    Force install account_payment_term if we need
    key 'days_end_of_month_on_the' of it
    it has already merged in odoo master
    """
    account_payment_term_module = env["ir.module.module"].search(
        [("name", "=", "account_payment_term")], limit=1
    )
    needs_account_payment_term = bool(
        env["account.payment.term.line"].search(
            [("delay_type", "=", "days_end_of_month_on_the")], limit=1
        )
    )
    if needs_account_payment_term and account_payment_term_module:
        account_payment_term_module.state = "to install"
        openupgrade.copy_columns(
            env.cr,
            {
                "account_payment_term_line": [
                    ("days_after", "days_next_month", "CHARACTER VARYING")
                ]
            },
        )
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE account_payment_term_line
            SET nb_days = nb_days - days_after,
                days_next_month = days_after
            WHERE delay_type = 'days_end_of_month_on_the'
            """,
        )


def _map_chart_template_id_to_chart_template(
    env, model_table, coa_m2o="chart_template_id", coa_name_column="chart_template"
):
    """
    In tables that used to refer to a chart template in the database, set the new
    column identitying the COA by the name of its localization module with the
    `l10n_` prefix removed (usually the country's iso code)
    """
    env.cr.execute(
        f"""SELECT m.{coa_m2o}, CONCAT(imd.module, '.', imd.name)
            FROM {model_table} m
                JOIN ir_model_data imd
                    ON imd.model='account.chart.template'
                        AND m.{coa_m2o} = imd.res_id
            WHERE m.{coa_m2o} IS NOT NULL
            AND CONCAT(imd.module, '.', imd.name) IN %s
        """,
        (tuple(COA_MAPPING),),
    )
    chart_id2name = [(_id, COA_MAPPING[xmlid]) for _id, xmlid in env.cr.fetchall()]
    openupgrade.map_values(
        env.cr,
        coa_m2o,
        coa_name_column,
        chart_id2name,
        table=model_table,
    )


def _rename_coa_elements_xmlids(env):
    """On v17, when you load a CoA into a company, the CoA elements are still given an
    XML-ID with the company ID + `_` + the original template XML-ID, but now, instead of
    putting the module containing the template, all of them are put with the module
    `account`. Reference:

    https://github.com/odoo/odoo/blob/b9abe46c1492b09e369434e76ec8196c6b02dd19/
    addons/account/models/chart_template.py#L608

    Thus, we need to rename the module for all the existing CoA elements XML-IDs with
    this pattern.
    """
    for company in env["res.company"].search([]):
        openupgrade.logged_query(
            env.cr,
            f"""
            UPDATE ir_model_data
            SET module='account'
            WHERE module <> 'account'
            AND model IN (
                'account.account',
                'account.fiscal.position',
                'account.group',
                'account.tax'
            )
            AND name LIKE '{company.id}_%'
            """,
        )


@openupgrade.migrate()
def migrate(env, version):
    _account_payment_term_migration(env)
    _account_payment_term_early_payment_discount(env)
    _force_install_account_payment_term_module_module(env)
    openupgrade.load_data(env, "account", "17.0.1.2/noupdate_changes_work.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "account",
        (
            "email_template_edi_credit_note",
            "email_template_edi_invoice",
            "mail_template_data_payment_receipt",
        ),
    )
    openupgrade.delete_records_safely_by_xml_id(
        env,
        _deleted_xml_records,
    )
    _am_update_invoice_pdf_report_file(env)
    _onboarding_state_migration(env)
    _account_tax_group_migration(env)
    _map_chart_template_id_to_chart_template(env, "res_company")
    _map_chart_template_id_to_chart_template(env, "account_report")
    _rename_coa_elements_xmlids(env)
