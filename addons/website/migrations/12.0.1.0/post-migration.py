# Copyright 2018-19 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from lxml import etree
from openupgradelib import openupgrade


def assign_theme(env):
    theme_category = env.ref('base.module_category_theme')
    theme_module = env['ir.module.module'].search(
        [('state', '=', 'installed'),
         ('category_id', '=', theme_category.id)],
        limit=1,
    )
    websites = env['website'].search([])
    if theme_module:
        websites.write({'theme_id': theme_module.id})


def fill_website_socials(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE website w
        SET social_facebook = c.social_facebook,
            social_github = c.social_github,
            social_googleplus = c.social_googleplus,
            social_linkedin = c.social_linkedin,
            social_twitter = c.social_twitter,
            social_youtube = c.social_youtube
        FROM res_company c
        WHERE w.company_id = c.id
        """
    )


def apply_bootstrap_4(view):
    def pre_child_bootstrap_changes(_node):
        new_node = _node
        parent = new_node.getparent()
        if len(parent) and 'class' in parent.attrib:
            if 'dropdown' in parent.attrib['class']:
                if 'class' in new_node.attrib:
                    new_node.attrib['class'] = new_node.attrib[
                        'class'].replace('divider', 'dropdown-divider')
                    if new_node.attrib.get('role') == 'menuitem':
                        new_node.attrib['class'] = new_node.attrib[
                            'class'] + ' dropdown-item'
                elif new_node.attrib.get('role') == 'menuitem':
                    new_node.set('class', 'dropdown-item')
            if 'nav' in parent.attrib['class']:
                if 'class' in new_node.attrib:
                    if new_node.tag == 'li':
                        new_node.attrib['class'] =\
                            'nav-item ' + new_node.attrib['class']
                        new_node.attrib['class'] = new_node.attrib[
                            'class'].replace('pull-left', 'ml-auto')
                        new_node.attrib['class'] = new_node.attrib[
                            'class'].replace('pull-right', 'ml-auto')
                    elif new_node.tag == 'a' and \
                            'navbar-brand' not in new_node.attrib['class']:
                        new_node.attrib['class'] =\
                            'nav-link ' + new_node.attrib['class']
                    new_node.attrib['class'] = new_node.attrib[
                        'class'].replace('navbar-toggle', 'navbar-toggler')
                    new_node.attrib['class'] = new_node.attrib[
                        'class'].replace('icon-bar', 'navbar-toggler-icon')
                else:
                    if new_node.tag == 'li':
                        new_node.set('class', 'nav-item')
                    elif new_node.tag == 'a':
                        new_node.set('class', 'nav-link')
            if 'pagination' in parent.attrib['class']:
                if 'class' in new_node.attrib:
                    if new_node.tag == 'li':
                        new_node.attrib['class'] = \
                            'page-item ' + new_node.attrib['class']
                    elif new_node.tag == 'a':
                        new_node.attrib['class'] =\
                            'page-link ' + new_node.attrib['class']
                else:
                    if new_node.tag == 'li':
                        new_node.set('class', 'page-item')
                    elif new_node.tag == 'a':
                        new_node.set('class', 'page-link')
            if 'breadcrumb' in parent.attrib['class']:
                if 'class' in new_node.attrib:
                    if new_node.tag == 'li':
                        new_node.attrib['class'] = \
                            'breadcrumb-item ' + new_node.attrib['class']
                else:
                    if new_node.tag == 'li':
                        new_node.set('class', 'breadcrumb-item')
            if 'list-inline' in parent.attrib['class']:
                if 'class' in new_node.attrib:
                    if new_node.tag == 'li':
                        new_node.attrib['class'] = \
                            'list-inline-item ' + new_node.attrib['class']
                else:
                    if new_node.tag == 'li':
                        new_node.set('class', 'list-inline-item')
            if 'custom-control' in parent.attrib['class']:
                if 'class' in new_node.attrib:
                    if new_node.tag == 'input':
                        new_node.attrib['class'] = \
                            'custom-control-input ' + new_node.attrib['class']
                else:
                    if new_node.tag == 'input':
                        new_node.set('class', 'custom-control-input')
            if 'input-group' in parent.attrib['class'] \
                    and 'input-group-btn' not in parent.attrib['class']:
                if 'class' in new_node.attrib:
                    if new_node.tag == 'input':
                        new_node.attrib['class'] = new_node.attrib[
                            'class'].replace('o_input', 'form-control o_input')
            if 'carousel' in parent.attrib['class']:
                if 'class' in new_node.attrib:
                    new_node.attrib['class'] = new_node.attrib[
                        'class'].replace('item', 'carousel-item')
                    new_node.attrib['class'] = new_node.attrib[
                        'class'].replace('left', 'carousel-item-left')
                    new_node.attrib['class'] = new_node.attrib[
                        'class'].replace('right', 'carousel-item-right')
                    new_node.attrib['class'] = new_node.attrib[
                        'class'].replace('next', 'carousel-item-next')
                    new_node.attrib['class'] = new_node.attrib[
                        'class'].replace('prev', 'carousel-item-prev')
            if parent.tag == 'form' or parent.attrib.get('role') == 'form':
                if 'form-inline' in parent.attrib['class'] and \
                        'class' in new_node.attrib:
                    if new_node.tag == 'div':
                        new_node.attrib['class'] = new_node.attrib[
                            'class'].replace('help-block', 'form-text')
                    else:
                        new_node.attrib['class'] = new_node.attrib[
                            'class'].replace('help-block', 'text-muted')
                if 'form-horizontal' in parent.attrib['class'] and \
                        'class' in new_node.attrib:
                    new_node.attrib['class'] = new_node.attrib[
                        'class'].replace('form-group', 'form-group row')
        if 'class' in new_node.attrib:
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'o_checkbox', 'custom-control custom-checkbox')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'o_radio_item', 'custom-control custom-radio o_radio_item')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'o_radio_input', 'custom-control-input o_radio_input')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'o_form_label', 'custom-control-label o_form_label')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'has-error', 'o_has_error')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'has-warning', 'o_has_warning')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'has-success', 'o_has_success')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'well', 'card')
            if new_node.tag != 'img':
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'thumbnail', 'card')
            else:
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'thumbnail', '')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'form-control-static', 'form-control-plaintext')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'btn-group-sm', '')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'btn-group-xs', 'btn-group-sm')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'dropdown full', 'dropdown-toggle full')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'col-lg-offset-', 'offset--xl-')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'col-md-offset-', 'offset--lg-')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'col-sm-offset-', 'offset--md-')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'col-xs-offset-', 'offset-')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'col-lg-', 'col-xl-')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'col-md-', 'col-lg-')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'col-sm-', 'col-md-')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'col-xs-', 'col-')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'badge', 'badge badge-pill')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'label label-default', 'badge badge-secondary')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'label label-', 'badge badge-')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'panel ', 'card ')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'panel-default', '')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'panel-collapse', '')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'panel-group', 'accordion')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'panel-heading', 'card-header')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'panel-title', 'card-title')
            if 'panel-body' in new_node.attrib['class']:
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'bg-success', '')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'bg-info', '')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'bg-warning', '')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'bg-danger', '')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'panel-body', 'card-body')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'panel-footer', 'card-footer')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'panel-', 'bg-')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'progress-bar-', 'bg-')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'show', 'd-block')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'hidden-print', 'd-print-none')
            if new_node.tag == 'a' or new_node.tag == 'button':
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'hidden-lg', 'd-none d-xl-inline-block')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'hidden-md', 'd-none d-lg-inline-block')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'hidden-sm', 'd-none d-md-inline-block')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'hidden-xs', 'd-none d-inline-block')
            elif new_node.tag == 'th':
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'hidden-lg', 'd-none d-xl-table-cell')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'hidden-md', 'd-none d-lg-table-cell')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'hidden-sm', 'd-none d-md-table-cell')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'hidden-xs', 'd-none d-table-cell')
            elif new_node.tag == 'span':
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'hidden-lg', 'd-none d-xl-inline')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'hidden-md', 'd-none d-lg-inline')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'hidden-sm', 'd-none d-md-inline')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'hidden-xs', 'd-none d-inline')
            else:
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'hidden-lg', 'd-none d-xl-block')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'hidden-md', 'd-none d-lg-block')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'hidden-sm', 'd-none d-md-block')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'hidden-xs', 'd-none d-block')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'hidden', 'd-none')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'visible-print', 'd-print')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'visible-md-inline', 'd-inline d-xl-none')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'visible-md-block', 'd-block d-xl-none')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'visible-md', 'd-block d-xl-none')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'visible-sm-inline', 'd-inline d-lg-none')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'visible-sm-block', 'd-block d-lg-none')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'visible-sm', 'd-block d-lg-none')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'visible-xs-inline', 'd-inline d-md-none')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'visible-xs-block', 'd-block d-md-none')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'visible-xs', 'd-block d-md-none')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                ' pull-', ' float-')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'center-block', 'd-block mx-auto')
            if 'navbar-default' in new_node.attrib['class']:
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'navbar-default', 'navbar-expand-md navbar-light bg-light')
            elif 'navbar-inverse' in new_node.attrib['class']:
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'navbar-default', 'navbar-expand-md navbar-dark bg-dark')
        if new_node.tag == 'img' or new_node.attrib.get('role') == 'img':
            if 'class' in new_node.attrib:
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'img-circle', 'rounded-circle')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'img-responsive', 'img-fluid')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'img-rounded', 'rounded')
        if new_node.tag == 'table':
            if 'class' in new_node.attrib:
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'active', 'table-active')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'success', 'table-success')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'warning', 'table-warning')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'danger', 'table-danger')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'info', 'table-info')
        if new_node.tag == 'form' or new_node.attrib.get('role') == 'form' or \
                (len(parent) and 'class' in parent.attrib and
                 'form-group' in parent.attrib['class']):
            if 'class' in new_node.attrib:
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'control-label', 'col-form-label')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'input-lg', 'form-control-lg')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'input-sm', 'form-control-sm')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'form-group-', 'form-control-')
        if new_node.tag == 'button' or new_node.attrib.get('role') == 'button':
            if 'class' in new_node.attrib:
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'btn-default', 'btn-secondary')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'btn-icon', 'btn-secondary')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'btn-sm', '')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'btn-xs', 'btn-sm')
            if 'data-loading-text' in new_node.attrib:
                del new_node.attrib['data-loading-text']
        if new_node.tag == 'nav' or new_node.attrib.get('role') == 'nav':
            if 'class' in new_node.attrib:
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'navbar-right', 'ml-auto')
                new_node.attrib['class'] = new_node.attrib['class'].replace(
                    'nav-stacked', 'flex-column')
        return new_node

    def post_child_bootstrap_changes(_node):
        new_node = _node
        # parent = new_node.getparent()
        if 'class' in new_node.attrib:
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'radio-inline', '')
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                'checkbox-inline', '')
        if new_node.tag == 'form' or new_node.attrib.get('role') == 'form':
            if 'class' in new_node.attrib:
                if "form-horizontal" in new_node.attrib['class']:
                    new_node.attrib['class'] = new_node.attrib[
                        'class'].replace('form-horizontal', '')
        if 'class' in new_node.attrib:
            new_node.attrib['class'] = new_node.attrib['class'].strip()
            new_node.attrib['class'] = new_node.attrib['class'].replace(
                '  ', ' ')
        return new_node

    def apply_bootstrap_all_nodes(_node):
        new_node = _node
        new_node = pre_child_bootstrap_changes(new_node)
        for child in new_node.getchildren():
            new_child = apply_bootstrap_all_nodes(child)
            new_node.replace(child, new_child)
        new_node = post_child_bootstrap_changes(new_node)
        return new_node

    text = view.arch_db
    openupgrade.logger.info("bootstrap: migration begins")
    text = text.replace('</p><p>', '<br/>')
    node = etree.fromstring(text)
    node = apply_bootstrap_all_nodes(node)
    text = etree.tostring(node)
    text = text.replace(' class=""', '')
    text = text.replace(" class=''", "")
    openupgrade.logger.info("bootstrap: migration ends")
    view.arch_db = text


def bootstrap_4_migration(env):
    pages = env['website.page'].search([])
    views = pages.mapped('view_id').filtered(
        lambda v: v.type == 'qweb' and not v.xml_id)
    for view in views:
        apply_bootstrap_4(view)


def apply_copy_views(env):
    env.cr.execute(
        """
        SELECT website_page_id, website_id
        FROM website_website_page_rel
        """
    )
    pages = {}
    for page_id, website_id in env.cr.fetchall():
        if page_id not in pages:
            pages[page_id] = []
        pages[page_id].append(website_id)
    for page in env['website.page'].browse(list(pages)):
        for website in env['website'].browse(list(pages[page.id])):
            page.copy({'website_id': website.id})


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    assign_theme(env)
    fill_website_socials(cr)
    env['website.menu']._parent_store_compute()
    bootstrap_4_migration(env)
    apply_copy_views(env)
    openupgrade.load_data(
        cr, 'website', 'migrations/12.0.1.0/noupdate_changes.xml')
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            'website.action_website_homepage',
            'website.action_module_theme',
            'website.action_module_website',
        ],
    )
