# -*- coding: utf-8 -*-
# Copyright 2017 Bloopark <http://bloopark.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # fill website.page with data from view with type page
    env.cr.execute(
        """INSERT INTO website_page(url,view_id,website_indexed,website_published,create_uid,create_date,write_uid,write_date)
            SELECT wm.url,iuv.id,TRUE,TRUE,iuv.create_uid,iuv.create_date,iuv.write_uid,iuv.write_date
            FROM ir_ui_view iuv,website_menu wm where page=true and iuv.name=wm.name""")

    # Many2many relation for field website_ids of website.page
    env.cr.execute(
        """INSERT INTO website_website_page_rel(website_page_id,website_id)
            SELECT wp.id,iuv.website_id FROM ir_ui_view iuv, website_page wp
            WHERE wp.view_id=iuv.id and iuv.website_id IS NOT NULL""")

    # clean data for website.menu_website deleted from noupdate data
    env.cr.execute(
        """DELETE FROM ir_ui_menu where id IN
                    (SELECT res_id FROM ir_model_data
                    WHERE model='ir.ui.menu' AND module='website' AND name='menu_website')""")

    env.cr.execute("""DELETE FROM ir_model_data WHERE model='ir.ui.menu'
                      AND module='website' AND name='menu_website'""")

    # Add homepage for websites
    env.cr.execute(
        """UPDATE website AS w SET homepage_id = am.homepage_id FROM
                (SELECT iuv.website_id AS website_id,wp.id AS homepage_id
                FROM ir_ui_view iuv,website_page wp
                    WHERE iuv.website_id IS NOT NULL AND iuv.key='website.homepage' AND iuv.id=wp.view_id) am
                    WHERE w.id = am.website_id""")

    openupgrade.load_data(env.cr, 'website', 'migrations/11.0.1.0/noupdate_changes.xml', )
