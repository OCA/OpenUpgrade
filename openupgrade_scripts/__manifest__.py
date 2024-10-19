# Copyright Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Openupgrade Scripts",
    "summary": """Module that contains all the migrations analysis
        and scripts for migrating Odoo SA modules.""",
    "author": "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/OpenUpgrade",
    "category": "Migration",
    "version": "16.0.1.0.4",
    "license": "AGPL-3",
    "depends": ["base"],
    "images": ["static/description/banner.jpg"],
    "external_dependencies": {"python": ["openupgradelib"]},
    "installable": True,
}
