# flake8: noqa
# pylint: skip-file

from odoo.addons.openupgrade_framework.openupgrade import openupgrade_log

from odoo.tools.convert import xml_import

if True:

    def __test_xml_id(self, xml_id):
        if '.' in xml_id:
            module, id = xml_id.split('.', 1)
            assert '.' not in id, """The ID reference "%s" must contain
maximum one dot. They are used to refer to other modules ID, in the
form: module.record_id""" % (xml_id,)
            if module != self.module:
                modcnt = self.env['ir.module.module'].search_count([('name', '=', module), ('state', '=', 'installed')])
                assert modcnt == 1, """The ID "%s" refers to an uninstalled module""" % (xml_id,)

        # OpenUpgrade: log entry of XML imports
        openupgrade_log.log_xml_id(self.env.cr, self.module, xml_id)

xml_import._test_xml_id = __test_xml_id
