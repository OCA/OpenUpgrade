# List of 'domain' fields in Odoo core and OCA models.
# ----------------------------------------------------
# It is used from openupgradelib
#
# Each list item is a tuple with the following data:
# - Module name where the domain field is defined
# - Table name of the model that contanins the domain field
# - Domain field name
# - Name of the Many2one field related to that model on which the
# domain field is applied.
# - Static _name of the model on which the domain field is applied
# in case there is no Many2one field related to that model (previous item).
# If that field doesn't exist, the _name of the model is specify in the view,
# Ex: rule_products_domain field in coupon.program (coupon_program table).
#
# This list has to be maintained manually:
# Currently these fields are Char type and are defined as domain widget
# in views, therefore this list has to be maintained manually until
# fields.Domain (or similar) exist or until the field has a
# property that allows it to be identified as a domain field.
domain_fields = [
    # odoo
    ("base_automation", "base_automation", "filter_pre_domain", "model_name", None),
    ("base_automation", "base_automation", "filter_domain", "model_name", None),
    ("coupon", "coupon_program", "rule_products_domain", None, "product.product"),
    ("coupon", "coupon_program", "rule_partners_domain", None, "res.partner"),
    ("coupon", "coupon_generate_wizard", "partners_domain", None, "res.partner"),
    ("crm", "crm_team_member", "assignment_domain", None, "crm.lead"),
    ("crm", "crm_team", "assignment_domain", None, "crm.lead"),
    (
        "event_crm",
        "event_lead_rule",
        "event_registration_filter",
        None,
        "event.registration",
    ),
    ("gamification", "gamification_challenge", "user_domain", None, "res.users"),
    ("mass_mailing", "mailing_mailing", "mailing_domain", "mailing_model_real", None),
    ("base", "ir_filters", "domain", "model_id", None),
    # account-financial-reporting
    (
        "account_financial_report",
        "general_ledger_report_wizard",
        "domain",
        None,
        "account.move.line",
    ),
    # crm
    (
        "crm_phonecall_planner",
        "crm_phonecall_planner",
        "res_partner_domain",
        None,
        "res.partner",
    ),
    # data-protection
    ("privacy", "privacy_activity", "subject_domain", None, "res.partner"),
    # ddmrp
    (
        "ddmrp_warning",
        "ddmrp_warning_definition",
        "warning_domain",
        None,
        "stock.buffer",
    ),
    # product-attribute
    ("product_assortment", "ir_filters", "domain", None, "product.product"),
    (
        "product_assortment",
        "ir_filters",
        "black_list_product_domain",
        None,
        "product.product",
    ),
    ("product_assortment", "ir_filters", "partner_domain", None, "res.partner"),
    # sale-promotion
    (
        "sale_coupon_criteria_order_based",
        "coupon_program",
        "rule_order_domain",
        None,
        "sale.order",
    ),
    # sale-workflow
    (
        "sale_automatic_workflow",
        "sale_workflow_process",
        "order_filter_domain",
        None,
        "sale.order",
    ),
    (
        "sale_automatic_workflow",
        "sale_workflow_process",
        "picking_filter_domain",
        None,
        "stock.picking",
    ),
    (
        "sale_automatic_workflow",
        "sale_workflow_process",
        "create_invoice_filter_domain",
        None,
        "sale.order",
    ),
    (
        "sale_automatic_workflow",
        "sale_workflow_process",
        "validate_invoice_filter_domain",
        None,
        "account.move",
    ),
    (
        "sale_automatic_workflow",
        "sale_workflow_process",
        "payment_filter_domain",
        None,
        "account.move",
    ),
    (
        "sale_automatic_workflow",
        "sale_workflow_process",
        "sale_done_filter_domain",
        None,
        "sale.order",
    ),
    # server-tools
    ("base_exception", "exception_rule", "domain", "model", None),
    ("excel_import_export", "report_xlsx_wizard", "domain", "res_model", None),
    # server-ux
    ("base_custom_filter", "ir_filters_group", "domain", "model_id", None),
    ("base_tier_validation", "tier_definition", "definition_domain", "model", None),
    # social
    (
        "mass_mailing_list_dynamic",
        "tier_definition",
        "sync_domain",
        None,
        "res.partner",
    ),
]
