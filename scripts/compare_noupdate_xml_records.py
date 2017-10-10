# coding: utf-8
# Copyright 2011-2015 Therp BV <https://therp.nl>
# Copyright 2016 Opener B.V. <https://opener.am>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from os.path import join as opj
import argparse
import ast
import os
from copy import deepcopy
from lxml import etree
from sys import version_info


def read_manifest(addon_dir):
    # this script should be compatible with 9.0 and 10.0
    manifest_name = '__openerp__.py'
    if os.access(os.path.join(addon_dir, '__manifest__.py'), os.R_OK):
        manifest_name = '__manifest__.py'
    with open(os.path.join(addon_dir, manifest_name), 'r') as f:
        manifest_string = f.read()
    return ast.literal_eval(manifest_string)


# from openerp.tools
def nodeattr2bool(node, attr, default=False):
    if not node.get(attr):
        return default
    val = node.get(attr).strip()
    if not val:
        return default
    return val.lower() not in ('0', 'false', 'off')


def get_node_dict(element):
    res = {}
    for child in element:
        if 'name' in child.attrib:
            key = "./%s[@name='%s']" % (
                child.tag, child.attrib['name'])
            res[key] = child
    return res


def get_node_value(element):
    if 'eval' in element.attrib.keys():
        return element.attrib['eval']
    if 'ref' in element.attrib.keys():
        return element.attrib['ref']
    if not len(element):
        return element.text
    return etree.tostring(element)


def update_node(target, source):
    for element in source:
        if 'name' in element.attrib:
            query = "./%s[@name='%s']" % (
                element.tag, element.attrib['name'])
        else:
            # query = "./%s" % element.tag
            continue
        for existing in target.xpath(query):
            target.remove(existing)
        target.append(element)


def get_records(addon_dir):
    addon_dir = addon_dir.rstrip(os.sep)
    addon_name = os.path.basename(addon_dir)
    manifest = read_manifest(addon_dir)
    # The order of the keys are important.
    # Load files in the same order as in
    # module/loading.py:load_module_graph
    keys = ['init_xml', 'update_xml', 'data']
    records_update = {}
    records_noupdate = {}

    def process_record_node(record, noupdate):
        xml_id = record.get("id")
        if not xml_id:
            return
        if '.' in xml_id and xml_id.startswith(addon_name + '.'):
            xml_id = xml_id[len(addon_name) + 1:]
        for records in records_noupdate, records_update:
            # records can occur multiple times in the same module
            # with different noupdate settings
            if xml_id in records:
                # merge records (overwriting an existing element
                # with the same tag). The order processing the
                # various directives from the manifest is
                # important here
                update_node(records[xml_id], record)
                break
        else:
            target_dict = (
                records_noupdate if noupdate else records_update)
            target_dict[xml_id] = record

    def process_data_node(data_node):
        noupdate = nodeattr2bool(data_node, 'noupdate', False)
        record_nodes = data_node.xpath("./record")
        for record in record_nodes:
            process_record_node(record, noupdate)

    for key in keys:
        if not manifest.get(key):
            continue
        for xml_file in manifest[key]:
            xml_path = xml_file.split('/')
            try:
                # This is for a final correct pretty print
                # Ref.: https://stackoverflow.com/a/7904066
                # Also don't strip CDATA tags as needed for HTML content
                parser = etree.XMLParser(
                    remove_blank_text=True, strip_cdata=False,
                )
                tree = etree.parse(os.path.join(addon_dir, *xml_path), parser)
            except etree.XMLSyntaxError:
                continue
            # Support xml files with root Element either odoo or openerp, supporting v9.0 and v10.0
            # Condition: each xml file should have only one root element {<odoo>, <openerp> or —rarely— <data>};
            root_node = tree.getroot()
            root_node_noupdate = nodeattr2bool(root_node, 'noupdate', False)
            if root_node.tag not in ('openerp', 'odoo', 'data'):
                raise Exception(
                    'Unexpected root Element: %s in file: %s' % (
                        tree.getroot(), xml_path
                    )
                )
            for node in root_node:
                if node.tag == 'data':
                    process_data_node(node)
                elif node.tag == 'record':
                    process_record_node(node, root_node_noupdate)

    return records_update, records_noupdate


def main_analysis(old_update, old_noupdate, new_update, new_noupdate):

    odoo = etree.Element("odoo")

    for xml_id, record_new in new_noupdate.items():
        record_old = None
        if xml_id in old_update:
            record_old = old_update[xml_id]
        elif xml_id in old_noupdate:
            record_old = old_noupdate[xml_id]

        if record_old is None:
            continue

        element = etree.Element(
            "record", id=xml_id, model=record_new.attrib['model'])
        # Add forcecreate attribute if exists
        if record_new.attrib.get('forcecreate'):
            element.attrib['forcecreate'] = record_new.attrib['forcecreate']
        record_old_dict = get_node_dict(record_old)
        record_new_dict = get_node_dict(record_new)
        for key in record_old_dict.keys():
            if not record_new.xpath(key):
                # The element is no longer present.
                # Overwrite an existing value with an
                # empty one. Of course, we do not know
                # if this field has actually been removed
                attribs = deepcopy(record_old_dict[key]).attrib
                for attr in ['eval', 'ref']:
                    if attr in attribs:
                        del attribs[attr]
                element.append(
                    etree.Element(record_old_dict[key].tag, attribs))
            else:
                oldrepr = get_node_value(record_old_dict[key])
                newrepr = get_node_value(record_new_dict[key])

                if oldrepr != newrepr:
                    element.append(deepcopy(record_new_dict[key]))

        for key in record_new_dict.keys():
            if not record_old.xpath(key):
                element.append(deepcopy(record_new_dict[key]))

        if len(element):
            odoo.append(element)

    document = etree.ElementTree(odoo)
    diff = etree.tostring(
        document, pretty_print=True, xml_declaration=True, encoding='utf-8')
    if version_info[0] > 2:
        diff = diff.decode('utf-8')

    print(diff)


def main(argv=None):
    """
    Attempt to represent the differences in data records flagged with
    'noupdate' between two different versions of the same Odoo module or
    repository.

    Print out a complete XML data file that can be loaded in a post-migration
    script using openupgrade::load_xml().

        :param argv: arg1 (old) and arg2 (new) are the module o repository
        path, and arg3 (mode) are the 'module' or 'repository' options.

    Known issues:
    - Does not detect if a deleted value belongs to a field
      which has been removed.
    - Does not take csv data into account (obviously)
    - Is not able to check cross module data
    - Does not take translations into account (e.g. in the case of
      email templates)
    - Does not handle the shorthand records <menu>, <act_window> etc.,
      although that could be done using the same expansion logic as
      is used in their parsers in openerp/tools/convert.py
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'olddir', metavar='older_directory')
    parser.add_argument(
        'newdir', metavar='newer_directory')
    parser.add_argument(
        '--mode', metavar='module/repository', default='module')
    arguments = parser.parse_args(argv)
    print("\n")

    if arguments.mode == "module":
        print(arguments.olddir.split('/')[-1] + ":\n")
        old_update, old_noupdate = get_records(arguments.olddir)
        new_update, new_noupdate = get_records(arguments.newdir)
        main_analysis(old_update, old_noupdate, new_update, new_noupdate)

    elif arguments.mode == "repository":
        old_module_list, new_module_list = [], []
        for mname in ('__manifest__.py', '__openerp__.py'):
            old_module_list += filter(
                lambda m: os.path.isfile(
                    opj(arguments.olddir, m, mname)),
                os.listdir(arguments.olddir))
            new_module_list += filter(
                lambda m: os.path.isfile(
                    opj(arguments.newdir, m, mname)),
                os.listdir(arguments.newdir))
        for module_name in set(old_module_list).intersection(new_module_list):
            print(module_name + ":\n")
            old_update, old_noupdate = get_records(
                opj(arguments.olddir, module_name))
            new_update, new_noupdate = get_records(
                opj(arguments.newdir, module_name))
            main_analysis(old_update, old_noupdate, new_update, new_noupdate)


if __name__ == "__main__":
    main()
