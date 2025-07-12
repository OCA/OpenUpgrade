# Copyright Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Openupgrade Framework",
    "summary": """Module to integrate in the server_wide_modules
    option to make upgrades between two major revisions.""",
    "author": "Odoo Community Association (OCA), Therp BV, Opener B.V., GRAP, "
    "Hunki Enterprises BV",
    "maintainers": ["legalsylvain", "StefanRijnhart", "hbrunn"],
    "website": "https://github.com/OCA/OpenUpgrade",
    "category": "Migration",
    "version": "18.0.1.0.2",
    "license": "AGPL-3",
    "depends": ["base"],
    "images": ["static/description/banner.jpg"],
    "external_dependencies": {"python": ["openupgradelib"]},
    "installable": True,
}
