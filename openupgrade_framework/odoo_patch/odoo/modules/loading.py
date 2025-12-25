# Copyright Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.modules.loading


def load_module_graph(env, graph, *args, **kwargs):
    """
    Force run pre-migration scripts for modules being installed
    """
    env.registry._force_upgrade_scripts.update(set(package.name for package in graph))
    return odoo.modules.loading.load_module_graph._original_method(
        env, graph, *args, **kwargs
    )


load_module_graph._original_method = odoo.modules.loading.load_module_graph
odoo.modules.loading.load_module_graph = load_module_graph
