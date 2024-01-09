from openupgradelib import openupgrade

_noupdate_xmlids = [
    "s_blockquote_default_image",
    "s_masonry_block_default_image_1",
    "s_masonry_block_default_image_2",
    "s_media_list_default_image_1",
    "s_media_list_default_image_2",
    "s_media_list_default_image_3",
    "s_product_list_default_image_1",
    "s_product_list_default_image_2",
    "s_product_list_default_image_3",
]


def _noupdate_switch(env):
    openupgrade.set_xml_ids_noupdate_value(env, "mass_mailing", _noupdate_xmlids, False)


@openupgrade.migrate()
def migrate(env, version):
    _noupdate_switch(env)
