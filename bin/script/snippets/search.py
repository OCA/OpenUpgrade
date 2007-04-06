import uno
from com.sun.star.awt.FontWeight import BOLD

"""def SimpleSearchExample():
    localContext = uno.getComponentContext()

    resolver = localContext.ServiceManager.createInstanceWithContext(
                    "com.sun.star.bridge.UnoUrlResolver", localContext )

    smgr = resolver.resolve( "uno:socket,host=localhost,port=2002;urp;StarOffice.ServiceManager" )
    remoteContext = smgr.getPropertyValue( "DefaultContext" )

    #remoteContext = resolver.resolve( "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext" )
    #smgr = remoteContext.ServiceManager

    desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",remoteContext)


    # open a writer document
    doc =desktop.getCurrentComponent()
    # Create a descriptor from a searchable document.
    vDescriptor = doc.createSearchDescriptor()
    # Set the text for which to search and other

    vDescriptor.SearchString = "[[ repeatIn(objects,'o') ]]"
    # These all default to false
    vDescriptor.SearchWords = True
    vDescriptor.SearchCaseSensitive = False
    # Find the first one
    vFound = doc.findFirst(vDescriptor)

    while not vFound == None:
        print vFound.getString()
        #vFound.CharWeight = "FontWeight.BOLD"
        vFound = doc.findNext( vFound.End, vDescriptor)

SimpleSearchExample()"""

def deleteTextBetweenDlimiters():
    localContext = uno.getComponentContext()

    resolver = localContext.ServiceManager.createInstanceWithContext(
                    "com.sun.star.bridge.UnoUrlResolver", localContext )

    smgr = resolver.resolve( "uno:socket,host=localhost,port=2002;urp;StarOffice.ServiceManager" )
    remoteContext = smgr.getPropertyValue( "DefaultContext" )

    #remoteContext = resolver.resolve( "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext" )
    #smgr = remoteContext.ServiceManager

    desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",remoteContext)


    # open a writer document
    oDoc =desktop.getCurrentComponent()
    # Create descriptors from the searchable document.
    vOpenSearch = oDoc.createSearchDescriptor()
    vCloseSearch = oDoc.createSearchDescriptor()
    # Set the text for which to search and other
    vOpenSearch.SearchString = "repeatIn"
    vCloseSearch.SearchString = "')"
    # Find the first open delimiter
    vOpenFound = oDoc.findFirst(vOpenSearch)
    while not vOpenFound==None:
        #Search for the closing delimiter starting from the open delimiter
        vCloseFound = oDoc.findNext( vOpenFound.End, vCloseSearch)
        if vCloseFound==None:
            print "Found an opening bracket but no closing bracket!"
            break
        else:
            vOpenFound.gotoRange(vCloseFound, True)
            print vOpenFound.getString()
            vOpenFound = oDoc.findNext( vOpenFound.End, vOpenSearch)
        #End If
    #End while Loop
#End def

deleteTextBetweenDlimiters()