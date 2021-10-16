import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-OpenUpgrade",
    description="Meta package for oca-OpenUpgrade Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-openupgrade_framework',
        'odoo14-addon-openupgrade_scripts',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
