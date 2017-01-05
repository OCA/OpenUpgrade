# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common


class TestWebsiteEventTrack(common.SavepointCase):
    def test_website_event_track_migration(self):
        track = self.env.ref('website_event_track.event_track27')
        self.assertEqual(track.state, 'confirmed')
