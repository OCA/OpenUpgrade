from xml.sax.saxutils import escape

class Node( object ):
    def __init__( self, name, *children ):
        self.name= name
        self.children= children
    def toXml( self, indent ):
        if len(self.children) == 0:
            return u"%s<%s/>" % ( indent*4*u' ', self.name )
        elif len(self.children) == 1:
            child= self.children[0].toXml(0)
            return u"%s<%s>%s</%s>" % ( indent*4*u' ', self.name, child, self.name )
        else:
            items = [ u"%s<%s>" % ( indent*4*u' ', self.name ) ]
            items.extend( [ c.toXml(indent+1) for c in self.children ] )
            items.append( u"%s</%s>" % ( indent*4*u' ', self.name ) )
            return u"\n".join( items )

class Text( Node ):
    def __init__( self, value ):
        self.value= value
    def toXml( self, indent ):
        def unicodify(o):
            if o is None:
                return u'';
            return unicode(o)
        return "%s%s" % ( indent*4*u' ', escape( unicodify(self.value) ), )

def dictToXml(d):

    def dictToNodeList(node):
        nodes= []
        for name, value in node.iteritems():
            if isinstance(value, dict):
                n= Node( name, *dictToNodeList( value ) )
                nodes.append( n )
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        n= Node( name, *dictToNodeList( value ) )
                        nodes.append( n )
                    else:
                        n= Node( name, Text( item ) )
                        nodes.append( n )
            else:
                n= Node( name, Text( value ) )
                nodes.append( n )
        return nodes

    return u"\n".join( [ n.toXml(0) for n in dictToNodeList(d) ] )

dictn={'a': 'aaa', 'school': {'id': '1', 'name': ' high-school '}}


if __name__ == '__main__':
    res=  dictToXml(dictn)
    print res

