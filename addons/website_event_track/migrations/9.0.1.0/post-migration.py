# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def copy_timezone_event_track(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE event_event
        SET date_tz = {}
        WHERE date_tz is NULL
        """.format(openupgrade.get_legacy_name('timezone_of_event'))
    )


def convert_track_stage(env):
    data_obj = env['ir.model.data']
    stage_state_mapping = [
        # website_event_track.event_track_stage1 is the default draft state
        (data_obj.xmlid_to_res_id('website_event_track.event_track_stage2'),
         'confirmed'),
        (data_obj.xmlid_to_res_id('website_event_track.event_track_stage3'),
         'published'),
        (data_obj.xmlid_to_res_id('website_event_track.event_track_stage4'),
         'announced'),
        # There's no exact equivalent to this stage (Completed)
        (data_obj.xmlid_to_res_id('website_event_track.event_track_stage5'),
         'announced'),
    ]
    openupgrade.map_values(
        env.cr, openupgrade.get_legacy_name('stage_id'), 'state',
        stage_state_mapping, table='event_track',
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    copy_timezone_event_track(env)
    convert_track_stage(env)
