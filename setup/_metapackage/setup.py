import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-OpenUpgrade",
    description="Meta package for oca-OpenUpgrade Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-openupgrade_framework>=15.0dev,<15.1dev',
        'odoo-addon-openupgrade_scripts>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
