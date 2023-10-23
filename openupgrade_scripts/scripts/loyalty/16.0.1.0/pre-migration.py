# Copyright 2023 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_field_renames = [
    ("coupon.program", "coupon_program", "promo_applicability", "applies_on"),
    ("coupon.program", "coupon_program", "promo_code_usage", "trigger"),
    ("coupon.program", "coupon_program", "maximum_use_number", "max_usage"),
    ("coupon.reward", "coupon_reward", "reward_description", "description"),
    ("coupon.reward", "coupon_reward", "discount_apply_on", "discount_applicability"),
    ("coupon.reward", "coupon_reward", "discount_type", "discount_mode"),
    (
        "coupon.reward",
        "coupon_reward",
        "discount_specific_product_ids",
        "discount_product_ids",
    ),
    ("coupon.reward", "coupon_reward", "reward_product_quantity", "reward_product_qty"),
    ("coupon.rule", "coupon_rule", "rule_minimum_amount", "minimum_amount"),
    ("coupon.rule", "coupon_rule", "rule_min_quantity", "minimum_qty"),
    ("coupon.rule", "coupon_rule", "rule_products_domain", "product_domain"),
    (
        "coupon.rule",
        "coupon_rule",
        "minimum_amount_tax_inclusion",
        "minimum_amount_tax_mode",
    ),
]
_models_renames = [
    ("coupon.program", "loyalty.program"),
    ("coupon.reward", "loyalty.reward"),
    ("coupon.coupon", "loyalty.card"),
    ("coupon.rule", "loyalty.rule"),
]
_tables_renames = [
    ("coupon_program", "loyalty_program"),
    ("coupon_reward", "loyalty_reward"),
    ("coupon_coupon", "loyalty_card"),
    ("coupon_rule", "loyalty_rule"),
]
_xmlids_renames = [
    (
        "loyalty.coupon_action",
        "loyalty.loyalty_card_action",
    ),
    (
        "loyalty.coupon_generate",
        "loyalty.loyalty_generate_wizard_action",
    ),
    (
        "loyalty.report_coupon_code",
        "loyalty.report_loyalty_card",
    ),
    (
        "loyalty.coupon_view_form",
        "loyalty.loyalty_card_view_form",
    ),
    (
        "loyalty.coupon_view_tree",
        "loyalty.loyalty_card_view_tree",
    ),
    (
        "loyalty.coupon_generate_view_form",
        "loyalty.loyalty_generate_wizard_view_form",
    ),
    (
        "loyalty.coupon_program_view_form_common",
        "loyalty.loyalty_program_view_form",
    ),
    (
        "loyalty.coupon_program_view_search",
        "loyalty.loyalty_program_view_search",
    ),
    (
        "loyalty.coupon_program_view_tree",
        "loyalty.loyalty_program_view_tree",
    ),
    (
        "sale_loyalty.mail_template_sale_coupon",
        "loyalty.mail_template_loyalty_card",
    ),
    (
        "gift_card.gift_card_product_50",
        "loyalty.gift_card_product_50",
    ),
]


def update_loyalty_program_data(env):
    # Fill date_to field: This data is updated with the values of the field 'rule_date_to
    # field of the 'loyalty_rule' table. Sets the 'date_to' field of the 'loyalty_program'
    # table to non-null values of to the non-null values of 'rule_date_to' where the old
    # 'loyalty_program.rule_id' field is equal to loyalty_rule.id' and
    # 'loyalty_rule.rule_date_to' is not null.
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_program
        ADD COLUMN IF NOT EXISTS date_to DATE
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_program
        SET date_to = loyalty_rule.rule_date_to
        FROM loyalty_rule
        WHERE loyalty_program.rule_id = loyalty_rule.id
        AND loyalty_rule.rule_date_to IS NOT NULL
        """,
    )
    # Sets the value of the limit_usage column to True for those records where the max_usage
    # column is not null.
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_program
        ADD COLUMN IF NOT EXISTS limit_usage BOOLEAN
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_program
        SET limit_usage = TRUE
        WHERE max_usage IS NOT NULL
        """,
    )
    # Determine the visibility on the default portal of specific loyalty programs, based
    # on their type (program_type)
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_program
        ADD COLUMN IF NOT EXISTS portal_visible BOOLEAN
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_program
        SET portal_visible =
            CASE
                WHEN program_type
                IN ('gift_card', 'ewallet', 'loyalty', 'next_order_coupons') THEN true
                ELSE false
            END
        """,
    )
    # Update standard selection values
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_program
        SET applies_on =
            CASE
                WHEN applies_on = 'on_current_order' THEN 'current'
                WHEN applies_on = 'on_next_order' THEN 'future'
            END
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_program
        SET trigger =
            CASE
                WHEN trigger = 'no_code_needed' THEN 'auto'
                WHEN trigger = 'code_needed' THEN 'with_code'
            END
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_program
        SET program_type =
            CASE
                WHEN program_type = 'coupon_program' THEN 'coupons'
                WHEN program_type = 'promotion_program' THEN 'promotion'
            END
        """,
    )


def update_loyalty_reward_data(env):
    # Determine which program_id and company_id each reward belongs to
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_reward
        ADD COLUMN IF NOT EXISTS program_id INT
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_reward AS lr
        SET program_id = lp.id
        FROM loyalty_program AS lp
        WHERE lr.id = lp.reward_id
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_reward
        ADD COLUMN IF NOT EXISTS company_id INT
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_reward AS lr
        SET company_id = lp.company_id
        FROM loyalty_program AS lp
        WHERE lr.id = lp.reward_id
        """,
    )
    # Update discount values according to discount mode
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_reward
        ADD COLUMN IF NOT EXISTS discount FLOAT
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_reward
        SET discount = CASE
            WHEN discount_mode = 'percentage' THEN discount_percentage
            WHEN discount_mode = 'fixed_amount' THEN discount_fixed_amount
        END
        """,
    )
    # Establish whether a reward is active based on the status of the program to which the
    # reward belongs
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_reward
        ADD COLUMN IF NOT EXISTS active BOOLEAN
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_reward AS lr
        SET active = lp.active
        FROM loyalty_program AS lp
        WHERE lr.id = lp.reward_id
        """,
    )
    # Set default values
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_reward
        ADD COLUMN IF NOT EXISTS clear_wallet BOOLEAN
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_reward
        SET clear_wallet = false
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_reward
        ADD COLUMN IF NOT EXISTS required_points FLOAT
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_reward
        SET required_points = 1
        """,
    )
    # Update standard selection values
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_reward
        SET discount_applicability =
            CASE
                WHEN discount_applicability = 'on_order' THEN 'order'
                WHEN discount_applicability = 'cheapest_product' THEN 'cheapest'
                WHEN discount_applicability = 'specific_products' THEN 'specific'
            END
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_reward
        SET discount_mode =
            CASE
                WHEN discount_mode = 'percentage' THEN 'percent'
                WHEN discount_mode = 'fixed_amount' THEN 'per_order'
            END
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_reward
        SET minimum_amount_tax_mode =
            CASE
                WHEN minimum_amount_tax_mode = 'tax_included' THEN 'incl'
                WHEN minimum_amount_tax_mode = 'tax_excluded' THEN 'excl'
            END
        """,
    )


def update_loyalty_rule_data(env):
    # Determine which program_id and company_id each rule belongs to
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_rule
        ADD COLUMN IF NOT EXISTS program_id INT
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_rule AS lr
        SET program_id = lp.id
        FROM loyalty_program AS lp
        WHERE lr.id = lp.rule_id
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_rule
        ADD COLUMN IF NOT EXISTS company_id INT
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_rule AS lr
        SET company_id = lp.company_id
        FROM loyalty_program AS lp
        WHERE lr.id = lp.rule_id
        """,
    )
    # Copy values from the "promo_code" field of loyalty.program to the "code" field of
    # loyalty.rule
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_rule
        ADD COLUMN IF NOT EXISTS code CHAR
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_rule AS lr
        SET code = lp.promo_code
        FROM loyalty_program AS lp
        WHERE lr.id = lp.rule_id
        """,
    )
    # If the code field is not null, the mode of application of a promotion based on its
    # rules will be set to "with_code", otherwise it will be "auto"
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_rule
        ADD COLUMN IF NOT EXISTS mode CHAR
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_rule
        SET mode = CASE
            WHEN code IS NOT NULL THEN 'with_code'
            ELSE 'auto'
        END
        """,
    )
    # Establish whether a rule is active based on the status of the program to which the
    # rule belongs
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_rule
        ADD COLUMN IF NOT EXISTS active BOOLEAN
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_rule AS lr
        SET active = lp.active
        FROM loyalty_program AS lp
        WHERE lr.id = lp.rule_id
        """,
    )
    # Set default values
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_rule
        ADD COLUMN IF NOT EXISTS reward_point_amount FLOAT
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_rule
        SET reward_point_amount = 1
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_rule
        ADD COLUMN IF NOT EXISTS reward_point_mode CHAR
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_rule
        SET reward_point_mode = 'order'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_rule
        ADD COLUMN IF NOT EXISTS reward_point_split BOOLEAN
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_rule
        SET reward_point_split = false
        """,
    )


def update_loyalty_card_data(env):
    # Determine which company_id each loyalty_card belongs to
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_card
        ADD COLUMN IF NOT EXISTS company_id INT
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_card AS lc
        SET company_id = lp.company_id
        FROM loyalty_program AS lp
        WHERE lc.program_id = lp.id
        """,
    )
    # In v16 points are used to establish the usability of a loyalty card, in case the
    # card has been used it will be 0, in case it is still valid it will be 1
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_card
        ADD COLUMN IF NOT EXISTS points FLOAT
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_card
        SET points = CASE
            WHEN loyalty_card.state IN ('used', 'cancel') THEN 0
            ELSE 1
        END
        """,
    )


# Field incorporated in new module loyalty_initial_date_validity
def fill_date_from_field(env):
    """Field incorporated in new module loyalty_initial_date_validity. This field takes
    the data from the old rule_date_from field of the coupon.rule template."""
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_program
        ADD COLUMN IF NOT EXISTS date_from DATE
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_program
        SET date_from = loyalty_rule.rule_date_from
        FROM loyalty_rule
        WHERE loyalty_program.rule_id = loyalty_rule.id
        AND loyalty_rule.rule_date_from IS NOT NULL
        """,
    )


def check_and_install_module_if_applicable(env):
    """
    The migration script for the loyalty_initial_date_validity modules is included.
    It is checked if there is any record with a start date in the rules of the
    established promotion. If there is any record, the modules are installed and the
    data is migrated from the database.
    """
    env.cr.execute(
        """
        SELECT 1 FROM loyalty_rule WHERE rule_date_from IS NOT NULL
        """,
    )
    has_date_from = env.cr.rowcount
    if has_date_from:
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE ir_module_module
            SET state='to install'
            WHERE name = 'loyalty_initial_date_validity' AND state='uninstalled'
            """,
        )
        fill_date_from_field(env)


def delete_sql_constraints(env):
    # Delete constraints to recreate it
    openupgrade.delete_sql_constraint_safely(
        env, "loyalty", "loyalty_rule", "check_coupon_rule_dates"
    )
    openupgrade.delete_sql_constraint_safely(
        env, "loyalty", "loyalty_card", "unique_coupon_code"
    )


def update_template_keys(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_ui_view
        SET key = 'loyalty.loyalty_report'
        WHERE key = 'coupon.report_coupon'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_ui_view
        SET key = 'loyalty.loyalty_report_i18n'
        WHERE key = 'coupon.report_coupon_i18n'
        """,
    )


def merge_gift_card_to_loyalty_card(env):
    """Merging the gift_card module into loyalty. To perform this data migration task,
    we work with gift_card and two tables to be updated, loyalty_program and
    loyalty_card. First, the data from gift_card will be inserted into loyalty_program
    to adapt the functionality to the gift card programs in v16, and then the data from
    gift_card will be copied to loyalty_card and the corresponding records will be
    referenced."""
    # Create records in loyalty_program based on gift_card data
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO loyalty_program (
            company_id,
            currency_id,
            create_uid,
            write_uid,
            program_type,
            applies_on,
            trigger,
            name,
            portal_point_name,
            active,
            portal_visible,
            create_date,
            write_date,
        )
        SELECT
            company_id,
            currency_id,
            create_uid,
            write_uid,
            'gift_card' AS program_type,
            'future' AS applies_on,
            'auto' AS trigger,
            '{"en_US": "Gift Cards"}' AS name,
            '{"en_US": "Gift Card"}' AS portal_point_name,
            CASE WHEN state = 'valid' THEN true ELSE false END AS active,
            true AS portal_visible,
            create_date,
            write_date
        FROM gift_card
        """,
    )
    # Add program_id column to gift_card to reference the program it belongs to
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE gift_card ADD COLUMN program_id INT;
        """,
    )
    # Update gift_card to link records with loyalty_program
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE gift_card gc
        SET program_id = (
            SELECT lp.id
            FROM loyalty_program lp
            WHERE lp.create_uid = gc.create_uid
            AND lp.create_date = gc.create_date
            AND lp.company_id = gc.company_id
            AND lp.currency_id = gc.currency_id
            AND lp.program_type = 'gift_card'
        )
        """,
    )
    # After having correctly referenced the data, we will copy the data from gift_card
    # to loyalty_card
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO loyalty_card (
            program_id,
            company_id,
            partner_id,
            create_uid,
            write_uid,
            code,
            expiration_date,
            create_date,
            write_date,
            points
        )
        SELECT
            program_id,
            company_id,
            partner_id,
            create_uid,
            write_uid,
            code,
            expiration_date AS expired_date,
            create_date,
            write_date,
            initial_amount AS points
        FROM gift_card
        """,
    )
    # Create records in loyalty_reward based on gift_card data
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO loyalty_reward (
            active,
            program_id,
            company_id,
            description,
            reward_type,
            discount,
            discount_mode,
            discount_applicability,
            discount_line_product_id,
            clear_wallet,
            required_points,
            reward_product_qty,
            create_uid,
            write_uid,
            discount_product_domain,
            create_date,
            write_date
        )
        SELECT
            lp.active,
            gc.program_id,
            gc.company_id,
            '{"en_US": "Gift Card"}',
            'discount',
            1,
            'per_point',
            'order',
            sol.product_id,
            false,
            1,
            1,
            gc.create_uid,
            gc.write_uid,
            '[]',
            gc.create_date,
            gc.write_date
        FROM gift_card AS gc
        JOIN loyalty_program AS lp ON gc.program_id = lp.id
        JOIN sale_order_line AS sol ON sol.gift_card_id = gc.id
        """,
    )
    # Create records in loyalty_rule based on gift_card data
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO loyalty_rrule (
            program_id,
            company_id,
            minimun_qty,
            create_uid,
            write_uid,
            product_domain,
            reward_point_mode,
            minimun_amount_tax_mode,
            mode,
            active,
            reward_point_split,
            create_date,
            write_date,
            reward_point_amount
        )
        SELECT
            gc.program_id,
            gc.company_id,
            1,
            gc.create_uid,
            gc.write_uid,
            '[]',
            'money',
            'incl',
            'auto',
            lp.active,
            true,
            gc.create_date,
            gc.write_date,
            1
        FROM gift_card AS gc
        JOIN loyalty_program AS lp ON gc.program_id = lp.id
        """,
    )
    # If the card has been used, it calculates the new points value by subtracting the
    # sum of the absolute price_unit values of the order lines linked to a gift_card
    # from the initial value of the loyalty card (loyalty_card.initial_amount). In case
    # there is no order line linked to the gift card, the initial value of the loyalty
    # card shall be maintained.
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_card lc
        SET points =
            CASE
                WHEN (
                    SELECT SUM(ABS(sol.price_unit))
                    FROM sale_order_line sol
                    JOIN gift_card gc ON gc.id = sol.gift_card_id
                    WHERE gc.program_id = lc.program_id
                ) IS NOT NULL
                THEN lc.initial_amount - (
                    SELECT SUM(ABS(sol.price_unit))
                    FROM sale_order_line sol
                    JOIN gift_card gc ON gc.id = sol.gift_card_id
                    WHERE gc.program_id = lc.program_id
                )
                ELSE lc.points
            END
        FROM gift_card gc
        WHERE lc.program_id = gc.program_id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_models(env.cr, _models_renames)
    openupgrade.rename_tables(env.cr, _tables_renames)
    openupgrade.rename_xmlids(env.cr, _xmlids_renames)
    # Renamed in rename_xmlids method.
    # In v15 are noupdate=1 and in v16 are noupdate=0
    openupgrade.set_xml_ids_noupdate_value(
        env, "loyalty", "mail_template_loyalty_card", False
    )
    openupgrade.set_xml_ids_noupdate_value(
        env, "loyalty", "gift_card_product_50", False
    )
    update_loyalty_program_data(env)
    update_loyalty_reward_data(env)
    update_loyalty_rule_data(env)
    update_loyalty_card_data(env)
    check_and_install_module_if_applicable(env)
    delete_sql_constraints(env)
    update_template_keys(env)
    merge_gift_card_to_loyalty_card(env)
