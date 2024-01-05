import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

ACCOUNT_TAX_NAMES = [
    # Version 12.0
    {
        "22v": "Iva al 22% (debito)",
        "22a": "Iva al 22% (credito)",
        "21v": "Iva al 21% (debito)",
        "21a": "Iva al 21% (credito)",
        "20v": "Iva al 20% (debito)",
        "20a": "Iva al 20% (credito)",
        "5v": "Iva al 5% (debito)",
        "5a": "Iva al 5% (credito)",
        "10v": "Iva al 10% (debito)",
        "10a": "Iva al 10% (credito)",
        "10AO": "Iva al 10% indetraibile",
        "12v": "Iva 12% (debito)",
        "12a": "Iva 12% (credito)",
        "2010": "Iva al 20% detraibile 10%",
        "2015": "Iva al 20% detraibile 15%",
        "2040": "Iva al 20% detraibile 40%",
        "20AO": "Iva al 20% indetraibile",
        "20I5": "IVA al 20% detraibile al 50%",
        "2v": "Iva 2% (debito)",
        "2a": "Iva 2% (credito)",
        "4v": "Iva 4% (debito)",
        "4a": "Iva 4% (credito)",
        "4AO": "Iva al 4% indetraibile",
        "10I5": "IVA al 10% detraibile al 50%",
        "4I5": "IVA al 4% detraibile al 50%",
        "00v": "Fuori Campo IVA (debito)",
        "00a": "Fuori Campo IVA (credito)",
        "00art15v": "Imponibile Escluso Art.15 (debito)",
        "00art15a": "Imponibile Escluso Art.15 (credito)",
        "22v INC": "Iva al 22% (debito) INC",
        "21v INC": "Iva al 21% (debito) INC",
        "20v INC": "Iva al 20% (debito) INC",
        "10v INC": "Iva al 10% (debito) INC",
        "12v INC": "Iva 12% (debito) INC",
        "2v INC": "Iva 2% (debito) INC",
        "4v INC": "Iva 4% (debito) INC",
        "00v INC": "Fuori Campo IVA (debito) INC",
        "2110": "Iva al 21% detraibile 10%",
        "2115": "Iva al 21% detraibile 15%",
        "2140": "Iva al 21% detraibile 40%",
        "21AO": "Iva al 21% indetraibile",
        "21I5": "IVA al 21% detraibile al 50%",
        "2210": "Iva al 22% detraibile 10%",
        "2215": "Iva al 22% detraibile 15%",
        "2240": "Iva al 22% detraibile 40%",
        "22AO": "Iva al 22% indetraibile",
        "22I5": "IVA al 22% detraibile al 50%",
    },
    # Version 14.0
    {
        "22am": "Iva al 22% (credito)",  # code is changed
        "5am": "Iva al 5% (credito)",  # code is changed
        "10am": "Iva al 10% (credito)",  # code is changed
        "4am": "Iva 4% (credito)",  # code is changed
        "00am": "Fuori Campo IVA (credito)",  # code is changed
    },
]


def get_old_account_tax_names(xmlid):
    """
    Return a list of old names for the account.tax given matching the
    xmlid.
    """
    names = []
    for version in ACCOUNT_TAX_NAMES:
        name = version.get(xmlid)
        if name:
            names.append(name)
    return names


def get_tags(env, repartition_line_tmpl):
    """
    Return the tags linked to an account.tax.repartition.line.template
    """
    tag_names = []
    for report_line in repartition_line_tmpl.plus_report_line_ids:
        tag_names.append("+" + report_line.tag_name)
    for report_line in repartition_line_tmpl.minus_report_line_ids:
        tag_names.append("-" + report_line.tag_name)
    return env["account.account.tag"].search([("name", "in", tag_names)])


def is_account_tax_used(env, account_tax):
    """Return True if account_tax is used on an account.move.line."""
    env.cr.execute(
        """
        SELECT account_tax_id
        FROM account_move_line_account_tax_rel
        WHERE account_tax_id = %s
        """,
        (account_tax.id,),
    )
    return len(env.cr.fetchall()) > 0


def find_account_tax(env, xmlid, account_tax_template, company_id):
    """Return the account tax based on the given account.tax.template"""
    current_name = account_tax_template.name
    old_names = get_old_account_tax_names(xmlid)
    domain = [
        ("type_tax_use", "=", account_tax_template.type_tax_use),
        ("company_id", "=", company_id),
    ]

    if not old_names:
        _logger.info(
            "Skipping account.tax.template '%s', because it's a new one.",
            current_name,
        )
        return env["account.tax"]

    _logger.info(
        "Looking for a account.tax that match account.tax.template '%s'.", current_name
    )
    account_taxes = env["account.tax"].search(domain + [("name", "=", current_name)])

    if not account_taxes:
        _logger.info(
            "No account.tax named '%s', searching with older names.", current_name
        )
        account_taxes = env["account.tax"].search(domain + [("name", "in", old_names)])

    nb_account_taxes = len(account_taxes)
    account_taxes_used = account_taxes.filtered(lambda r: is_account_tax_used(env, r))

    if nb_account_taxes > 1:
        _logger.info(
            "There is several account.tax found for the "
            "account.tax.template '%s'. Trying to see which one is "
            "realy used.",
            current_name,
        )

        nb_account_taxes_used = len(account_taxes_used)
        if nb_account_taxes_used > 1:
            raise ValueError(
                "There is several account.tax found for the "
                "account.tax.template ID %s '%s' that are used on "
                "account.move.line. Clean up "
                "account.tax by renaming your specific account.tax "
                "and migrate it via a dedicated script. "
                "The matching account.tax ID %s"
                % (
                    account_tax_template.id,
                    current_name,
                    ", ".join(str(rec_id) for rec_id in account_taxes_used.ids),
                )
            )

        account_tax = account_taxes_used

    else:
        account_tax = account_taxes

    if not account_tax:
        _logger.error(
            "No matching account.tax for the account.tax.template '%s'.",
            current_name,
        )
    else:
        _logger.info(
            "Using account.tax ID %s '%s' that correspond to the "
            "account.tax.template '%s'.",
            account_tax.id,
            account_tax.name,
            current_name,
        )

    return account_tax


def find_repartition_line(account_tax, repartition_line_tmpl):
    """
    Retrieve the repartition line that match the given repartition
    line from the account.tax.template
    """
    # Choose to search on invoice repartition lines or refund ones.
    if repartition_line_tmpl.invoice_tax_id:
        repartition_lines = account_tax.invoice_repartition_line_ids
    else:
        repartition_lines = account_tax.refund_repartition_line_ids

    repartition_lines = repartition_lines.filtered(
        lambda r: r.repartition_type == repartition_line_tmpl.repartition_type
    )

    if len(repartition_lines) > 1:
        repartition_lines = repartition_lines.filtered(
            lambda r: r.factor_percent == repartition_line_tmpl.factor_percent
        )

    if len(repartition_lines) > 1:
        repartition_lines = repartition_lines.filtered(
            lambda r: r.account_id == repartition_line_tmpl.account_id
        )

    if not repartition_lines:
        # TODO: maybe in this case we need to create the repartition.line ?
        # Or we should delegate this to account_chart_update ?
        _logger.error(
            "No matching account.tax.repartition.line on account.tax ID %s "
            "for the account.tax.repartition.line.template ID %s",
            account_tax.id,
            repartition_line_tmpl.id,
        )
    elif len(repartition_lines) > 1:
        _logger.error(
            "Several matching account.tax.repartition.line on account.tax "
            "ID %s for the account.tax.repartition.line.template ID %s."
            "Found account.tax.repartition.line ID %s.",
            account_tax.id,
            repartition_line_tmpl.id,
            ", ".join(str(rec_id) for rec_id in repartition_lines.ids),
        )
    else:
        _logger.info(
            "Found matching account.tax.repartition.line ID %s "
            "on account.tax ID %s "
            "for the account.tax.repartition.line.template ID %s",
            repartition_lines.id,
            account_tax.id,
            repartition_line_tmpl.id,
        )

    return repartition_lines


def update_repartition_line(env, repartition_line, repartition_line_tmpl):
    """
    Update tag of the account.tax.repartition.line based on
    account.tax.repartition.line.template

    Update the following tables:
    - account_account_tag_account_tax_repartition_line_rel
    - account_account_tag_account_move_line_rel
    """
    # FIXME: I'm not sure if the table :
    #  - account_tax_repartition_financial_tags
    # should be updated or not.

    new_tag_ids = get_tags(env, repartition_line_tmpl)
    old_tag_ids = repartition_line.tag_ids
    # Update account_account_tag_account_tax_repartition_line_rel
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM account_account_tag_account_tax_repartition_line_rel
        WHERE account_tax_repartition_line_id = %s;
        """,
        (repartition_line.id,),
    )
    for new_tag_id in new_tag_ids:
        openupgrade.logged_query(
            env.cr,
            """
            INSERT INTO account_account_tag_account_tax_repartition_line_rel
            (account_tax_repartition_line_id, account_account_tag_id)
            VALUES (%s, %s)
            """,
            (repartition_line.id, new_tag_id.id),
        )

    # Update account_account_tag_account_move_line_rel
    domain = [
        "|",
        ("tax_ids", "=", repartition_line.tax_id.id),
        ("tax_line_id", "=", repartition_line.tax_id.id),
        ("tax_repartition_line_id", "=", False),
    ]
    if repartition_line.repartition_type == "base":
        # WARNING: Here I'm not sure if an account.move.line with a null
        # value as tax_base_amount should be considered equal to zero or
        # not. For now, I assume yes.
        domain.append("|")
        domain.append(("tax_base_amount", "=", 0))
        domain.append(("tax_base_amount", "=", False))
    if repartition_line.repartition_type == "tax":
        domain.append(("tax_base_amount", "!=", 0))

    account_move_line_ids = env["account.move.line"].search(domain)

    # Considering that "out_receipt" and "in_receipt" are not affected
    # by tags.
    if repartition_line.invoice_tax_id:
        account_move_line_ids = account_move_line_ids.filtered(
            lambda r: r.move_id.move_type in ("out_invoice", "in_invoice")
        )
    if repartition_line.refund_tax_id:
        # WARNING ! Some refund are invoices with a negative amount
        # This case is not taken into account.
        account_move_line_ids = account_move_line_ids.filtered(
            lambda r: r.move_id.move_type in ("out_refund", "in_refund")
        )

    # Adding account.move.line that are linked to this specific
    # repartition_line
    account_move_line_ids += env["account.move.line"].search(
        [("tax_repartition_line_id", "=", repartition_line.id)]
    )

    if not account_move_line_ids:
        return

    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM account_account_tag_account_move_line_rel
        WHERE account_move_line_id IN (%s)
        AND account_account_tag_id IN (%s)
        """
        % (
            ",".join(str(rec_id) for rec_id in account_move_line_ids.ids),
            ",".join(str(rec_id) for rec_id in old_tag_ids.ids),
        ),
    )
    for new_tag_id in new_tag_ids:
        values = [
            "(%s, %s)" % (aml_id, new_tag_id.id) for aml_id in account_move_line_ids.ids
        ]
        openupgrade.logged_query(
            env.cr,
            """
            INSERT INTO account_account_tag_account_move_line_rel
            (account_move_line_id, account_account_tag_id)
            VALUES %s
            ON CONFLICT DO NOTHING
            """
            % ",".join(values),
        )


def get_account_tax_templates_iterator(env):
    """
    Return account.tax.template with their xmlid
    """
    module = "l10n_it"
    data = env["ir.model.data"].search(
        [("model", "=", "account.tax.template"), ("module", "like", module)]
    )
    for elem in data:
        account_tax_template = env["account.tax.template"].browse(elem.res_id)
        yield elem.name, account_tax_template


def apply_new_tax_tags_on_account_tax(env, account_tax, account_tax_template):
    """
    The normal migration script of module account tries to link the old
    account.account.tag to account.tax.repartition.line.
    Which does not reflect the new account.tax.template and new
    account.account.tag which comes with positive (debit) and negative
    (credit) flavors.
    This function replace the old tags by the new ones.
    """
    for repartition_line_tmpl in (
        account_tax_template.invoice_repartition_line_ids
        + account_tax_template.refund_repartition_line_ids
    ):
        repartition_line = find_repartition_line(account_tax, repartition_line_tmpl)
        if not repartition_line:
            _logger.info(
                "No account.tax.repartition.line found that match "
                "the repartition line ID %s of the account.tax.template "
                "ID %s '%s'",
                repartition_line_tmpl.id,
                account_tax_template.id,
                account_tax_template.name,
            )
            continue
        update_repartition_line(env, repartition_line, repartition_line_tmpl)


def update_account_tax(env, company_id):
    """
    Use account.tax.template to update existing account.tax
    """
    for xmlid, account_tax_template in get_account_tax_templates_iterator(env):
        account_tax = find_account_tax(env, xmlid, account_tax_template, company_id)

        if not account_tax:
            continue

        apply_new_tax_tags_on_account_tax(env, account_tax, account_tax_template)

        # Do not rename account_tax to avoid differences in reports
        # account_tax.name = account_tax_template.name


def remove_wrong_tag(env):
    """
    Remove tags on account.move.line that are not linked to an
    account.tax.
    """
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM account_account_tag_account_move_line_rel
        WHERE account_move_line_id IN (
            SELECT id FROM account_move_line
            WHERE id NOT IN (
                SELECT DISTINCT account_move_line_id
                FROM account_move_line_account_tax_rel
            )
        )
        """,
    )


def unlink_tags_from_move_line(env, tag_xmlids):
    """Unlink tags from account.move.line"""
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM account_account_tag_account_move_line_rel r
        WHERE
            account_account_tag_id IN (
                SELECT res_id FROM ir_model_data
                WHERE
                    model = 'account.account.tag' AND
                    module = 'l10n_it' AND
                    name IN (%s)
            )
        """
        % ",".join("'" + xmlid + "'" for xmlid in tag_xmlids),
    )


def disable_troublesome_tags(env):
    """Disable old tags"""
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_account_tag
        SET active = FALSE
        WHERE
            name NOT LIKE '+%' AND
            name NOT LIKE '-%' AND
            applicability = 'taxes'
    """,
    )


# Based on file l10n_be/data/account_tax_template_data.xml
# Also based on Mis Builder VAT report
# (Cadre I, II et III -> base, Cardre IV and following -> tax).
base_tag_xmlids = []
tax_tag_xmlids = [
    "tax_tag_01",  # 10a
    "tax_tag_02",  # 10I5
    "tax_tag_03",  # 12a
    "tax_tag_04",  # 2a
    "tax_tag_05",  # 20a
    "tax_tag_06",  # 2010
    "tax_tag_07",  # 2015
    "tax_tag_08",  # 2040
    "tax_tag_09",  # 20I5
    "tax_tag_10",  # 21a
    "tax_tag_11",  # 2110
    "tax_tag_12",  # 2115
    "tax_tag_13",  # 2140
    "tax_tag_14",  # 21I5
    "tax_tag_15",  # 22a
    "tax_tag_16",  # 2210
    "tax_tag_17",  # 2215
    "tax_tag_18",  # 2240
    "tax_tag_19",  # 22I5
    "tax_tag_20",  # 4a
    "tax_tag_21",  # 4I5
    "tax_tag_22",  # 00a
    "tax_tag_23",  # 10AO
    "tax_tag_24",  # 20AO
    "tax_tag_25",  # 21AO
    "tax_tag_26",  # 22AO
    "tax_tag_27",  # 4AO
    "tax_tag_28",  # 00art15a
    "tax_tag_29",  # 10v
    "tax_tag_30",  # 10v INC
    "tax_tag_31",  # 12v
    "tax_tag_32",  # 12v INC
    "tax_tag_33",  # 2v
    "tax_tag_34",  # 2v INC
    "tax_tag_35",  # 20v
    "tax_tag_36",  # 20v INC
    "tax_tag_37",  # 21v
    "tax_tag_38",  # 21v INC
    "tax_tag_39",  # 22v
    "tax_tag_40",  # 22v INC
    "tax_tag_41",  # 4v
    "tax_tag_42",  # 4v INC
    "tax_tag_43",  # 00v
    "tax_tag_44",  # 00v INC
    "tax_tag_45",  # 00art15v
    "tax_tag_5a",  # 5a
    "tax_tag_5v",  # 5v
]


@openupgrade.migrate()
def migrate(env, version):
    remove_wrong_tag(env)
    for company in env["res.company"].search([]):
        update_account_tax(env, company.id)
    update_account_tax(env, False)
    unlink_tags_from_move_line(env, base_tag_xmlids + tax_tag_xmlids)
    disable_troublesome_tags(env)
