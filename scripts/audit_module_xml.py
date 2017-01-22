#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    audit_module_xml
    ~~~~~~~~~~~~~~~~

    Compares Odoo module xml data files against Odoo database content
    providing various diagnostic output.

    Usage::

        audit_module_xml.py path-to-odoo-module db-connection-uri

    Where db-connection-uri has following form::

    postgresql://[user[:password]@][netloc][:port][/dbname][?param1=value1&...]

    :copyright: (c) 2014 Priit Laes, Povi Software LLC
    :license: GPLv3, see LICENSE for more details
"""
import argparse
import ast
import os

from lxml import etree

import psycopg2


class ir_actions_act_window(object):
    __table__ = 'ir_act_window'
    __fields__ = ['res_model', 'domain', 'view_type', 'context']
    __field_defaults__ = {
        'context': '{}',
    }

    def __init__(self, id, data):
        self.id = id
        for f in self.__fields__:
            if f not in self.__field_defaults__:
                setattr(self, f, None)
            else:
                setattr(self, f, self.__field_defaults__[f])
        for c in data.getchildren():
            if c.tag != 'field':
                raise NotImplementedError
            if 'name' in c.attrib and c.attrib['name'] in self.__fields__:
                setattr(self, c.attrib['name'], c.text)

    def __repr__(self):
        return '<%r : %r>' % (self.__class__.__name__,
                              {x: getattr(self, x) for x in self.__fields__})


def analyze(conn, filename, data):
    cur = conn.cursor()
    print ("Analyzing {}".format(filename))
    for item in data:
        # First, look up the resource id from ir_model_data table...
        fields = ['name', 'module', 'model', 'res_id']
        SQL = "SELECT {} FROM ir_model_data WHERE name = %s;".format(','.join(fields))
        cur.execute(SQL, (item.id,))
        if cur.rowcount == 0:
            print ("WARNING: '{}'.<{}> was not found in database".format(item.id, item.__class__.__name__))
            continue
        elif cur.rowcount > 1:
            print ("WARNING: Found multiple records for '{}'.<{}>".format(item.id, item.__class__.__name__))
            continue
        row = dict(zip(fields, next(cur)))
        # ...fetch the data for the record itself
        SQL = "SELECT {} FROM {} WHERE id = %s".format(','.join(item.__fields__), item.__table__)
        cur.execute(SQL, (row['res_id'],))
        assert cur.rowcount == 1
        row = dict(zip(item.__fields__, next(cur)))
        # ... and compare the fields
        issues = []
        for field in item.__fields__:
            if getattr(item, field) != row[field]:
                issues.append(field)
        if not issues:
            continue
        print ("WARNING: Found issues with '{}'.<{}>:".format(item.id, item.__class__.__name__))
        for issue in issues:
            print ("\t'{}' -> XML:`{}`!= DB:`{}`".format(issue, getattr(item, issue), row[issue]))


def parse_record(data):
    attr = data.attrib
    id, type = attr['id'], attr['model']
    if type == 'ir.actions.act_window':
        return ir_actions_act_window(id, data)
    print ("Unimplemented: {}".format(type))


def parse_file(file):
    records = []
    for item in etree.parse(file).getroot().getchildren():
        assert item.tag == 'data'
        for d in item.getchildren():
            # skip comments
            if not isinstance(d.tag, basestring):
                continue
            if d.tag == 'record':
                record = parse_record(d)
                if record:
                    records.append(record)
    return records


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Post-migration auditing for Odoo XML data.')
    parser.add_argument("module_path", help="Path to module")
    parser.add_argument("db_uri", help="Connection URI for Odoo database")
    args = parser.parse_args()

    # Check whether module_dir exists ...
    if not os.path.isdir(args.module_path):
        parser.error(message="module_path '{}' does not exist.".format(args.module_path))
    # ...and contains valid odoo module
    odoo_py = os.path.join(args.module_path, '__openerp__.py')
    if not os.path.exists(odoo_py):
        parser.error(message="module_path '{}' does not contain valid Odoo module .".format(args.module_path))

    conn = psycopg2.connect(args.db_uri)

    try:
        with open(odoo_py, "r") as data:
            dictionary = ast.literal_eval(data.read())
        if 'data' not in dictionary:
            raise SyntaxError
    except SyntaxError:
        parser.exit(message="'{}' does not contain valid 'data' section.\n".format(odoo_py))
    files = (item for item in dictionary['data'] if item.endswith('.xml'))
    records = {f: parse_file(os.path.join(args.module_path, f)) for f in files}

    for file, items in records.iteritems():
        analyze(conn, file, items)
