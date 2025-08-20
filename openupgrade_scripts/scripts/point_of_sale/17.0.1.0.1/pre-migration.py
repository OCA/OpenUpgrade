# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_model_renames = [
    ("restaurant.printer", "pos.printer"),
]

_table_renames = [
    ("restaurant_printer", "pos_printer"),
]

_field_renames = [
    ("pos.order", "pos_order", "multiprint_resume", "last_order_preparation_change"),
    ("pos.order.line", "pos_order_line", "mp_skip", "skip_change"),
]


def precreate_pos_config_auto_validate_terminal_payment(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE pos_config
        ADD COLUMN auto_validate_terminal_payment boolean DEFAULT TRUE
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE pos_config
        ALTER COLUMN auto_validate_terminal_payment DROP DEFAULT
        """,
    )


def fill_pos_order_config_id(env):
    openupgrade.logged_query(
        env.cr,
        """
         ALTER TABLE pos_order ADD COLUMN IF NOT EXISTS config_id INTEGER
         """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE pos_order pos
        SET config_id = ses.config_id
        FROM pos_session ses
        WHERE pos.session_id = ses.id AND pos.config_id IS NULL
        """,
    )


def fill_pos_payment_method_sequence(env):
    openupgrade.logged_query(
        env.cr,
        """
         ALTER TABLE pos_payment_method ADD COLUMN IF NOT EXISTS sequence INTEGER
         """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE pos_payment_method
        SET sequence = id
        WHERE sequence IS NULL
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.table_exists(env.cr, "restaurant_printer"):
        openupgrade.rename_models(env.cr, _model_renames)
        openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.rename_fields(env, _field_renames)
    precreate_pos_config_auto_validate_terminal_payment(env)
    fill_pos_order_config_id(env)
    fill_pos_payment_method_sequence(env)
