from openupgradelib import openupgrade

@openupgrade.migrate()
def migrate(env, version):

    default_spec = {
        'product.attribute': [('create_variant', 'always')]
    }

    openupgrade.set_defaults(env.cr, env, default_spec)

    env['product.category']._parent_store_compute()
