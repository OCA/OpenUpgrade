# -*- encoding: utf-8 -*-
##############################################################################
#
#    ETL system- Extract Transfer Load system
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
"""
 To provide connectivity with OpenERP server.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License.
"""
from etl.connector import connector
from xml.etree import ElementTree as ET
from lxml import etree

class xml_connector(connector):
    """
    This is an ETL connector that is used to provide connectivity with OpenERP server.
    """
    def __init__(self, tree, name='xml_connector'):
        
       super(xml_connector, self).__init__()
       self._type = 'connector.xml_connector'
       self.tree = tree
      
    def open(self,node):
        res = {}
        res[node.tag] = []
        result=self.xmltodict(node,res[node.tag])
        reply = {}
        reply[node.tag] = {'value':res[node.tag],'attributes':node.attrib}
        return reply

    def xmltodict(self,node,res):
        rep = {}
        if len(node):
            #n = 0
            for n in list(node):
                rep[node.tag] = []
                value = self.xmltodict(n,rep[node.tag])
                if len(n):
                    
                    value = {'value':rep[node.tag],'attributes':n.attrib}
                    res.append({n.tag:value})
                else :
                    res.append(rep[node.tag][0])
        else:
            value = {}
            value = {'value':node.text,'attributes':node.attrib}
            res.append({node.tag:value})
        return res
        
    
    
def main():
    tree = etree.parse('/home/tiny/Desktop/xml-dict-xml/XMLtest.xml')
    res = open(tree.getroot())

if __name__ == '__main__' :
    main()
    
    
