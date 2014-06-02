
import openupgrade

@openupgrade.migrate
def migrate(cr, version):
    openupgrade.load_data(cr, 'product', 'migrations/8.0.1.1/modified_data.xml', mode='init')
