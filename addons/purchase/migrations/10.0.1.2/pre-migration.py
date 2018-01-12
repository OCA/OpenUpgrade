from openupgradelib import openupgrade


def copy_state_to_purchase_lines(cr):
    cr.execute('ALTER TABLE purchase_order_line ADD COLUMN state VARCHAR;')
    openupgrade.logged_query(cr, '''
       UPDATE purchase_order_line line SET state=po.state
       FROM purchase_order po WHERE line.order_id=po.id;
    ''')


@openupgrade.migrate()
def migrate(env, version):
    copy_state_to_purchase_lines(env.cr)
