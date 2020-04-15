# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_field_renames = [
    ('lunch.alert ', 'lunch_alert ', 'monday', 'recurrency_monday'),
    ('lunch.alert ', 'lunch_alert ', 'tuesday', 'recurrency_tuesday'),
    ('lunch.alert ', 'lunch_alert ', 'wednesday', 'recurrency_wednesday'),
    ('lunch.alert ', 'lunch_alert ', 'thursday', 'recurrency_thursday'),
    ('lunch.alert ', 'lunch_alert ', 'friday', 'recurrency_friday'),
    ('lunch.alert ', 'lunch_alert ', 'saturday', 'recurrency_saturday'),
    ('lunch.alert ', 'lunch_alert ', 'sunday', 'recurrency_sunday'),
    ('lunch.alert ', 'lunch_alert ', 'specific_day', 'until'),
]

_field_adds = [
    ("category_id", "lunch.order", "lunch_order", "many2one", False, "lunch"),
    ("product_id", "lunch.order", "lunch_order", "many2one", False, "lunch"),
    ("supplier_id", "lunch.order", "lunch_order", "many2one", False, "lunch"),
    ("price", "lunch.order", "lunch_order", "float", False, "lunch"),
    ("note", "lunch.order", "lunch_order", "text", False, "lunch"),
]

_xmlid_renames = [
    # ir.model.access
    ('lunch.alert_manager', 'lunch.lunch_alert_access'),
    ('lunch.alert_user', 'lunch.lunch_alert_user'),
]


def move_lunch_order_line_to_lunch_order(env):
    openupgrade.add_fields(env, _field_adds)
    openupgrade.logged_query(
        env.cr, """
        UPDATE lunch_order lo
        SET
            category_id = lol.category_id,
            product_id = lol.product_id,
            supplier_id = lol.supplier,
            price = lol.price,
            note = lol.note,
            state = lol.state
        FROM lunch_order_line lol
        WHERE lo.id = lol.order_id
        """)


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    move_lunch_order_line_to_lunch_order(env)
