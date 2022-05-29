# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from psycopg2 import sql


def use_new_taxes_and_repartition_lines_on_move_lines(env):
    xmlid_names = [
        'account_tax_template_p_iva21_sp_in',
        'account_tax_template_p_iva21_ic_bc',
        'account_tax_template_p_iva21_ic_bi',
        'account_tax_template_p_iva4_sp_ex',
        'account_tax_template_p_iva10_sp_ex',
        'account_tax_template_p_iva21_sp_ex',
        'account_tax_template_p_iva4_ic_bc',
        'account_tax_template_p_iva4_ic_bi',
        'account_tax_template_p_iva10_ic_bc',
        'account_tax_template_p_iva10_ic_bi',
        'account_tax_template_p_iva10_sp_in',
        'account_tax_template_p_iva4_sp_in',
        'account_tax_template_p_iva4_isp',
        'account_tax_template_p_iva10_isp',
        'account_tax_template_p_iva21_isp',
    ]

    # select companies with chart of l10n_es:
    openupgrade.logged_query(
        env.cr, """
        SELECT rc.id
        FROM res_company rc
        JOIN ir_model_data imd ON (
            imd.model = 'account.chart.template'
            AND imd.module = 'l10n_es'
            AND imd.res_id = rc.chart_template_id)"""
    )
    companies_ids = [x[0] for x in env.cr.fetchall()]
    if not companies_ids:
        return
    # select taxes with children that don't have repartition lines
    taxes_with_children = env['account.tax'].with_context(
        active_test=False).search(
        [('children_tax_ids', '!=', False), ('company_id', 'in', companies_ids)]
    ).filtered(lambda t: not t.invoice_repartition_line_ids
               and not t.refund_repartition_line_ids)
    children_tax_ids = taxes_with_children.mapped('children_tax_ids').ids
    tax_ids = taxes_with_children.ids
    # create tax repartition lines
    if tax_ids:
        refund_account_query = (
            "CASE WHEN tax_exigibility = 'on_payment' "
            "THEN cash_basis_account_id ELSE account_id END"
        )
        column_mapping = [
            # (account_id, factor_percent, invoice_tax_id, refund_tax_id, repartition_type)
            ("NULL", 100, "id", "NULL", "base"),
            (refund_account_query, 100, "id", "NULL", "tax"),
            (refund_account_query, -100, "id", "NULL", "tax"),
            ("NULL", 100, "NULL", "id", "base"),
            (refund_account_query, 100, "NULL", "id", "tax"),
            (refund_account_query, -100, "NULL", "id", "tax"),
        ]
        for column in column_mapping:
            openupgrade.logged_query(
                env.cr,
                """INSERT INTO account_tax_repartition_line (
                    account_id, company_id, factor_percent, invoice_tax_id,
                    refund_tax_id, repartition_type, sequence,
                    create_uid, create_date, write_uid, write_date
                )
                SELECT %s, company_id, %s, %s, %s, '%s', 1,
                create_uid, create_date, write_uid, write_date
                FROM account_tax
                WHERE id IN %%s""" % column, (tuple(tax_ids), ),
            )
    if children_tax_ids:
        # assure children taxes are not parent taxes
        openupgrade.logged_query(
            env.cr, """
            DELETE FROM account_tax_filiation_rel rel
            WHERE rel.parent_tax IN %s
            """, (tuple(children_tax_ids), ),
        )
        # update account move line tax_ids
        openupgrade.logged_query(
            env.cr, """
            INSERT INTO account_move_line_account_tax_rel (
                account_move_line_id, account_tax_id)
            SELECT aml.id, at2.id
            FROM account_move_line aml
            JOIN account_move_line_account_tax_rel rel
                ON aml.id = rel.account_move_line_id
            JOIN account_tax at ON rel.account_tax_id = at.id
            JOIN account_tax_filiation_rel fil ON fil.child_tax = at.id
            JOIN account_tax at2 ON fil.parent_tax = at2.id
            WHERE at.id IN %s
            ON CONFLICT DO NOTHING""", (tuple(children_tax_ids), ),
        )
        other_parents = env["account.tax"].with_context(active_test=False).search(
            [("children_tax_ids", "in", children_tax_ids)]).filtered(lambda t: t not in taxes_with_children)
        obsolete_children = [x for x in children_tax_ids if x not in other_parents.mapped(
            'children_tax_ids').filtered(lambda t: t.id in children_tax_ids).ids]
        if obsolete_children:
            openupgrade.logged_query(
                env.cr, """
                DELETE FROM account_move_line_account_tax_rel
                WHERE account_tax_id IN %s
                """, (tuple(obsolete_children), ),
            )
        # update account move line tax_repartition_line_id
        for tax_column in ("invoice_tax_id", "refund_tax_id"):
            openupgrade.logged_query(
                env.cr, sql.SQL("""
                UPDATE account_move_line aml
                SET tax_repartition_line_id = atrl2.id, name = at2.name,
                    tax_line_id = at2.id
                FROM account_tax_repartition_line atrl
                JOIN account_tax at ON atrl.{column} = at.id
                JOIN account_tax_filiation_rel rel ON rel.child_tax = at.id
                JOIN account_tax at2 ON rel.parent_tax = at2.id
                JOIN account_tax_repartition_line atrl2 ON (
                    atrl2.{column} = at2.id
                    AND atrl2.repartition_type = atrl.repartition_type
                    AND SIGN(at.amount) = SIGN(atrl2.factor_percent))
                WHERE aml.tax_repartition_line_id = atrl.id AND at.id IN %s
                """).format(column=sql.Identifier(tax_column)),
                (tuple(children_tax_ids), ),
            )
        # update amount of parent taxes:
        for company_id in companies_ids:
            for tax_xmlid in xmlid_names:
                tax = env.ref('l10n_es.' + str(company_id) + '_' + tax_xmlid, raise_if_not_found=False)
                tax_template = env.ref('l10n_es.' + tax_xmlid, raise_if_not_found=False)
                if tax and tax_template:
                    tax.amount = tax_template.amount
                    tax.amount_type = tax_template.amount_type


def update_account_tags(env):
    xmlids = {
        "mod_115_02_03": ["mod_115_02", "mod_115_03"],
        "mod_303_01_03": ["mod_303_01", "mod_303_03"],
        "mod_303_04_06": ["mod_303_04", "mod_303_06"],
        "mod_303_07_09": ["mod_303_07", "mod_303_09"],
        "mod_303_10_11": ["mod_303_10", "mod_303_11"],
        "mod_303_12_13": ["mod_303_12", "mod_303_13"],
        "mod_303_14_15_purchase": ["mod_303_14_purchase", "mod_303_15"],
        "mod_303_14_15_sale": ["mod_303_14_sale", "mod_303_15"],
        "mod_303_16_18": ["mod_303_16", "mod_303_18"],
        "mod_303_19_21": ["mod_303_19", "mod_303_21"],
        "mod_303_22_24": ["mod_303_22", "mod_303_24"],
        "mod_303_25_26": ["mod_303_25", "mod_303_26"],
        "mod_303_28_29": ["mod_303_28", "mod_303_29"],
        "mod_303_30_31": ["mod_303_30", "mod_303_31"],
        "mod_303_32_33": ["mod_303_32", "mod_303_33"],
        "mod_303_34_35": ["mod_303_34", "mod_303_35"],
        "mod_303_36_37": ["mod_303_36", "mod_303_37"],
        "mod_303_38_39": ["mod_303_38", "mod_303_39"],
        "mod_303_40_41": ["mod_303_40", "mod_303_41"],
    }
    tables = {
        "account_account_tag_account_move_line_rel": "account_move_line_id",
        "account_account_tag_account_tax_repartition_line_rel": "account_tax_repartition_line_id",
        "account_account_account_tag": "account_account_id",
        "account_tax_repartition_financial_tags": "account_tax_repartition_line_template_id",
        "account_account_template_account_tag": "account_account_template_id",
    }
    old_tags = env["account.account.tag"]
    for old_xmlid, data_new in xmlids.items():
        old_tag = env.ref("l10n_es." + old_xmlid, raise_if_not_found=False)
        if not old_tag:
            continue
        old_tags |= old_tag
        for new_xmlid in data_new:
            new_tag = env.ref("l10n_es." + new_xmlid)
            for table, field in tables.items():
                openupgrade.logged_query(
                    env.cr, sql.SQL(
                        """INSERT INTO {table}
                        ({field}, account_account_tag_id)
                        SELECT rel.{field}, %(new_tag)s
                        FROM {table} rel
                        WHERE rel.account_account_tag_id = %(old_tag)s
                        ON CONFLICT DO NOTHING"""
                    ).format(
                        table=sql.Identifier(table),
                        field=sql.Identifier(field),
                    ), {
                        "old_tag": old_tag.id,
                        "new_tag": new_tag.id,
                    }
                )
    # Pre-deleting m2m links for avoiding ondelete="restrict" constraint when unlinking
    if old_tags:
        for table, field in tables.items():
            openupgrade.logged_query(
                env.cr, """
                DELETE FROM %(table)s
                WHERE account_account_tag_id IN %(old_tags)s
                """ % {
                    "table": table,
                    "old_tags": tuple(old_tags.ids),
                },
            )
    openupgrade.delete_records_safely_by_xml_id(
        env, ["l10n_es." + x for x in xmlids.keys()])
    # Make sure remaining tags that can't be removed don't fail when updating l10n_es
    # module and Odoo tries to remove them
    openupgrade.logged_query(
        env.cr, """
        UPDATE ir_model_data imd
        SET noupdate = TRUE
        WHERE model = 'account.account.tag' AND module = 'l10n_es'
            AND name IN %s
        """, (tuple(xmlids), ),
    )


@openupgrade.migrate()
def migrate(env, version):
    use_new_taxes_and_repartition_lines_on_move_lines(env)
    update_account_tags(env)
    # ALERT: remember to run after account_chart_update from OCA/account-financial-tools
