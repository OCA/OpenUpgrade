# © 2018 Opener B.V. (stefan@opener.amsterdam)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.models import PREFETCH_MAX
from openupgradelib import openupgrade


def chunked(records, single=True):
    """ Memory and performance friendly method to iterate over a potentially
    large number of records. Yields either a whole chunk or a single record
    at the time. Don't nest calls to this method. """
    model = records._name
    ids = records.with_context(prefetch_fields=False).ids
    for i in range(0, len(ids), PREFETCH_MAX):
        records.env.invalidate_all()
        chunk = records.env[model].browse(ids[i:i + PREFETCH_MAX])
        if single:
            for record in chunk:
                yield record
            continue
        yield chunk


def generate_thumbnails(env):
    """ Let Odoo create a thumbnail for all attachments that consist of one of
    the supported image types and are not linked to a binary field. """
    for chunk in chunked(
            env['ir.attachment'].search([
                ('res_field', '=', False),
                ('mimetype', 'like', 'image.%'),
                '|', ('mimetype', 'like', '%gif'),
                '|', ('mimetype', 'like', '%jpeg'),
                '|', ('mimetype', 'like', '%jpg'),
                ('mimetype', 'like', '%png')])):
        for attachment in chunk.with_context(prefetch_fields=False).read(
                ['datas', 'mimetype']):
            res = env['ir.attachment']._make_thumbnail(attachment)
            if res.get('thumbnail'):
                env['ir.attachment'].browse(attachment['id']).write({
                    'thumbnail': res['thumbnail']})


@openupgrade.migrate()
def migrate(env, version):
    env['ir.ui.menu']._parent_store_compute()
    env['res.partner.category']._parent_store_compute()
    generate_thumbnails(env)
    env['res.company'].write({'base_onboarding_company_state': 'done'})
    openupgrade.load_data(
        env.cr, 'base', 'migrations/12.0.1.3/noupdate_changes.xml')
