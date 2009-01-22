#!/usr/bin/python

#
# Proof of concept ETL computation
#

class node(object):
    def __init__(self, *args, **argv):
        self.meta = None
        self.has_input = True
        self.has_output = True
        self.is_start = argv.get('is_start', False)
        self.name = argv.get('name', '')
        self.trans_out = []
        self.trans_in = []
        self.stopped = []

    # When a flow starts, it should pass elements like meta to next flows
    def start(self, transition=None):
        for trans in self.trans_out:
            trans.destination.start(trans)
        return True

    # Called when the transition is done
    def stop(self, transition=None):
        if transition:
            self.stopped.append(transition)
            ok = True
            for t in self.trans_in:
                if t not in self.stopped:
                    ok=False
        else:
            ok = True
        if ok:
            for trans in self.trans_out:
                trans.destination.stop(trans)
        return ok

    #
    # This function is called for all starting element when the job is run
    # it should read the element and call input method on them, finishing by a stop.
    #
    def run(self):
        self.start()
        self.stop()

    def output(self, rows, channel=None):
        for trans in self.trans_out:
            if (not channel) or (trans.channel_source==channel) or (not trans.channel_source):
                trans.destination.input(rows, trans)

    def input(self, rows, transition=None):
        self.output(rows)

class transition(object):
    def __init__(self, source, destination, status='open', channel_source=None, channel_destination=None):
        self.source = source
        self.source.trans_out.append(self)
        self.destination = destination
        self.destination.trans_in.append(self)
        self.status = 'open'
        self.channel_source = channel_source
        self.channel_destination = channel_destination


class job(object):
    def __init__(self, nodes):
        self.nodes = nodes

    def run(self):
        for n in self.nodes:
            if n.is_start:
                n.run()

