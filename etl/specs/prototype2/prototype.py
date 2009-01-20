#csv_in ---> logger
import csv

class component(object):
    def __init__(self,*args, **argv):
        self.is_start=argv.get('is_start', False)
        self.data=[]
        self.job=None
        self.trans_out = []
        self.trans_in = []

    def event(self,name,channel=None):
        return self.output(channel=channel,event=name)
    def start(self):
        self.event('component_start')
        return True
    def stop(self):
        self.event('component_end')
        return True
    def run(self,data=[]):
        self.event('component_run')        
        return data

    def input(self, rows=None,channel=None, transition=None):
        self.event('component_inputflow',channel)
        return rows

    def output(self, rows=None, channel=None,event=None):
        self.event('component_outputflow',channel)
        for trans in self.trans_out:
            if (not channel) or (trans.channel_source==channel) or (not trans.channel_source):
                if trans.type=='data_transition' or (trans.type=='trigger_transition' and event==trans.listen_event):
                    yield rows, trans.destination
                else:
                    yield rows,None

class csv_in(component):
    def __init__(self, filename, *args, **argv):
        super(csv_in, self).__init__(*args, **argv)
        self.filename = filename
        self.fp=None
    def start(self):
        self.fp = csv.DictReader(file(self.filename))
        return super(csv_in, self).start()
    
    def input(self,rows=[]):   
        data=[]     
        for row in self.fp:
            data.append(row)
        return super(csv_in, self).input(data)

class csv_out(component):
    def __init__(self, filename, *args, **argv):
        super(csv_out, self).__init__(*args, **argv)
        self.filename=filename
        self.fp=None

    def start(self):
        self.fp = file(self.filename, 'wb+')
        return super(csv_out, self).start()

    def input(self,rows=[]):
        fieldnames = rows[0].keys()
        fp = csv.DictWriter(self.fp, fieldnames)
        fp.writerow(dict(map(lambda x: (x,x), fieldnames)))
        fp.writerows(rows)        
        return super(csv_out, self).input(rows)

class sort(component):
    def __init__(self, fieldname, *args, **argv):
        self.fieldname = fieldname
        super(sort, self).__init__(*args, **argv)    

    def run(self,rows=[], transition=None):
        self.data=rows
        self.data.sort(lambda x,y: cmp(x[self.fieldname],y[self.fieldname]))
        return super(sort, self).run(self.data)     

    

class logger(component):
    def __init__(self, name, *args, **argv):
        self.name = name
        super(logger, self).__init__(*args, **argv) 
    def run(self,data=[]): 
        res=[]    
        print ' Logger : ',self.name
        for row in data:
            print row
            res.append(row)
        return super(logger, self).run(data)

class transition(object):
    def __init__(self, source, destination,type='data_transition', status='open', channel_source=None, channel_destination=None):
        self.type=type
        self.source = source
        self.source.trans_out.append(self)
        self.destination = destination
        self.destination.trans_in.append(self)
        self.status = 'open'
        self.channel_source = channel_source
        self.channel_destination = channel_destination

class job(object):
    def __init__(self,components=[]):
        self.components=components        
        for component in components:
            component.job=self

    def run(self):
        data=None           
        def _run(data,component):            
            if not component:
                return            
            res=component.start()        
            if not res:
                raise Exception('not started component')
            try:          
                res_process=component.run(data)      
                res_input=component.input(res_process)
                                 
                res_output=component.output(res_input)               
                for out_data,out_component in res_output:                    
                    _run(out_data,out_component)
            except Exception,e:
                raise e
            finally:
                component.stop() 
        for component in self.components:
            if component.is_start:
                _run(data,component)    
            


csv_in1= csv_in('partner.csv',is_start=True)
csv_in2= csv_in('partner1.csv',is_start=True)
csv_out1= csv_out('partner2.csv')
sort1=sort('name')
log1=logger(name='Read Partner File')
log2=logger(name='After Sort')

tran=transition(csv_in1,log1)
tran1=transition(csv_in2,log1)
tran2=transition(csv_in1,sort1)
tran3=transition(csv_in2,sort1)
tran4=transition(sort1,csv_out1)
tran5=transition(sort1,log2)

job1=job([csv_in1,csv_in2,log1,sort1,log2])

job1.run()

# csv_in1  -> log1
# csv_in2  -> log1
# csv_in1  -> sort1 
# csv_in2  -> sort1 -> csv_out1
#                   -> log2







