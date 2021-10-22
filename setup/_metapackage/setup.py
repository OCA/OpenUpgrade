import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo15-addons-oca-OpenUpgrade",
    description="Meta package for oca-OpenUpgrade Odoo addons",
    version=version,
    install_requires=[
        'odoo15-addon-openupgrade_scripts',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
