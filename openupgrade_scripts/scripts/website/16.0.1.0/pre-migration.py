from lxml import etree
from openupgradelib import openupgrade

_xmlids_renames = [
    (
        "website.group_website_publisher",
        "website.group_website_restricted_editor",
    ),
    (
        "website_sale.menu_reporting",
        "website.menu_reporting",
    ),
]

# delete xml xpath for odoo add it again
_xmlids_delete = [
    "website.website_configurator",
    "website.website_menu",
]


def delete_constraint_website_visitor_partner_uniq(env):
    openupgrade.delete_sql_constraint_safely(
        env,
        "website",
        "website_visitor",
        "partner_uniq",
    )


def _fill_partner_id_if_null(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE website_visitor v
           SET partner_id = p.id
          FROM res_partner p
         WHERE v.partner_id IS NULL
           AND length(v.access_token) != 32
           AND p.id = CAST(v.access_token AS integer);
        """,
    )


def _fill_language_ids_if_null(env):
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO website_lang_rel (website_id, lang_id)
        SELECT w.id, w.default_lang_id
          FROM website w
         WHERE NOT EXISTS (
            SELECT 1
              FROM website_lang_rel wlr
             WHERE wlr.website_id = w.id
         );
         """,
    )


def _fill_homepage_url(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE website
            ADD COLUMN IF NOT EXISTS homepage_url CHARACTER VARYING
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE website
           SET homepage_url = website_page.url
        FROM website_page
        WHERE website_page.id = website.homepage_id
        """,
    )


def _mig_s_progress_steps_contents(env):
    """Adapt to the new expected format inserted "Steps" snippet."""
    views = (
        env["ir.ui.view"]
        .with_context(active_test=False)
        .search(
            [
                ("arch_db", "ilike", '%data-snippet="s_process_steps"%'),
                ("arch_db", "not ilike", '%s_process_steps_connector_line"%'),
            ]
        )
    )
    for view in views:
        arch = etree.fromstring(view.arch_db)
        step_els = arch.xpath("//section[hasclass('s_process_steps')]")
        for step in step_els:
            if step.get("data-vcss"):
                continue
            step.set(
                "class", step.attrib.get("class") + " s_process_steps_connector_line"
            )
            step.set("data-vcss", "001")
            svg_defs = """
                <svg class="s_process_step_svg_defs position-absolute">
                    <defs>
                        <marker class="s_process_steps_arrow_head" markerWidth="15"
                            markerHeight="10" refX="6" refY="6" orient="auto">
                            <path d="M 2,2 L10,6 L2,10 L6,6 L2,2"
                                vector-effect="non-scaling-size"/>
                        </marker>
                    </defs>
                </svg>
            """
            step.insert(0, etree.fromstring(svg_defs))
            icon_els = step.xpath(".//div[hasclass('s_process_step_icon')]")
            for icon in icon_els:
                connector = """
                    <svg class="s_process_step_connector" viewBox="0 0 100 20"
                        preserveAspectRatio="none">
                        <path d="M 0 10 L 100 10" vector-effect="non-scaling-stroke"/>
                    </svg>
                """
                parent = icon.getparent()
                parent.insert(parent.index(icon), etree.fromstring(connector))
        view.arch_db = env["ir.ui.view"]._pretty_arch(arch)


def _reset_customize_show_in_website_views(env):
    """New Odoo website engine doesn't use customize_show=True system to show options
    in the Customize tab, so we preventively reset all of them containing a website* key
    for avoiding showing extra options where they shouldn't (it already happens for
    example in website_sale with "Category Collapsible List" view).
    """
    openupgrade.logged_query(
        env.cr,
        """UPDATE ir_ui_view
        SET customize_show=False
        WHERE key like 'website%' AND customize_show
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _fill_partner_id_if_null(env)
    _fill_language_ids_if_null(env)
    openupgrade.rename_xmlids(env.cr, _xmlids_renames)
    openupgrade.delete_records_safely_by_xml_id(env, _xmlids_delete)
    delete_constraint_website_visitor_partner_uniq(env)
    _fill_homepage_url(env)
    _mig_s_progress_steps_contents(env)
    _reset_customize_show_in_website_views(env)
