# -*- coding: utf-8 -*-
# Copyright 2017 bloopark systems (<http://bloopark.de>)
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def map_list_id_to_list_ids(env):
    """Set the list_ids for the list_id in mail.mass_mailing.contact"""
    openupgrade.m2o_to_x2m(
        env.cr, env['mail.mass_mailing.contact'], 'mail_mass_mailing_contact',
        'list_ids', 'list_id',
    )


def map_mailing_model_to_mailing_model_id(cr):
    """Set the mailing_model_id for the mailing_model in mail.mass_mailing"""
    openupgrade.logged_query(
        cr, """
        UPDATE mail_mass_mailing mmm
        SET mailing_model_id = im.id
        FROM ir_model im
        WHERE im.model = mmm.mailing_model"""
    )


@openupgrade.migrate()
def migrate(env, version):
    map_list_id_to_list_ids(env)
    map_mailing_model_to_mailing_model_id(env.cr)
