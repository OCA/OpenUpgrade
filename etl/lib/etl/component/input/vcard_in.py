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
To import data from vcard

Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
GNU General Public License
"""

from etl.component import component

class vcard_in(component):
    def __init__(self,fileconnector,name='component.input.vcard_in'):
        """
        Parameters ::
        fileconnector : It is a required field and it provides  local file connector to connect with file.
        """
        super(vcard_in, self).__init__(name)
        self.fileconnector = fileconnector             
    
    
    def process(self):
        try:
            import vobject 
            fp=self.fileconnector.open('r')        
            s = "".join(fp.readlines())
            reader = vobject.readComponents(s)
            while True:
                row={}
                data=reader.next()
                for d in data.contents:
                    row[unicode(d)]=eval('data.'+unicode(d)+'.value')                    
                yield row,'main'
            self.fileconnector.close(fp)
        except IOError,e:
            self.signal('error',{'data':self.data,'type':'exception','error':str(e)})


    def __copy__(self):
        """
        Overrides copy method
        """
        res=vcard_in(self.fileconnector, self.name)
        return res

def test():
    pass

if __name__ == '__main__':
    test() 
