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
  To handle ETL signal.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). 
 GNU General Public License

"""
class signal(object):
    """
    ETL Signal.
    Each component can send signals. Trigger Transitions can listen to these signals.
    Signals are automatically generated:
       - start : When the component starts
       - start_input : At the first row received by the component
       - start_output : At the first row send by the component
       - no_input : At the end of the process, if no data received
       - stop : when the component is set as pause
       - continue : when the component restart after a pause
       - end : When the component finnished is process
       - error : When the component give error
    """
    def __init__(self,*args, **argv):
        self.__connects={}  
    
    def signal(self, signal, signal_data=None):
        for fnct,data,key in self.__connects.get(signal, []):
            fnct(key, signal_data, *data)
        

    def signal_connect(self, key, signal, fnct, *data):
        self.__connects.setdefault(signal, [])
        if (fnct, data, key) not in self.__connects[signal]:
            self.__connects[signal].append((fnct, data, key))
        

    def signal_unconnect(self, key, signal=None):
        if not signal:
            signal = self.__connects.keys()
        else:
            signal = [signal]
        for sig in signal:
            i=0
            while i<len(self.__connects[sig]):
                if self.__connects[sig][i][2]==key:
                    del self.__connects[sig][i]
                else:
                    i+=1
    





