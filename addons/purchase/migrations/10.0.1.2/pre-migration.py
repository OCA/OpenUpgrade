from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openupgradelib import openupgrade


def copy_state_to_purchase_lines(cr):
    openupgrade.logged_query(cr, '''
       ALTER TABLE purchase_order_line ADD COLUMN state VARCHAR;

       WITH purchases AS (
          SELECT id, state FROM purchase_order
       )
       UPDATE purchase_order_line line SET state=po.state
       FROM purchases po WHERE line.order_id=po.id;

    ''')


@openupgrade.migrate()
def migrate(env, version):
    copy_state_to_purchase_lines(env.cr)
