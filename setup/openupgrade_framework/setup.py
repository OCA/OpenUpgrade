import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        'external_dependencies_override': {
            'python': {
                'openupgradelib': 'git+https://github.com/OCA/openupgradelib.git@master',
            }
        }
    },
)
