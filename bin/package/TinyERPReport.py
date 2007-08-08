__name__="package"

import uno
import unohelper
import os
#--------------------------------------------------
# An ActionListener adapter.
# This object implements com.sun.star.awt.XActionListener.
# When actionPerformed is called, this will call an arbitrary
#  python procedure, passing it...
#   1. the oActionEvent
#   2. any other parameters you specified to this object's constructor (as a tuple).
os.system( "ooffice '-accept=socket,host=localhost,port=2002;urp;'" )
passwd=""
database=""
loginstatus=False
from com.sun.star.awt import XActionListener
class ActionListenerProcAdapter( unohelper.Base, XActionListener ):
    def __init__( self, oProcToCall, tParams=() ):
        self.oProcToCall = oProcToCall # a python procedure
        self.tParams = tParams # a tuple

    # oActionEvent is a com.sun.star.awt.ActionEvent struct.
    def actionPerformed( self, oActionEvent ):
        if callable( self.oProcToCall ):
            apply( self.oProcToCall, (oActionEvent,) + self.tParams )

#--------------------------------------------------
# An ItemListener adapter.
# This object implements com.sun.star.awt.XItemListener.
# When itemStateChanged is called, this will call an arbitrary
#  python procedure, passing it...
#   1. the oItemEvent
#   2. any other parameters you specified to this object's constructor (as a tuple).
from com.sun.star.awt import XItemListener
class ItemListenerProcAdapter( unohelper.Base, XItemListener ):
    def __init__( self, oProcToCall, tParams=() ):
        self.oProcToCall = oProcToCall # a python procedure
        self.tParams = tParams # a tuple

    # oItemEvent is a com.sun.star.awt.ItemEvent struct.
    def itemStateChanged( self, oItemEvent ):
        if callable( self.oProcToCall ):
            apply( self.oProcToCall, (oItemEvent,) + self.tParams )

#--------------------------------------------------
# An TextListener adapter.
# This object implements com.sun.star.awt.XTextistener.
# When textChanged is called, this will call an arbitrary
#  python procedure, passing it...
#   1. the oTextEvent
#   2. any other parameters you specified to this object's constructor (as a tuple).
from com.sun.star.awt import XTextListener
class TextListenerProcAdapter( unohelper.Base, XTextListener ):
    def __init__( self, oProcToCall, tParams=() ):
        self.oProcToCall = oProcToCall # a python procedure
        self.tParams = tParams # a tuple

    # oTextEvent is a com.sun.star.awt.TextEvent struct.
    def textChanged( self, oTextEvent ):
        if callable( self.oProcToCall ):
            apply( self.oProcToCall, (oTextEvent,) + self.tParams )


if __name__<>"package":
    from gui import *
class ErrorDialog:
    def __init__(self,sErrorMsg, sErrorHelpMsg="",sTitle="Error Message"):
        self.win = DBModalDialog(50, 50, 150, 90, sTitle)
        self.win.addFixedText("lblErrMsg", 5, 5, 190, 25, sErrorMsg)
        self.win.addFixedText("lblErrHelpMsg", 5, 30, 190, 25, sErrorHelpMsg)
        self.win.addButton('btnOK', 55,-5,40,15,'Ok'
                     ,actionListenerProc = self.btnOkOrCancel_clicked )
        self.win.doModalDialog("",None)
    def btnOkOrCancel_clicked( self, oActionEvent ):
        self.win.endExecute()

import uno
import xmlrpclib
import re
import socket
import cPickle
import marshal
import tempfile
if __name__<>"package":
    from gui import *

def genTree(object,aList,insField,host,level=3, ending=[], ending_excl=[], recur=[], root='', actualroot=""):
    try:
        sock = xmlrpclib.ServerProxy(host+'/xmlrpc/object')
        desktop=getDesktop()
        doc =desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        res = sock.execute(database, 3, docinfo.getUserFieldValue(1), object , 'fields_get')
        key = res.keys()
        key.sort()
        for k in key:
            if (not ending or res[k]['type'] in ending) and ((not ending_excl) or not (res[k]['type'] in ending_excl)):
                insField.addItem(root+'/'+res[k]["string"],aList.__len__())#getListBoxItemCount("lstFields"))
                aList.append(actualroot+'/'+k)
            if (res[k]['type'] in recur) and (level>0):
                genTree(res[k]['relation'],aList,insField,host ,level-1, ending, ending_excl, recur,root+'/'+res[k]["string"],actualroot+'/'+k)
    except:
        import traceback;traceback.print_exc()

def VariableScope(oTcur,insVariable,aObjectList,aComponentAdd,aItemList,sTableName=""):
    if sTableName.find(".") != -1:
        for i in range(aItemList.__len__()):
            if aComponentAdd[i]==sTableName:
                sLVal=aItemList[i].__getitem__(1).__getslice__(aItemList[i].__getitem__(1).find(",'")+2,aItemList[i].__getitem__(1).find("')"))
                for j in range(aObjectList.__len__()):
                    if aObjectList[j].__getslice__(0,aObjectList[j].find("(")) == sLVal:
                        insVariable.addItem(aObjectList[j],1)
        VariableScope(oTcur,insVariable,aObjectList,aComponentAdd,aItemList, sTableName.__getslice__(0,sTableName.rfind(".")))
    else:
        for i in range(aItemList.__len__()):
            if aComponentAdd[i]==sTableName:
                sLVal=aItemList[i].__getitem__(1).__getslice__(aItemList[i].__getitem__(1).find(",'")+2,aItemList[i].__getitem__(1).find("')"))
                for j in range(aObjectList.__len__()):
                    if aObjectList[j].__getslice__(0,aObjectList[j].find("(")) == sLVal and sLVal!="":
                        insVariable.addItem(aObjectList[j],1)

def getList(aObjectList,host,count):
    desktop=getDesktop()
    doc =desktop.getCurrentComponent()
    docinfo=doc.getDocumentInfo()
    sMain=""
    if not count == 0:
        if count >= 1:
            oParEnum = doc.getTextFields().createEnumeration()
            while oParEnum.hasMoreElements():
                oPar = oParEnum.nextElement()
                if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                    sItem=oPar.Items.__getitem__(1)
                    if sItem.__getslice__(sItem.find("(")+1,sItem.find(","))=="objects":
                        sMain = sItem.__getslice__(sItem.find(",'")+2,sItem.find("')"))
            oParEnum = doc.getTextFields().createEnumeration()
            aObjectList.append("List of " + docinfo.getUserFieldValue(3))
            while oParEnum.hasMoreElements():
                oPar = oParEnum.nextElement()
                if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                    sItem=oPar.Items.__getitem__(1)
                    if sItem.__getslice__(sItem.find("[[ ")+3,sItem.find("("))=="repeatIn":
                        if sItem.__getslice__(sItem.find("(")+1,sItem.find(","))=="objects":
                            aObjectList.append(sItem.__getslice__(sItem.rfind(",'")+2,sItem.rfind("')")) + "(" + docinfo.getUserFieldValue(3) + ")")
                        else:
                            sTemp=sItem.__getslice__(sItem.find("(")+1,sItem.find(","))
                            if sMain == sTemp.__getslice__(0,sTemp.find(".")):
                                getRelation(docinfo.getUserFieldValue(3), sItem.__getslice__(sItem.find(".")+1,sItem.find(",")), sItem.__getslice__(sItem.find(",'")+2,sItem.find("')")),aObjectList,host)
                            else:
                                sPath=getPath(sItem.__getslice__(sItem.find("(")+1,sItem.find(",")), sMain)
                                getRelation(docinfo.getUserFieldValue(3), sPath.__getslice__(sPath.find(".")+1,sPath.__len__()), sItem.__getslice__(sItem.find(",'")+2,sItem.find("')")),aObjectList,host)
    else:
        aObjectList.append("List of " + docinfo.getUserFieldValue(3))

def getRelation(sRelName, sItem, sObjName, aObjectList, host ):
        sock = xmlrpclib.ServerProxy(host+'/xmlrpc/object')
        desktop=getDesktop()
        doc =desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        res = sock.execute(database, 3, docinfo.getUserFieldValue(1), sRelName , 'fields_get')
        key = res.keys()
        for k in key:
            if sItem.find(".") == -1:
                if k == sItem:
                    aObjectList.append(sObjName + "(" + res[k]['relation'] + ")")
                    return 0
            if k == sItem.__getslice__(0,sItem.find(".")):
                getRelation(res[k]['relation'], sItem.__getslice__(sItem.find(".")+1,sItem.__len__()), sObjName,aObjectList,host)


def getPath(sPath,sMain):
    desktop=getDesktop()
    doc =desktop.getCurrentComponent()
    oParEnum = doc.getTextFields().createEnumeration()
    while oParEnum.hasMoreElements():
        oPar = oParEnum.nextElement()
        if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
            sItem=oPar.Items.__getitem__(1)
            if sPath.__getslice__(0,sPath.find(".")) == sMain:
                break;
            else:
                if sItem.__getslice__(sItem.find(",'")+2,sItem.find("')")) == sPath.__getslice__(0,sPath.find(".")):
                    sPath =  sItem.__getslice__(sItem.find("(")+1,sItem.find(",")) + sPath.__getslice__(sPath.find("."),sPath.__len__())
                    getPath(sPath, sMain)
    return sPath


def EnumDocument(aItemList,aComponentAdd):
    desktop = getDesktop()
    Doc =desktop.getCurrentComponent()
    #oVC = Doc.CurrentController.getViewCursor()
    oParEnum = Doc.getText().createEnumeration()
    while oParEnum.hasMoreElements():
        oPar = oParEnum.nextElement()
        if oPar.supportsService("com.sun.star.text.TextTable"):
            getChildTable(oPar,aItemList,aComponentAdd)
        if oPar.supportsService("com.sun.star.text.Paragraph"):
            oSecEnum = oPar.createEnumeration()
            while oSecEnum.hasMoreElements():
                oSubSection = oSecEnum.nextElement()
                if oSubSection.TextSection:
                    if oSubSection.TextField:
                        aItemList.append( oSubSection.TextField.Items )
                        aComponentAdd.append(oSubSection.TextSection.Name)
                elif oPar.getAnchor().TextField:
                    sItem=oPar.getAnchor().TextField.Items.__getitem__(1)
                    if sItem.__getslice__(sItem.find("[[ ")+3,sItem.find("("))=="repeatIn":
                        aItemList.append(oSubSection.TextField.Items )
                        aComponentAdd.append("Document")

def getChildTable(oPar,aItemList,aComponentAdd,sTableName=""):
    sNames = oPar.getCellNames()
    bEmptyTableFlag=True
    for val in sNames:
        oCell = oPar.getCellByName(val)
        oCurEnum = oCell.createEnumeration()
        while oCurEnum.hasMoreElements():
            try:
                oCur = oCurEnum.nextElement()

                if oCur.supportsService("com.sun.star.text.TextTable"):
                    if sTableName=="":
                        getChildTable(oCur,aItemList,aComponentAdd,oPar.Name)
                    else:
                        getChildTable(oCur,aItemList,aComponentAdd,sTableName+"."+oPar.Name)
                else:
                    oSecEnum = oCur.createEnumeration()
                    while oSecEnum.hasMoreElements():
                        oSubSection = oSecEnum.nextElement()
                        if oSubSection.supportsService("com.sun.star.text.TextField"):
                            bEmptyTableFlag=False
                            sItem=oSubSection.TextField.Items.__getitem__(1)
                            if sItem.__getslice__(sItem.find("[[ ")+3,sItem.find("("))=="repeatIn":
                                if aItemList.__contains__(oSubSection.TextField.Items)==False:
                                    aItemList.append(oSubSection.TextField.Items)
                                if sTableName=="":
                                    if  aComponentAdd.__contains__(oPar.Name)==False:
                                        aComponentAdd.append(oPar.Name)
                                else:
                                    if aComponentAdd.__contains__(sTableName+"."+oPar.Name)==False:
                                        aComponentAdd.append(sTableName+"."+oPar.Name)

            except:
                import traceback;traceback.print_exc()
    if bEmptyTableFlag==True:
        aItemList.append((u'',u''))
        if sTableName=="":
            if  aComponentAdd.__contains__(oPar.Name)==False:
                aComponentAdd.append(oPar.Name)
        else:
            if aComponentAdd.__contains__(sTableName+"."+oPar.Name)==False:
                aComponentAdd.append(sTableName+"."+oPar.Name)
    return 0

def getRecersiveSection(oCurrentSection,aSectionList):
        desktop=getDesktop()
        doc =desktop.getCurrentComponent()
        oParEnum=doc.getText().createEnumeration()
        aSectionList.append(oCurrentSection.Name)
        if oCurrentSection.ParentSection:
            getRecersiveSection(oCurrentSection.ParentSection,aSectionList)
        else:
            return
def getConnectionStatus(url):
    m = re.match('^(http[s]?://|socket://)([\w.\-]+):(\d{1,5})$', url or '')
    if not m:
        return -1
    if m.group(1) == 'http://' or m.group(1) == 'https://':
        sock = xmlrpclib.ServerProxy(url + '/xmlrpc/db')
        try:
            return sock.list()
        except:
            return -1
    else:
        sock = mysocket
        #sock = xmlrpclib.ServerProxy(url + '/xmlrpc/common')
        try:
            sock.connect(m.group(2), int(m.group(3)))
            sock.mysend(('db', 'list'))
            res = sock.myreceive()
            sock.disconnect()
            return res
        except Exception, e:
            return -1

class Myexception(Exception):
    def __init__(self, faultCode, faultString):
        self.faultCode = faultCode
        self.faultString = faultString

class mysocket:
    def __init__(self, sock=None):
        print "abc"
        if sock is None:
            self.sock = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
        self.sock.settimeout(60)
    def connect(self, host, port=False):
        if not port:
            protocol, buf = host.split('//')
            host, port = buf.split(':')
        self.sock.connect((host, int(port)))
    def disconnect(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
    def mysend(self, msg, exception=False, traceback=None):
        msg = cPickle.dumps([msg,traceback])
        size = len(msg)
        self.sock.send('%8d' % size)
        self.sock.send(exception and "1" or "0")
        totalsent = 0
        while totalsent < size:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError, "socket connection broken"
            totalsent = totalsent + sent
    def myreceive(self):
        buf=''
        while len(buf) < 8:
            chunk = self.sock.recv(8 - len(buf))
            if chunk == '':
                raise RuntimeError, "socket connection broken"
            buf += chunk
        size = int(buf)
        buf = self.sock.recv(1)
        if buf != "0":
            exception = buf
        else:
            exception = False
        msg = ''
        while len(msg) < size:
            chunk = self.sock.recv(size-len(msg))
            if chunk == '':
                raise RuntimeError, "socket connection broken"
            msg = msg + chunk
        res = cPickle.loads(msg)
        if isinstance(res[0],Exception):
            if exception:
                raise Myexception(str(res[0]), str(res[1]))
            raise res[0]
        else:
            return res[0]

def GetAFileName():
    oFileDialog=None
    iAccept=None
    sPath=""
    InitPath=""
    oUcb=None
    oFileDialog = createUnoService("com.sun.star.ui.dialogs.FilePicker")
    oUcb = createUnoService("com.sun.star.ucb.SimpleFileAccess")
    oFileDialog.appendFilter("TinyReport File","*.sxw")
    oFileDialog.setCurrentFilter("TinyReport File")
    if InitPath == "":
        InitPath =tempfile.gettempdir()
    #End If
    if oUcb.exists(InitPath):
        oFileDialog.setDisplayDirectory(InitPath)
    #End If
    iAccept = oFileDialog.execute()
    if iAccept == 1:
        sPath = oFileDialog.Files[0]
    oFileDialog.dispose()
    return sPath


import uno
import unohelper
if __name__<>"package":
    from actions import *


#------------------------------------------------------------
#   Uno ServiceManager access
#   A different version of this routine and global variable
#    is needed for code running inside a component.
#------------------------------------------------------------


# The ServiceManager of the running OOo.
# It is cached in a global variable.
goServiceManager = False
def getServiceManager( cHost="localhost", cPort="2002" ):
    """Get the ServiceManager from the running OpenOffice.org.
        Then retain it in the global variable goServiceManager for future use.
        This is similar to the GetProcessServiceManager() in OOo Basic.
    """
    global goServiceManager
    if not goServiceManager:
        # Get the uno component context from the PyUNO runtime
        oLocalContext = uno.getComponentContext()
        # Create the UnoUrlResolver on the Python side.
        oLocalResolver = oLocalContext.ServiceManager.createInstanceWithContext(
                                    "com.sun.star.bridge.UnoUrlResolver", oLocalContext )
        # Connect to the running OpenOffice.org and get its context.
        oContext = oLocalResolver.resolve( "uno:socket,host=" + cHost + ",port=" + cPort + ";urp;StarOffice.ComponentContext" )
        # Get the ServiceManager object
        goServiceManager = oContext.ServiceManager
    return goServiceManager


#------------------------------------------------------------
#   Uno convenience functions
#   The stuff in this section is just to make
#    python progrmaming of OOo more like using OOo Basic.
#------------------------------------------------------------


# This is the same as ServiceManager.createInstance( ... )
def createUnoService( cClass ):
    """A handy way to create a global objects within the running OOo.
    Similar to the function of the same name in OOo Basic.
    """
    oServiceManager = getServiceManager()
    oObj = oServiceManager.createInstance( cClass )
    return oObj


# The StarDesktop object.  (global like in OOo Basic)
# It is cached in a global variable.
StarDesktop = None
def getDesktop():
    """An easy way to obtain the Desktop object from a running OOo.
    """
    global StarDesktop
    if StarDesktop == None:
        StarDesktop = createUnoService( "com.sun.star.frame.Desktop" )
    return StarDesktop
# preload the StarDesktop variable.
getDesktop()


# The CoreReflection object.
# It is cached in a global variable.
goCoreReflection = False
def getCoreReflection():
    global goCoreReflection
    if not goCoreReflection:
        goCoreReflection = createUnoService( "com.sun.star.reflection.CoreReflection" )
    return goCoreReflection


def createUnoStruct( cTypeName ):
    """Create a UNO struct and return it.
    Similar to the function of the same name in OOo Basic.
    """
    oCoreReflection = getCoreReflection()
    # Get the IDL class for the type name
    oXIdlClass = oCoreReflection.forName( cTypeName )
    # Create the struct.
    oReturnValue, oStruct = oXIdlClass.createObject( None )
    return oStruct

#------------------------------------------------------------
#   API helpers
#------------------------------------------------------------

def hasUnoInterface( oObject, cInterfaceName ):
    """Similar to Basic's HasUnoInterfaces() function, but singular not plural."""

    # Get the Introspection service.
    oIntrospection = createUnoService( "com.sun.star.beans.Introspection" )

    # Now inspect the object to learn about it.
    oObjInfo = oIntrospection.inspect( oObject )

    # Obtain an array describing all methods of the object.
    oMethods = oObjInfo.getMethods( uno.getConstantByName( "com.sun.star.beans.MethodConcept.ALL" ) )
    # Now look at every method.
    for oMethod in oMethods:
        # Check the method's interface to see if
        #  these aren't the droids you're looking for.
        cMethodInterfaceName = oMethod.getDeclaringClass().getName()
        if cMethodInterfaceName == cInterfaceName:
            return True
    return False

def hasUnoInterfaces( oObject, *cInterfaces ):
    """Similar to the function of the same name in OOo Basic."""
    for cInterface in cInterfaces:
        if not hasUnoInterface( oObject, cInterface ):
            return False
    return True

#------------------------------------------------------------
#   High level general purpose functions
#------------------------------------------------------------


def makePropertyValue( cName=None, uValue=None, nHandle=None, nState=None ):
    """Create a com.sun.star.beans.PropertyValue struct and return it.
    """
    oPropertyValue = createUnoStruct( "com.sun.star.beans.PropertyValue" )

    if cName != None:
        oPropertyValue.Name = cName
    if uValue != None:
        oPropertyValue.Value = uValue
    if nHandle != None:
        oPropertyValue.Handle = nHandle
    if nState != None:
        oPropertyValue.State = nState

    return oPropertyValue


def makePoint( nX, nY ):
    """Create a com.sun.star.awt.Point struct."""
    oPoint = createUnoStruct( "com.sun.star.awt.Point" )
    oPoint.X = nX
    oPoint.Y = nY
    return oPoint


def makeSize( nWidth, nHeight ):
    """Create a com.sun.star.awt.Size struct."""
    oSize = createUnoStruct( "com.sun.star.awt.Size" )
    oSize.Width = nWidth
    oSize.Height = nHeight
    return oSize


def makeRectangle( nX, nY, nWidth, nHeight ):
    """Create a com.sun.star.awt.Rectangle struct."""
    oRect = createUnoStruct( "com.sun.star.awt.Rectangle" )
    oRect.X = nX
    oRect.Y = nY
    oRect.Width = nWidth
    oRect.Height = nHeight
    return oRect


def Array( *args ):
    """This is just sugar coating so that code from OOoBasic which
    contains the Array() function can work perfectly in python."""
    tArray = ()
    for arg in args:
        tArray += (arg,)
    return tArray


def loadComponentFromURL( cUrl, tProperties=() ):
    """Open or Create a document from it's URL.
    New documents are created from URL's such as:
        private:factory/sdraw
        private:factory/swriter
        private:factory/scalc
        private:factory/simpress
    """
    StarDesktop = getDesktop()
    oDocument = StarDesktop.loadComponentFromURL( cUrl, "_blank", 0, tProperties )
    return oDocument


#------------------------------------------------------------
#   Styles
#------------------------------------------------------------


def defineStyle( oDrawDoc, cStyleFamily, cStyleName, cParentStyleName=None ):
    """Add a new style to the style catalog if it is not already present.
    This returns the style object so that you can alter its properties.
    """

    oStyleFamily = oDrawDoc.getStyleFamilies().getByName( cStyleFamily )

    # Does the style already exist?
    if oStyleFamily.hasByName( cStyleName ):
        # then get it so we can return it.
        oStyle = oStyleFamily.getByName( cStyleName )
    else:
        # Create new style object.
        oStyle = oDrawDoc.createInstance( "com.sun.star.style.Style" )

        # Set its parent style
        if cParentStyleName != None:
            oStyle.setParentStyle( cParentStyleName )

        # Add the new style to the style family.
        oStyleFamily.insertByName( cStyleName, oStyle )

    return oStyle


def getStyle( oDrawDoc, cStyleFamily, cStyleName ):
    """Lookup and return a style from the document.
    """
    return oDrawDoc.getStyleFamilies().getByName( cStyleFamily ).getByName( cStyleName )

#------------------------------------------------------------
#   General Utility functions
#------------------------------------------------------------


def convertToURL( cPathname ):
    """Convert a Windows or Linux pathname into an OOo URL."""
    if len( cPathname ) > 1:
        if cPathname[1:2] == ":":
            cPathname = "/" + cPathname[0] + "|" + cPathname[2:]
    cPathname = string.replace( cPathname, "\\", "/" )
    cPathname = "file://" + cPathname
    return cPathname

# The global Awt Toolkit.
# This is initialized the first time it is needed.
#goAwtToolkit = createUnoService( "com.sun.star.awt.Toolkit" )
goAwtToolkit = None

def getAwtToolkit():
    global goAwtToolkit
    if goAwtToolkit == None:
        goAwtToolkit = createUnoService( "com.sun.star.awt.Toolkit" )
    return goAwtToolkit

# This class builds dialog boxes.
# This can be used in two different ways...
# 1. by subclassing it (elegant)
# 2. without subclassing it (less elegant)
class DBModalDialog:
    """Class to build a dialog box from the com.sun.star.awt.* services.
    This doesn't do anything you couldn't already do using OOo's UNO API,
     this just makes it much easier.
    You can change the dialog box size, position, title, etc.
    You can add controls, and listeners for those controls to the dialog box.
    This class can be used by subclassing it, or without subclassing it.
    """
    def __init__( self, nPositionX=None, nPositionY=None, nWidth=None, nHeight=None, cTitle=None ):
        self.oDialogModel = createUnoService( "com.sun.star.awt.UnoControlDialogModel" )
        if nPositionX != None:  self.oDialogModel.PositionX = nPositionX
        if nPositionY != None:  self.oDialogModel.PositionY = nPositionY
        if nWidth     != None:  self.oDialogModel.Width     = nWidth
        if nHeight    != None:  self.oDialogModel.Height    = nHeight
        if cTitle     != None:  self.oDialogModel.Title     = cTitle
        self.oDialogControl = createUnoService( "com.sun.star.awt.UnoControlDialog" )
        self.oDialogControl.setModel( self.oDialogModel )

    def release( self ):
        """Release resources.
        After calling this, you can no longer use this object.
        """
        self.oDialogControl.dispose()

    #--------------------------------------------------
    #   Dialog box adjustments
    #--------------------------------------------------

    def setDialogPosition( self, nX, nY ):
        self.oDialogModel.PositionX = nX
        self.oDialogModel.PositionY = nY

    def setDialogSize( self, nWidth, nHeight ):
        self.oDialogModel.Width = nWidth
        self.oDialogModel.Height = nHeight

    def setDialogTitle( self, cCaption ):
        self.oDialogModel.Title = cCaption

    def setVisible( self, bVisible ):
        self.oDialogControl.setVisible( bVisible )


    #--------------------------------------------------
    #   com.sun.star.awt.UnoControlButton
    #--------------------------------------------------

    # After you add a Button control, you can call self.setControlModelProperty()
    #  passing any of the properties for a...
    #       com.sun.star.awt.UnoControlButtonModel
    #       com.sun.star.awt.UnoControlDialogElement
    #       com.sun.star.awt.UnoControlModel
    def addButton( self, cCtrlName, nPositionX, nPositionY, nWidth, nHeight,
                       cLabel=None,
                       actionListenerProc=None,
                       nTabIndex=None ):
        self.addControl( "com.sun.star.awt.UnoControlButtonModel",
                         cCtrlName, nPositionX, nPositionY, nWidth, nHeight, bDropdown=None,
                         cLabel=cLabel,
                         nTabIndex=nTabIndex )
        if actionListenerProc != None:
            self.addActionListenerProc( cCtrlName, actionListenerProc )

    def setButtonLabel( self, cCtrlName, cLabel ):
        """Set the label of the control."""
        oControl = self.getControl( cCtrlName )
        oControl.setLabel( cLabel )

    #--------------------------------------------------
    #   com.sun.star.awt.UnoControlEditModel
    #--------------------------------------------------
    def addEdit( self, cCtrlName, nPositionX, nPositionY, nWidth, nHeight,
                        cText=None,
                        textListenerProc=None ):
        """Add a Edit control to the window."""
        self.addControl( "com.sun.star.awt.UnoControlEditModel",
            cCtrlName, nPositionX, nPositionY, nWidth, nHeight, bDropdown=None)

        if cText != None:
            self.setEditText( cCtrlName, cText )
        if textListenerProc != None:
            self.addTextListenerProc( cCtrlName, textListenerProc )

    #--------------------------------------------------
    #   com.sun.star.awt.UnoControlCheckBox
    #--------------------------------------------------

    # After you add a CheckBox control, you can call self.setControlModelProperty()
    #  passing any of the properties for a...
    #       com.sun.star.awt.UnoControlCheckBoxModel
    #       com.sun.star.awt.UnoControlDialogElement
    #       com.sun.star.awt.UnoControlModel
    def addCheckBox( self, cCtrlName, nPositionX, nPositionY, nWidth, nHeight,
                       cLabel=None,
                       itemListenerProc=None,
                       nTabIndex=None ):
        self.addControl( "com.sun.star.awt.UnoControlCheckBoxModel",
                         cCtrlName, nPositionX, nPositionY, nWidth, nHeight, bDropdown=None,
                         cLabel=cLabel,
                         nTabIndex=nTabIndex )
        if itemListenerProc != None:
            self.addItemListenerProc( cCtrlName, itemListenerProc )

    def setEditText( self, cCtrlName, cText ):
        """Set the text of the edit box."""
        oControl = self.getControl( cCtrlName )
        oControl.setText( cText )

    def getEditText( self, cCtrlName):
        """Set the text of the edit box."""
        oControl = self.getControl( cCtrlName )
        return oControl.getText()

    def setCheckBoxLabel( self, cCtrlName, cLabel ):
        """Set the label of the control."""
        oControl = self.getControl( cCtrlName )
        oControl.setLabel( cLabel )

    def getCheckBoxState( self, cCtrlName ):
        """Get the state of the control."""
        oControl = self.getControl( cCtrlName )
        return oControl.getState();

    def setCheckBoxState( self, cCtrlName, nState ):
        """Set the state of the control."""
        oControl = self.getControl( cCtrlName )
        oControl.setState( nState )

    def enableCheckBoxTriState( self, cCtrlName, bTriStateEnable ):
        """Enable or disable the tri state mode of the control."""
        oControl = self.getControl( cCtrlName )
        oControl.enableTriState( bTriStateEnable )


    #--------------------------------------------------
    #   com.sun.star.awt.UnoControlFixedText
    #--------------------------------------------------

    def addFixedText( self, cCtrlName, nPositionX, nPositionY, nWidth, nHeight,
                        cLabel=None ):
        self.addControl( "com.sun.star.awt.UnoControlFixedTextModel",
                         cCtrlName, nPositionX, nPositionY, nWidth, nHeight,
                         bDropdown=None,
                         cLabel=cLabel )

    #--------------------------------------------------
    #   Add Controls to dialog
    #--------------------------------------------------

    def addControl( self, cCtrlServiceName,
                        cCtrlName, nPositionX, nPositionY, nWidth, nHeight,
                        bDropdown=None,
                        cLabel=None,
                        nTabIndex=None,
                         ):
        oControlModel = self.oDialogModel.createInstance( cCtrlServiceName )
        self.oDialogModel.insertByName( cCtrlName, oControlModel )

        # if negative coordinates are given for X or Y position,
        #  then make that coordinate be relative to the right/bottom
        #  edge of the dialog box instead of to the left/top.
        if nPositionX < 0: nPositionX = self.oDialogModel.Width  + nPositionX - nWidth
        if nPositionY < 0: nPositionY = self.oDialogModel.Height + nPositionY - nHeight
        oControlModel.PositionX = nPositionX
        oControlModel.PositionY = nPositionY
        oControlModel.Width = nWidth
        oControlModel.Height = nHeight
        oControlModel.Name = cCtrlName

        if bDropdown != None:
            oControlModel.Dropdown = bDropdown

        if cLabel != None:
            oControlModel.Label = cLabel

        if nTabIndex != None:
            oControlModel.TabIndex = nTabIndex

    #--------------------------------------------------
    #   Access controls and control models
    #--------------------------------------------------

    #--------------------------------------------------
    #   com.sun.star.awt.UnoContorlListBoxModel
    #--------------------------------------------------


    def addComboListBox( self, cCtrlName, nPositionX, nPositionY, nWidth, nHeight,
                        bDropdown=True,
                        itemListenerProc=None,
                        actionListenerProc=None ):
        mod = self.addControl( "com.sun.star.awt.UnoControlListBoxModel",
                         cCtrlName, nPositionX, nPositionY, nWidth, nHeight,bDropdown)
        if itemListenerProc != None:
            self.addItemListenerProc( cCtrlName, itemListenerProc )

    def addListBoxItems( self, cCtrlName, tcItemTexts, nPosition=0 ):
        """Add a tupple of items to the ListBox at specified position."""
        oControl = self.getControl( cCtrlName )
        oControl.addItems( tcItemTexts, nPosition )

    def selectListBoxItem( self, cCtrlName, cItemText, bSelect=True ):
        """Selects/Deselects the ispecified item."""
        oControl = self.getControl( cCtrlName )
        return oControl.selectItem( cItemText, bSelect )

    def selectListBoxItemPos( self, cCtrlName, nItemPos, bSelect=True ):
        """Select/Deselect the item at the specified position."""
        oControl = self.getControl( cCtrlName )
        return oControl.selectItemPos( nItemPos, bSelect )

    def removeListBoxItems( self, cCtrlName, nPosition, nCount=1 ):
        """Remove items from a ListBox."""
        oControl = self.getControl( cCtrlName )
        oControl.removeItems( nPosition, nCount )

    def getListBoxItemCount( self, cCtrlName ):
        """Get the number of items in a ListBox."""
        oControl = self.getControl( cCtrlName )
        return oControl.getItemCount()

    def getListBoxSelectedItem( self, cCtrlName ):
        """Returns the currently selected item."""
        oControl = self.getControl( cCtrlName )
        return oControl.getSelectedItem()

    def getListBoxItem( self, cCtrlName, nPosition ):
        """Return the item at specified position within the ListBox."""
        oControl = self.getControl( cCtrlName )
        return oControl.getItem( nPosition )

    def getListBoxSelectedItemPos(self,cCtrlName):

        oControl = self.getControl( cCtrlName )
        return oControl.getSelectedItemPos()

    #--------------------------------------------------
    #   com.sun.star.awt.UnoControlComboBoxModel
    #--------------------------------------------------
    def addComboBox( self, cCtrlName, nPositionX, nPositionY, nWidth, nHeight,
                        bDropdown=True,
                        itemListenerProc=None,
                        actionListenerProc=None ):

        mod = self.addControl( "com.sun.star.awt.UnoControlComboBoxModel",
                         cCtrlName, nPositionX, nPositionY, nWidth, nHeight,bDropdown)

        if itemListenerProc != None:
            self.addItemListenerProc( cCtrlName, itemListenerProc )
        if actionListenerProc != None:
            self.addActionListenerProc( cCtrlName, actionListenerProc )


    def setComboBoxText( self, cCtrlName, cText ):
        """Set the text of the ComboBox."""
        oControl = self.getControl( cCtrlName )
        oControl.setText( cText )

    def getComboBoxText( self, cCtrlName):
        """Set the text of the ComboBox."""
        oControl = self.getControl( cCtrlName )
        return oControl.getText()

    def getComboBoxSelectedText( self, cCtrlName ):
        """Get the selected text of the ComboBox."""
        oControl = self.getControl( cCtrlName )
        return oControl.getSelectedText();

    def getControl( self, cCtrlName ):
        """Get the control (not its model) for a particular control name.
        The control returned includes the service com.sun.star.awt.UnoControl,
         and another control-specific service which inherits from it.
        """
        oControl = self.oDialogControl.getControl( cCtrlName )
        return oControl

    def getControlModel( self, cCtrlName ):
        """Get the control model (not the control) for a particular control name.
        The model returned includes the service UnoControlModel,
         and another control-specific service which inherits from it.
        """
        oControl = self.getControl( cCtrlName )
        oControlModel = oControl.getModel()
        return oControlModel

    #--------------------------------------------------
    #   Adjust properties of control models
    #--------------------------------------------------

    def setControlModelProperty( self, cCtrlName, cPropertyName, uValue ):
        """Set the value of a property of a control's model.
        This affects the control model, not the control.
        """
        oControlModel = self.getControlModel( cCtrlName )
        oControlModel.setPropertyValue( cPropertyName, uValue )

    def getControlModelProperty( self, cCtrlName, cPropertyName ):
        """Get the value of a property of a control's model.
        This affects the control model, not the control.
        """
        oControlModel = self.getControlModel( cCtrlName )
        return oControlModel.getPropertyValue( cPropertyName )

    #--------------------------------------------------
    #   Sugar coated property adjustments to control models.
    #--------------------------------------------------

    def setEnabled( self, cCtrlName, bEnabled=True ):
        """Supported controls...
            UnoControlButtonModel
            UnoControlCheckBoxModel
        """
        self.setControlModelProperty( cCtrlName, "Enabled", bEnabled )

    def getEnabled( self, cCtrlName ):
        """Supported controls...
            UnoControlButtonModel
            UnoControlCheckBoxModel
        """

        return self.getControlModelProperty( cCtrlName, "Enabled" )

    def setState( self, cCtrlName, nState ):
        """Supported controls...
            UnoControlButtonModel
            UnoControlCheckBoxModel
        """
        self.setControlModelProperty( cCtrlName, "State", nState )

    def getState( self, cCtrlName ):
        """Supported controls...
            UnoControlButtonModel
            UnoControlCheckBoxModel
        """
        return self.getControlModelProperty( cCtrlName, "State" )

    def setLabel( self, cCtrlName, cLabel ):
        """Supported controls...
            UnoControlButtonModel
            UnoControlCheckBoxModel
        """
        self.setControlModelProperty( cCtrlName, "Label", cLabel )

    def getLabel( self, cCtrlName ):
        """Supported controls...
            UnoControlButtonModel
            UnoControlCheckBoxModel
        """
        return self.getControlModelProperty( cCtrlName, "Label" )

    def setHelpText( self, cCtrlName, cHelpText ):
        """Supported controls...
            UnoControlButtonModel
            UnoControlCheckBoxModel
        """
        self.setControlModelProperty( cCtrlName, "HelpText", cHelpText )

    def getHelpText( self, cCtrlName ):
        """Supported controls...
            UnoControlButtonModel
            UnoControlCheckBoxModel
        """
        return self.getControlModelProperty( cCtrlName, "HelpText" )


    #--------------------------------------------------
    #   Adjust controls (not models)
    #--------------------------------------------------

    # The following apply to all controls which are a
    #   com.sun.star.awt.UnoControl

    def setDesignMode( self, cCtrlName, bDesignMode=True ):
        oControl = self.getControl( cCtrlName )
        oControl.setDesignMode( bDesignMode )

    def isDesignMode( self, cCtrlName, bDesignMode=True ):
        oControl = self.getControl( cCtrlName )
        return oControl.isDesignMode()

    def isTransparent( self, cCtrlName, bDesignMode=True ):
        oControl = self.getControl( cCtrlName )
        return oControl.isTransparent()


    # The following apply to all controls which are a
    #   com.sun.star.awt.UnoControlDialogElement

    def setPosition( self, cCtrlName, nPositionX, nPositionY ):
        self.setControlModelProperty( cCtrlName, "PositionX", nPositionX )
        self.setControlModelProperty( cCtrlName, "PositionY", nPositionY )
    def setPositionX( self, cCtrlName, nPositionX ):
        self.setControlModelProperty( cCtrlName, "PositionX", nPositionX )
    def setPositionY( self, cCtrlName, nPositionY ):
        self.setControlModelProperty( cCtrlName, "PositionY", nPositionY )
    def getPositionX( self, cCtrlName ):
        return self.getControlModelProperty( cCtrlName, "PositionX" )
    def getPositionY( self, cCtrlName ):
        return self.getControlModelProperty( cCtrlName, "PositionY" )

    def setSize( self, cCtrlName, nWidth, nHeight ):
        self.setControlModelProperty( cCtrlName, "Width", nWidth )
        self.setControlModelProperty( cCtrlName, "Height", nHeight )
    def setWidth( self, cCtrlName, nWidth ):
        self.setControlModelProperty( cCtrlName, "Width", nWidth )
    def setHeight( self, cCtrlName, nHeight ):
        self.setControlModelProperty( cCtrlName, "Height", nHeight )
    def getWidth( self, cCtrlName ):
        return self.getControlModelProperty( cCtrlName, "Width" )
    def getHeight( self, cCtrlName ):
        return self.getControlModelProperty( cCtrlName, "Height" )

    def setTabIndex( self, cCtrlName, nWidth, nTabIndex ):
        self.setControlModelProperty( cCtrlName, "TabIndex", nTabIndex )
    def getTabIndex( self, cCtrlName ):
        return self.getControlModelProperty( cCtrlName, "TabIndex" )

    def setStep( self, cCtrlName, nWidth, nStep ):
        self.setControlModelProperty( cCtrlName, "Step", nStep )
    def getStep( self, cCtrlName ):
        return self.getControlModelProperty( cCtrlName, "Step" )

    def setTag( self, cCtrlName, nWidth, cTag ):
        self.setControlModelProperty( cCtrlName, "Tag", cTag )
    def getTag( self, cCtrlName ):
        return self.getControlModelProperty( cCtrlName, "Tag" )


    #--------------------------------------------------
    #   Add listeners to controls.
    #--------------------------------------------------

    # This applies to...
    #   UnoControlButton
    def addActionListenerProc( self, cCtrlName, actionListenerProc ):
        """Create an com.sun.star.awt.XActionListener object and add it to a control.
        A listener object is created which will call the python procedure actionListenerProc.
        The actionListenerProc can be either a method or a global procedure.
        The following controls support XActionListener:
            UnoControlButton
        """
        oControl = self.getControl( cCtrlName )
        oActionListener = ActionListenerProcAdapter( actionListenerProc )
        oControl.addActionListener( oActionListener )

    # This applies to...
    #   UnoControlCheckBox
    def addItemListenerProc( self, cCtrlName, itemListenerProc ):
        """Create an com.sun.star.awt.XItemListener object and add it to a control.
        A listener object is created which will call the python procedure itemListenerProc.
        The itemListenerProc can be either a method or a global procedure.
        The following controls support XActionListener:
            UnoControlCheckBox
        """
        oControl = self.getControl( cCtrlName )
        oActionListener = ItemListenerProcAdapter( itemListenerProc )
        oControl.addItemListener( oActionListener )

    #--------------------------------------------------
    #   Display the modal dialog.
    #--------------------------------------------------

    def doModalDialog( self, sObjName,sValue):
        """Display the dialog as a modal dialog."""
        self.oDialogControl.setVisible( True )
        if not sValue==None:
            self.selectListBoxItem( sObjName, sValue, True )
        self.oDialogControl.execute()

    def endExecute( self ):
        """Call this from within one of the listeners to end the modal dialog.
        For instance, the listener on your OK or Cancel button would call this to end the dialog.
        """
        self.oDialogControl.endExecute()


import uno
import string
import unohelper
import xmlrpclib
from com.sun.star.task import XJobExecutor
if __name__<>"package":
    from lib.gui import *
    from lib.error import ErrorDialog
    from lib.functions import *
    from ServerParameter import *
    from LoginTest import *

#class RepeatIn:
class RepeatIn( unohelper.Base, XJobExecutor ):
    def __init__(self,sObject="",sVariable="",sFields="",sDisplayName="",bFromModify=False):
        # Interface Design
        LoginTest()
        if not loginstatus and __name__=="package":
            exit(1)
        self.win = DBModalDialog(60, 50, 180, 250, "RepeatIn Builder")
        self.win.addFixedText("lblVariable", 2, 12, 60, 15, "Objects to loop on :")
        self.win.addComboBox("cmbVariable", 180-120-2, 10, 120, 15,True,
                            itemListenerProc=self.cmbVariable_selected)
        self.insVariable = self.win.getControl( "cmbVariable" )

        self.win.addFixedText("lblFields", 10, 32, 60, 15, "Field to loop on :")
        self.win.addComboListBox("lstFields", 180-120-2, 30, 120, 150, False,itemListenerProc=self.lstbox_selected)
        self.insField = self.win.getControl( "lstFields" )

        self.win.addFixedText("lblName", 12, 187, 60, 15, "Variable name :")
        self.win.addEdit("txtName", 180-120-2, 185, 120, 15,)

        self.win.addFixedText("lblUName", 8, 207, 60, 15, "Displayed name :")
        self.win.addEdit("txtUName", 180-120-2, 205, 120, 15,)


        self.win.addButton('btnOK',-2 ,-10,45,15,'Ok'
                      ,actionListenerProc = self.btnOkOrCancel_clicked )

        self.win.addButton('btnCancel',-2 - 45 - 5 ,-10,45,15,'Cancel'
                      ,actionListenerProc = self.btnOkOrCancel_clicked )
        # Variable Declaration
        self.sValue=None
        self.sObj=None
        self.aSectionList=[]
        self.sGVariable=sVariable
        self.sGDisplayName=sDisplayName
        self.aItemList=[]
        self.aComponentAdd=[]
        self.aObjectList=[]
        self.aListRepeatIn=[]
        # Call method to perform Enumration on Report Document
        EnumDocument(self.aItemList,self.aComponentAdd)
        # Perform checking that Field-1 and Field - 4 is available or not alos get Combobox
        # filled if condition is true
        desktop=getDesktop()
        doc =desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        # Check weather Field-1 is available if not then exit from application
        self.sMyHost= ""
        if not docinfo.getUserFieldValue(3) == "" and not docinfo.getUserFieldValue(0)=="":
            self.sMyHost= docinfo.getUserFieldValue(0)
            self.count=0
            oParEnum = doc.getTextFields().createEnumeration()
            while oParEnum.hasMoreElements():
                oPar = oParEnum.nextElement()
                if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                    self.count += 1
            getList(self.aObjectList, self.sMyHost,self.count)
            cursor = doc.getCurrentController().getViewCursor()
            text=cursor.getText()
            tcur=text.createTextCursorByRange(cursor)

            for j in range(self.aObjectList.__len__()):
                if self.aObjectList[j].__getslice__(0,self.aObjectList[j].find(" ")) == "List":
                    self.insVariable.addItem(self.aObjectList[j],1)
            for i in range(self.aItemList.__len__()):
                if self.aComponentAdd[i]=="Document":
                    sLVal=self.aItemList[i].__getitem__(1).__getslice__(self.aItemList[i].__getitem__(1).find(",'")+2,self.aItemList[i].__getitem__(1).find("')"))
                    for j in range(self.aObjectList.__len__()):
                        if self.aObjectList[j].__getslice__(0,self.aObjectList[j].find("(")) == sLVal:
                            self.insVariable.addItem(self.aObjectList[j],1)
                if tcur.TextSection:
                    getRecersiveSection(tcur.TextSection,self.aSectionList)
                    #for k in range(self.aSectionList.__len__()):
                    if self.aComponentAdd[i] in self.aSectionList:
                        sLVal=self.aItemList[i].__getitem__(1).__getslice__(self.aItemList[i].__getitem__(1).find(",'")+2,self.aItemList[i].__getitem__(1).find("')"))
                        for j in range(self.aObjectList.__len__()):
                            if self.aObjectList[j].__getslice__(0,self.aObjectList[j].find("(")) == sLVal:
                                self.insVariable.addItem(self.aObjectList[j],1)

                if tcur.TextTable:
                    if not self.aComponentAdd[i] == "Document" and self.aComponentAdd[i].__getslice__(self.aComponentAdd[i].rfind(".")+1,self.aComponentAdd[i].__len__())== tcur.TextTable.Name:
                        VariableScope(tcur,self.insVariable,self.aObjectList,self.aComponentAdd,self.aItemList,self.aComponentAdd[i])
            self.bModify=bFromModify
            if self.bModify==True:
                if sObject=="":
                    self.insVariable.setText("List of "+docinfo.getUserFieldValue(3))
                    self.insField.addItem("objects",self.win.getListBoxItemCount("lstFields"))
                    self.win.setEditText("txtName", sVariable)
                    self.win.setEditText("txtUName",sDisplayName)
                    self.sValue= "objects"
                else:
                    sItem=""
                    i=0
                    for i in range(self.aObjectList.__len__()):
                        if self.aObjectList[i].__getslice__(0,self.aObjectList[i].find("("))==sObject:
                            sItem= self.aObjectList[i]
                            self.insVariable.setText(sItem)
                    genTree(sItem.__getslice__(sItem.find("(")+1,sItem.find(")")), self.aListRepeatIn, self.insField, self.sMyHost, 2, ending=['one2many','many2many'], recur=['one2many','many2many'])
#                    self.win.setEditText("txtName", sVariable)
#                    self.win.setEditText("txtUName",sDisplayName)
                    self.sValue= self.win.getListBoxItem("lstFields",self.aListRepeatIn.index(sFields))
            self.win.doModalDialog("lstFields",self.sValue)
        else:
            ErrorDialog("Please Select Appropriate module" ,"Create new report from: \nTiny Report->Open a New Report")
            self.win.endExecute()




#    def getSection(self,oParEnum,oCurrentSection):
#        while oParEnum.hasMoreElements():
#            oPar = oParEnum.nextElement()
#            if oPar.supportsService("com.sun.star.text.TextContent"):
#                if oPar.TextSection:
#                    if oPar.TextSection.Name==oCurrentSection.Name:
#                        oInsideEnum=oPar.createEnumeration()
#                        while oInsideEnum.hasMoreElements():
#                            oInside=oInsideEnum.nextElement()
#                            if oInside.supportsService("com.sun.star.text.TextPortion"):
#                                if oInside.TextField:
#                                    print oInside.TextField.Items
    def lstbox_selected(self,oItemEvent):
        sItem=self.win.getListBoxSelectedItem("lstFields")
        sMain=self.aListRepeatIn[self.win.getListBoxSelectedItemPos("lstFields")]
        if self.bModify==True:
            self.win.setEditText("txtName", self.sGVariable)
            self.win.setEditText("txtUName",self.sGDisplayName)
        else:
            self.win.setEditText("txtName",sMain.__getslice__(sMain.rfind("/")+1,sMain.__len__()))
            self.win.setEditText("txtUName","|-."+sItem.__getslice__(sItem.rfind("/")+1,sItem.__len__())+".-|")
    def cmbVariable_selected(self,oItemEvent):
        if self.count > 0 :
            sock = xmlrpclib.ServerProxy(self.sMyHost + '/xmlrpc/object')
            desktop=getDesktop()
            doc =desktop.getCurrentComponent()
            docinfo=doc.getDocumentInfo()
            self.win.removeListBoxItems("lstFields", 0, self.win.getListBoxItemCount("lstFields"))
            sItem=self.win.getComboBoxText("cmbVariable")
            self.aListRepeatIn=[]
            if sItem.__getslice__(sItem.rfind(" ")+1,sItem.__len__()) == docinfo.getUserFieldValue(3):
                genTree(docinfo.getUserFieldValue(3), self.aListRepeatIn, self.insField,self.sMyHost, 2, ending=['one2many','many2many'], recur=['one2many','many2many'])
            else:
                genTree(sItem.__getslice__(sItem.find("(")+1,sItem.find(")")), self.aListRepeatIn, self.insField,self.sMyHost,2,ending=['one2many','many2many'], recur=['one2many','many2many'])
            self.win.selectListBoxItemPos("lstFields", 0, True )

        else:
            sItem=self.win.getComboBoxText("cmbVariable")
            self.win.setEditText("txtName",sItem.__getslice__(sItem.rfind(".")+1,sItem.__len__()))
            self.win.setEditText("txtUName","|-."+sItem.__getslice__(sItem.rfind(".")+1,sItem.__len__())+".-|")
            self.insField.addItem("objects",self.win.getListBoxItemCount("lstFields"))
            self.win.selectListBoxItemPos("lstFields", 0, True )

    def btnOkOrCancel_clicked(self, oActionEvent):
        if oActionEvent.Source.getModel().Name == "btnOK":
            desktop=getDesktop()
            doc = desktop.getCurrentComponent()
            text = doc.Text
            cursor = doc.getCurrentController().getViewCursor()
            if self.win.getListBoxSelectedItem("lstFields") != "" and self.win.getEditText("txtName") != "" and self.win.getEditText("txtUName") != "" :
                sObjName=""
                if self.bModify==True:
                    oCurObj=cursor.TextField
                    if self.win.getListBoxSelectedItem("lstFields") == "objects":
                        sKey=u""+ self.win.getEditText("txtUName")
                        sValue=u"[[ repeatIn(" + self.win.getListBoxSelectedItem("lstFields") + ",'" + self.win.getEditText("txtName") + "') ]]"
                        oCurObj.Items = (sKey,sValue)
                        oCurObj.update()
                    else:
                        sObjName=self.win.getComboBoxText("cmbVariable")
                        sObjName=sObjName.__getslice__(0,sObjName.find("("))
                        sKey=u""+ self.win.getEditText("txtUName")
                        sValue=u"[[ repeatIn(" + sObjName + self.aListRepeatIn[self.win.getListBoxSelectedItemPos("lstFields")].replace("/",".") + ",'" + self.win.getEditText("txtName") +"') ]]"
                        oCurObj.Items = (sKey,sValue)
                        oCurObj.update()
                else:
                    oInputList = doc.createInstance("com.sun.star.text.TextField.DropDown")
                    if self.win.getListBoxSelectedItem("lstFields") == "objects":
                        sKey=u""+ self.win.getEditText("txtUName")
                        sValue=u"[[ repeatIn(" + self.win.getListBoxSelectedItem("lstFields") + ",'" + self.win.getEditText("txtName") + "') ]]"
                        oInputList.Items = (sKey,sValue)
                        text.insertTextContent(cursor,oInputList,False)
                    else:
                        sObjName=self.win.getComboBoxText("cmbVariable")
                        sObjName=sObjName.__getslice__(0,sObjName.find("("))
                        if cursor.TextTable==None:
                            sKey=u""+ self.win.getEditText("txtUName")
                            sValue=u"[[ repeatIn(" + sObjName + self.aListRepeatIn[self.win.getListBoxSelectedItemPos("lstFields")].replace("/",".") + ",'" + self.win.getEditText("txtName") +"') ]]"
                            oInputList.Items = (sKey,sValue)
                            text.insertTextContent(cursor,oInputList,False)
                        else:
                            oTable = cursor.TextTable
                            oCurCell = cursor.Cell
                            tableText = oTable.getCellByName( oCurCell.CellName )
                            sKey=u""+ self.win.getEditText("txtUName")
                            sValue=u"[[ repeatIn(" + sObjName + self.aListRepeatIn[self.win.getListBoxSelectedItemPos("lstFields")].replace("/",".") + ",'" + self.win.getEditText("txtName") +"') ]]"
                            oInputList.Items = (sKey,sValue)
                            tableText.insertTextContent(cursor,oInputList,False)
                self.win.endExecute()
            else:
                ErrorDialog("Please Fill appropriate data in Object Field or Name field \nor select perticular value from the list of fields")
        elif oActionEvent.Source.getModel().Name == "btnCancel":
            self.win.endExecute()

if __name__<>"package" and __name__=="__main__":
    RepeatIn()
elif __name__=="package":
    g_ImplementationHelper = unohelper.ImplementationHelper()
    g_ImplementationHelper.addImplementation( \
            RepeatIn,
            "org.openoffice.tiny.report.repeatln",
            ("com.sun.star.task.Job",),)

import uno
import string
import unohelper
import xmlrpclib
from com.sun.star.task import XJobExecutor
if __name__<>"package":
    from lib.gui import *
    from lib.functions import *
    from lib.error import ErrorDialog
    from LoginTest import *


class Fields(unohelper.Base, XJobExecutor ):
    def __init__(self,sVariable="",sFields="",sDisplayName="",bFromModify=False):
        LoginTest()
        if not loginstatus and __name__=="package":
            exit(1)
        self.win = DBModalDialog(60, 50, 180, 225, "Field Builder")

        self.win.addFixedText("lblVariable", 27, 12, 60, 15, "Variable :")
        self.win.addComboBox("cmbVariable", 180-120-2, 10, 120, 15,True,
                            itemListenerProc=self.cmbVariable_selected)
        self.insVariable = self.win.getControl( "cmbVariable" )

        self.win.addFixedText("lblFields", 10, 32, 60, 15, "Variable Fields :")
        self.win.addComboListBox("lstFields", 180-120-2, 30, 120, 150, False,itemListenerProc=self.lstbox_selected)
        self.insField = self.win.getControl( "lstFields" )

        self.win.addFixedText("lblUName", 8, 187, 60, 15, "Displayed name :")
        self.win.addEdit("txtUName", 180-120-2, 185, 120, 15,)

        self.win.addButton('btnOK',-5 ,-5,45,15,'Ok'
                     ,actionListenerProc = self.btnOkOrCancel_clicked )
        self.win.addButton('btnCancel',-5 - 45 - 5 ,-5,45,15,'Cancel'
                      ,actionListenerProc = self.btnOkOrCancel_clicked )
        self.sValue=None
        self.sObj=None
        self.aSectionList=[]
        self.sGDisplayName=sDisplayName
        self.aItemList=[]
        self.aComponentAdd=[]
        self.aObjectList=[]
        self.aListFields=[]
        EnumDocument(self.aItemList,self.aComponentAdd)
        desktop=getDesktop()
        doc =desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        self.sMyHost= ""
        if not docinfo.getUserFieldValue(3) == "" and not docinfo.getUserFieldValue(0)=="":
            self.sMyHost= docinfo.getUserFieldValue(0)
            self.count=0
            oParEnum = doc.getTextFields().createEnumeration()
            while oParEnum.hasMoreElements():
                oPar = oParEnum.nextElement()
                if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                    self.count += 1
            getList(self.aObjectList, self.sMyHost,self.count)
            cursor = doc.getCurrentController().getViewCursor()
            text=cursor.getText()
            tcur=text.createTextCursorByRange(cursor)
            for j in range(self.aObjectList.__len__()):
                if self.aObjectList[j].__getslice__(0,self.aObjectList[j].find("(")) == "Objects":
                    self.insVariable.addItem(self.aObjectList[j],1)
            for i in range(self.aItemList.__len__()):
                if self.aComponentAdd[i]=="Document":
                    sLVal=self.aItemList[i].__getitem__(1).__getslice__(self.aItemList[i].__getitem__(1).find(",'")+2,self.aItemList[i].__getitem__(1).find("')"))
                    for j in range(self.aObjectList.__len__()):
                        if self.aObjectList[j].__getslice__(0,self.aObjectList[j].find("(")) == sLVal:
                            self.insVariable.addItem(self.aObjectList[j],1)
                if tcur.TextSection:
                    getRecersiveSection(tcur.TextSection,self.aSectionList)
                    #for k in range(self.aSectionList.__len__()):
                    if self.aComponentAdd[i] in self.aSectionList:
                        sLVal=self.aItemList[i].__getitem__(1).__getslice__(self.aItemList[i].__getitem__(1).find(",'")+2,self.aItemList[i].__getitem__(1).find("')"))
                        for j in range(self.aObjectList.__len__()):
                            if self.aObjectList[j].__getslice__(0,self.aObjectList[j].find("(")) == sLVal:
                                self.insVariable.addItem(self.aObjectList[j],1)
                if tcur.TextTable:
                    if not self.aComponentAdd[i] == "Document" and self.aComponentAdd[i].__getslice__(self.aComponentAdd[i].rfind(".")+1,self.aComponentAdd[i].__len__())== tcur.TextTable.Name:
                        VariableScope(tcur,self.insVariable,self.aObjectList,self.aComponentAdd,self.aItemList,self.aComponentAdd[i])#self.aComponentAdd[i].__getslice__(self.aComponentAdd[i].rfind(".")+1,self.aComponentAdd[i].__len__())
            self.bModify=bFromModify
            if self.bModify==True:
                sItem=""
                i=0
                for i in range(self.aObjectList.__len__()):
                    if self.aObjectList[i].__getslice__(0,self.aObjectList[i].find("("))==sVariable:
                        sItem= self.aObjectList[i]
                        self.insVariable.setText(sItem)
                genTree(sItem.__getslice__(sItem.find("(")+1,sItem.find(")")),self.aListFields, self.insField,self.sMyHost,2,ending_excl=['one2many','many2one','many2many','reference'], recur=['many2one'])
#                self.win.setEditText("txtUName",sDisplayName)
                self.sValue= self.win.getListBoxItem("lstFields",self.aListFields.index(sFields))
            self.win.doModalDialog("lstFields",self.sValue)
        else:
            ErrorDialog("Please insert user define field Field-1 or Field-4","Just go to File->Properties->User Define \nField-1 Eg. http://localhost:8069 \nOR \nField-4 Eg. account.invoice")
            self.win.endExecute()

    def lstbox_selected(self,oItemEvent):
        try:
            sock = xmlrpclib.ServerProxy(self.sMyHost + '/xmlrpc/object')
            desktop=getDesktop()
            doc =desktop.getCurrentComponent()
            docinfo=doc.getDocumentInfo()
            #sItem=self.win.getComboBoxSelectedText("cmbVariable")
            sItem= self.win.getComboBoxText("cmbVariable")
            sMain=self.aListFields[self.win.getListBoxSelectedItemPos("lstFields")]
            sObject=self.getRes(sock,sItem.__getslice__(sItem.find("(")+1,sItem.__len__()-1),sMain.__getslice__(1,sMain.__len__()))
            res = sock.execute(database, 3, docinfo.getUserFieldValue(1), sObject , 'read',[1])
            self.win.setEditText("txtUName",res[0][(sMain.__getslice__(sMain.rfind("/")+1,sMain.__len__()))])
        except:
            #import traceback;traceback.print_exc()
            self.win.setEditText("txtUName","/")
        if self.bModify:
            self.win.setEditText("txtUName",self.sGDisplayName)
    def getRes(self,sock ,sObject,sVar):
        desktop=getDesktop()
        doc =desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        res = sock.execute(database, 3, docinfo.getUserFieldValue(1), sObject , 'fields_get')
        key = res.keys()
        key.sort()
        myval=None
        if not sVar.find("/")==-1:
            myval=sVar.__getslice__(0,sVar.find("/"))
        else:
            myval=sVar
        for k in key:
            if (res[k]['type'] in ['many2one']) and k==myval:
                self.getRes(sock,res[myval]['relation'], sVar.__getslice__(sVar.find("/")+1,sVar.__len__()))
                return res[myval]['relation']
            elif k==myval:
                return sObject
    def cmbVariable_selected(self,oItemEvent):
        if self.count > 0 :
            sock = xmlrpclib.ServerProxy(self.sMyHost + '/xmlrpc/object')
            desktop=getDesktop()
            doc =desktop.getCurrentComponent()
            docinfo=doc.getDocumentInfo()
            self.win.removeListBoxItems("lstFields", 0, self.win.getListBoxItemCount("lstFields"))
            self.aListFields=[]
            sItem=self.win.getComboBoxText("cmbVariable")
            genTree(sItem.__getslice__(sItem.find("(")+1,sItem.find(")")),self.aListFields, self.insField,self.sMyHost,2,ending_excl=['one2many','many2one','many2many','reference'], recur=['many2one'])

    def btnOkOrCancel_clicked( self, oActionEvent ):
        #Called when the OK or Cancel button is clicked.
        if oActionEvent.Source.getModel().Name == "btnOK":
            self.bOkay = True
            desktop=getDesktop()
            doc = desktop.getCurrentComponent()
            text = doc.Text
            cursor = doc.getCurrentController().getViewCursor()
            if self.win.getListBoxSelectedItem("lstFields") != "" and self.win.getEditText("txtUName") != "" and self.bModify==True :
                oCurObj=cursor.TextField
                sObjName=self.insVariable.getText()
                sObjName=sObjName.__getslice__(0,sObjName.find("("))
                sKey=u""+ self.win.getEditText("txtUName")
                sValue=u"[[ " + sObjName + self.aListFields[self.win.getListBoxSelectedItemPos("lstFields")].replace("/",".") + " ]]"
                oCurObj.Items = (sKey,sValue)
                oCurObj.update()
                self.win.endExecute()
            elif self.win.getListBoxSelectedItem("lstFields") != "" and self.win.getEditText("txtUName") != "" :
                sObjName=""
                oInputList = doc.createInstance("com.sun.star.text.TextField.DropDown")
                sObjName=self.win.getComboBoxText("cmbVariable")
                sObjName=sObjName.__getslice__(0,sObjName.find("("))
                if cursor.TextTable==None:
                    sKey=u""+ self.win.getEditText("txtUName")
                    sValue=u"[[ " + sObjName + self.aListFields[self.win.getListBoxSelectedItemPos("lstFields")].replace("/",".") + " ]]"
                    oInputList.Items = (sKey,sValue)
                    text.insertTextContent(cursor,oInputList,False)
                else:
                    oTable = cursor.TextTable
                    oCurCell = cursor.Cell
                    tableText = oTable.getCellByName( oCurCell.CellName )
                    sKey=u""+ self.win.getEditText("txtUName")
                    sValue=u"[[ " + sObjName + self.aListFields[self.win.getListBoxSelectedItemPos("lstFields")].replace("/",".") + " ]]"
                    oInputList.Items = (sKey,sValue)
                    tableText.insertTextContent(cursor,oInputList,False)
                self.win.endExecute()
            else:
                    ErrorDialog("Please Fill appropriate data in Name field \nor select perticular value from the list of fields")
        elif oActionEvent.Source.getModel().Name == "btnCancel":
            self.win.endExecute()

if __name__<>"package" and __name__=="__main__":
    Fields()
elif __name__=="package":
    g_ImplementationHelper.addImplementation( \
        Fields,
        "org.openoffice.tiny.report.fields",
        ("com.sun.star.task.Job",),)


import uno
import string
import unohelper
import xmlrpclib
from com.sun.star.task import XJobExecutor
if __name__<>"package":
    from lib.gui import *
    from lib.error import ErrorDialog
    from lib.functions import *



class Expression(unohelper.Base, XJobExecutor ):
    def __init__(self,sExpression="",sName="", bFromModify=False):
        LoginTest()
        if not loginstatus and __name__=="package":
            exit(1)
        self.win = DBModalDialog(60, 50, 180, 65, "Expression Builder")
        self.win.addFixedText("lblExpression",17 , 10, 35, 15, "Expression :")
        self.win.addEdit("txtExpression", -5, 5, 123, 15)
        self.win.addFixedText("lblName", 2, 30, 50, 15, "Displayed Name :")
        self.win.addEdit("txtName", -5, 25, 123, 15)
        self.win.addButton( "btnOK", -5, -5, 40, 15, "OK",
                        actionListenerProc = self.btnOkOrCancel_clicked )
        self.win.addButton( "btnCancel", -5 - 40 -5, -5, 40, 15, "Cancel",
                        actionListenerProc = self.btnOkOrCancel_clicked )
        self.bModify=bFromModify
        if self.bModify==True:
            self.win.setEditText("txtExpression",sExpression)
            self.win.setEditText("txtName",sName)
        self.win.doModalDialog("",None)

    def getDesktop(self):
        localContext = uno.getComponentContext()
        resolver = localContext.ServiceManager.createInstanceWithContext(
                        "com.sun.star.bridge.UnoUrlResolver", localContext )
        smgr = resolver.resolve( "uno:socket,host=localhost,port=2002;urp;StarOffice.ServiceManager" )
        remoteContext = smgr.getPropertyValue( "DefaultContext" )
        desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",remoteContext)
        return desktop

    def btnOkOrCancel_clicked( self, oActionEvent ):
        #Called when the OK or Cancel button is clicked.
        if oActionEvent.Source.getModel().Name == "btnOK":
            desktop=self.getDesktop()
            doc = desktop.getCurrentComponent()
            text = doc.Text
            cursor = doc.getCurrentController().getViewCursor()
            if self.bModify==True:
                oCurObj=cursor.TextField
                sKey=u""+self.win.getEditText("txtName")
                sValue=u"[[ " + self.win.getEditText("txtExpression") + " ]]"
                oCurObj.Items = (sKey,sValue)
                oCurObj.update()
                self.win.endExecute()
            else:
                oInputList = doc.createInstance("com.sun.star.text.TextField.DropDown")
                if self.win.getEditText("txtName")!="" and self.win.getEditText("txtExpression")!="":
                    sKey=u""+self.win.getEditText("txtName")
                    sValue=u"[[ " + self.win.getEditText("txtExpression") + " ]]"
                    if cursor.TextTable==None:
                        oInputList.Items = (sKey,sValue)
                        text.insertTextContent(cursor,oInputList,False)
                    else:
                        oTable = cursor.TextTable
                        oCurCell = cursor.Cell
                        tableText = oTable.getCellByName( oCurCell.CellName )
                        oInputList.Items = (sKey,sValue)
                        tableText.insertTextContent(cursor,oInputList,False)
                    self.win.endExecute()
                else:
                    ErrorDialog("Please Fill appropriate data in Name field or \nExpression field")
        elif oActionEvent.Source.getModel().Name == "btnCancel":
            self.win.endExecute()

if __name__<>"package" and __name__=="__main__":
    Expression()
elif __name__=="package":
    g_ImplementationHelper.addImplementation( \
        Expression,
        "org.openoffice.tiny.report.expression",
        ("com.sun.star.task.Job",),)

import re
import uno
import string
import unohelper
import xmlrpclib
from com.sun.star.task import XJobExecutor
if __name__<>"package":
    from lib.gui import *
    from Expression import Expression
    from Fields import Fields
    from Repeatln import RepeatIn
    from lib.error import *


class modify(unohelper.Base, XJobExecutor ):

    def __init__( self, ctx ):
        self.ctx     = ctx
        self.module  = "tiny_report"
        self.version = "0.1"
        self.win=None
        localContext = uno.getComponentContext()
        resolver = localContext.ServiceManager.createInstanceWithContext(
                        "com.sun.star.bridge.UnoUrlResolver", localContext )
        smgr = resolver.resolve( "uno:socket,host=localhost,port=2002;urp;StarOffice.ServiceManager" )
        remoteContext = smgr.getPropertyValue( "DefaultContext" )
        desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",remoteContext)
        Doc =desktop.getCurrentComponent()
        self.oVC = Doc.CurrentController.getViewCursor()
        # Variable Declaration
        self.sObj=None
        self.count=0
        self.aItemList=[]
        self.aComponentAdd=[]
        self.aObjectList=[]
        desktop=getDesktop()
        doc =desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        self.oMyObject=None
        if not docinfo.getUserFieldValue(0)=="":
            self.sMyHost= docinfo.getUserFieldValue(0)
        else:
            ErrorDialog("Please insert user define field Field-1","Just go to File->Properties->User Define \nField-1 Eg. http://localhost:8069")
            exit(1)
        # Check weather Field-4 is available or not otherwise exit from application
        if not docinfo.getUserFieldValue(3) == "" and not docinfo.getUserFieldValue(0)=="":
            if self.oVC.TextField:
                self.oCurObj=self.oVC.TextField
                self.oMyObject= self.getOperation(self.oVC.TextField.Items.__getitem__(1))
                if self.oMyObject.__getitem__(0) == "field":
                    Fields(self.oMyObject.__getitem__(1).__getslice__(0,self.oMyObject.__getitem__(1).find(".")),self.oMyObject.__getitem__(1).__getslice__(self.oMyObject.__getitem__(1).find("."),self.oMyObject.__getitem__(1).__len__()).replace(".","/"),self.oCurObj.Items[0],True)
                elif self.oMyObject.__getitem__(0) == "expression":
                    Expression(self.oMyObject.__getitem__(1),self.oCurObj.Items.__getitem__(0),True)
                elif self.oMyObject.__getitem__(0)=="repeatIn":
                    #RepeatIn(self,sObject="",sVariable="",sFields="",sDisplayName="",bFromModify=False):
                    RepeatIn(self.oMyObject.__getitem__(1).__getslice__(0,self.oMyObject.__getitem__(1).find(".")),self.oMyObject[2],self.oMyObject.__getitem__(1).__getslice__(self.oMyObject.__getitem__(1).find("."),self.oMyObject.__getitem__(1).__len__()).replace(".","/"),self.oCurObj.Items[0],True)
            else:
                ErrorDialog("Please place your cursor at begaining of field \nwhich you want to modify","")

        else:
            ErrorDialog("Please insert user define field Field-1 or Field-4","Just go to File->Properties->User Define \nField-1 Eg. http://localhost:8069 \nOR \nField-4 Eg. account.invoice")
            exit(1)

    def getOperation(self, str):
        #str = "[[ RepeatIn(objects, 'variable') ]]" #repeatIn
        #str = "[[ saleorder.partner_id.name ]]" # field
        #str = "[[ some thing complex ]]" # expression
        method1 = lambda x: (u'repeatIn', x.group(1), x.group(2))
        method2 = lambda x: (u'field', x.group(1))
        method3 = lambda x: (u'expression', x.group(1))
        regexes = [
                ('\\[\\[ *repeatIn\\( *(.+)*, *\'([a-zA-Z0-9_]+)\' *\\) *\\]\\]', method1),
                ('\\[\\[ *([a-zA-Z0-9_\.]+) *\\]\\]', method2),
                ('\\[\\[ *(.+) *\\]\\]', method3)
        ]
        for (rule,method) in regexes:
                res= re.match(rule, str)
                if res:
                        return method(res)
                        break

if __name__<>"package":
    modify(None)
else:
    g_ImplementationHelper.addImplementation( \
        modify,
        "org.openoffice.tiny.report.modify",
        ("com.sun.star.task.Job",),)

import uno
import string
import unohelper
import xmlrpclib
from com.sun.star.task import XJobExecutor
if __name__<>"package":
    from lib.gui import *
    from lib.error import ErrorDialog
    from lib.functions import *
    from Change import *

class ServerParameter( unohelper.Base, XJobExecutor ):
    def __init__(self,ctx):
        self.ctx     = ctx
        self.module  = "tiny_report"
        self.version = "0.1"
        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        self.win=DBModalDialog(60, 50, 160, 108, "Server Connection Parameter")

        self.win.addFixedText("lblVariable", 2, 12, 60, 15, "Server URL")
        if docinfo.getUserFieldValue(0)<>"":
            res=getConnectionStatus(docinfo.getUserFieldValue(0))
            if res == -1:
                ErrorDialog("Could not connect to the server!","")
            elif res == 0:
                ErrorDialog("No Database found !!!","")

        self.win.addEdit("txtHost",-34,9,91,15,docinfo.getUserFieldValue(0))
        self.win.addButton('btnChange',-2 ,9,30,15,'Change'
                      ,actionListenerProc = self.btnChange_clicked )

        self.win.addFixedText("lblDatabaseName", 6, 31, 60, 15, "Database")
        #self.win.addFixedText("lblMsg", -2,28,123,15)
        self.win.addComboListBox("lstDatabase", -2,28,123,15, True)
        self.lstDatabase = self.win.getControl( "lstDatabase" )
        if docinfo.getUserFieldValue(0)<>"":
            self.win.removeListBoxItems("lstDatabase", 0, self.win.getListBoxItemCount("lstDatabase"))
            for i in range(res.__len__()):
                self.lstDatabase.addItem(res[i],i)
        #self.win.selectListBoxItem( "lstDatabase", docinfo.getUserFieldValue(2), True )
        #self.win.setEnabled("lblMsg",False)

        self.win.addFixedText("lblLoginName", 17, 51, 60, 15, "Login")
        self.win.addEdit("txtLoginName",-2,48,123,15,docinfo.getUserFieldValue(1))

        self.win.addFixedText("lblPassword", 6, 70, 60, 15, "Password")
        self.win.addEdit("txtPassword",-2,67,123,15)

        self.win.addButton('btnOK',-2 ,-5, 60,15,'Test Connection'
                      ,actionListenerProc = self.btnOkOrCancel_clicked )

        self.win.addButton('btnCancel',-2 - 60 - 5 ,-5, 35,15,'Cancel'
                      ,actionListenerProc = self.btnOkOrCancel_clicked )

        self.win.doModalDialog("",None)
        #self.win.doModalDialog("lstDatabase",docinfo.getUserFieldValue(2))

    def btnOkOrCancel_clicked(self,oActionEvent):
        if oActionEvent.Source.getModel().Name == "btnOK":
            sock = xmlrpclib.ServerProxy(self.win.getEditText("txtHost")+'/xmlrpc/common')
            sDatabase=self.win.getListBoxSelectedItem("lstDatabase")
            sLogin=self.win.getEditText("txtLoginName")
            sPassword=self.win.getEditText("txtPassword")
            UID = sock.login(sDatabase,sLogin,sPassword)
            if not UID:
                ErrorDialog("Connection Refuse...","Please enter valid Login/Password")
            else:
                desktop=getDesktop()
                doc = desktop.getCurrentComponent()
                docinfo=doc.getDocumentInfo()
                docinfo.setUserFieldValue(0,self.win.getEditText("txtHost"))
                docinfo.setUserFieldValue(1,self.win.getEditText("txtLoginName"))
                global passwd
                passwd=self.win.getEditText("txtPassword")
                global loginstatus
                loginstatus=True
                global database
                database=sDatabase
                #docinfo.setUserFieldValue(2,self.win.getListBoxSelectedItem("lstDatabase"))
                #docinfo.setUserFieldValue(3,"")
                self.win.endExecute()
        elif oActionEvent.Source.getModel().Name == "btnCancel":
            self.win.endExecute()

    def btnChange_clicked(self,oActionEvent):
        aVal=[]
        url= self.win.getEditText("txtHost")
        print url
        Change(aVal,url)
        if aVal[1]== -1:
            ErrorDialog(aVal[0],"")
        elif aVal[1]==0:
            ErrorDialog(aVal[0],"")
        else:
            self.win.setEditText("txtHost",aVal[0])
            self.win.removeListBoxItems("lstDatabase", 0, self.win.getListBoxItemCount("lstDatabase"))
            for i in range(aVal[1].__len__()):
                self.lstDatabase.addItem(aVal[1][i],i)


if __name__<>"package" and __name__=="__main__":
    ServerParameter(None)
elif __name__=="package":
    g_ImplementationHelper.addImplementation( \
            ServerParameter,
            "org.openoffice.tiny.report.serverparam",
            ("com.sun.star.task.Job",),)

if __name__<>"package":
    from lib.gui import *
    from lib.functions import *

class Change:
    def __init__(self, aVal= None, sURL=""):
        self.win=DBModalDialog(60, 50, 120, 90, "Connect to Tiny ERP Server")

        self.win.addFixedText("lblVariable", 38, 12, 60, 15, "Server")

        if sURL<>"":
            print sURL.__getslice__(sURL.rfind(":")+1,sURL.__len__())
        self.win.addEdit("txtHost",-2,9,60,15,sURL.__getslice__(sURL.find("/")+2,sURL.rfind(":")))

        self.win.addFixedText("lblReportName",45 , 31, 60, 15, "Port")
        self.win.addEdit("txtPort",-2,28,60,15,sURL.__getslice__(sURL.rfind(":")+1,sURL.__len__()))

        self.win.addFixedText("lblLoginName", 2, 51, 60, 15, "Protocol Connection")

        self.win.addComboListBox("lstProtocol", -2, 48, 60, 15, True)
        self.lstProtocol = self.win.getControl( "lstProtocol" )

        self.lstProtocol.addItem( "XML-RPC", 0)
        self.lstProtocol.addItem( "XML-RPC secure", 1)
        self.lstProtocol.addItem( "NET-RPC (faster)", 2)

        self.win.addButton( 'btnOK', -2, -5, 30, 15, 'Ok'
                      , actionListenerProc = self.btnOkOrCancel_clicked )

        self.win.addButton( 'btnCancel', -2 - 30 - 5 ,-5, 30, 15, 'Cancel'
                      , actionListenerProc = self.btnOkOrCancel_clicked )
        self.aVal=aVal
        self.protocol={'XML-RPC': 'http://',
            'XML-RPC secure': 'https://',
            'NET-RPC (faster)': 'socket://',}
        sValue=""
        if sURL<>"":
            sValue=self.protocol.keys()[self.protocol.values().index(sURL.__getslice__(0,sURL.find("/")+2))]

        self.win.doModalDialog( "lstProtocol", sValue)

    def cmbProtocol_selected(self,oItemEvent):
        pass
    def btnOkOrCancel_clicked(self,oActionEvent):
        if oActionEvent.Source.getModel().Name == "btnOK":
            url = self.protocol[self.win.getListBoxSelectedItem("lstProtocol")]+self.win.getEditText("txtHost")+":"+self.win.getEditText("txtPort")
            res = getConnectionStatus(url)
            if res == -1:
                self.aVal.append("Could not connect to the server!")
                self.aVal.append(res)
            elif res == 0:
                self.aVal.append("No Database found !!!")
                self.aVal.append(res)
            else:
                self.aVal.append(url)
                self.aVal.append(res)
            #return self.aVal
            self.win.endExecute()
        elif oActionEvent.Source.getModel().Name =="btnCancel":
            self.win.endExecute()


import uno
import string
import unohelper
import xmlrpclib
from com.sun.star.task import XJobExecutor
if __name__<>"package":
    from lib.gui import *
    from lib.error import ErrorDialog
    from lib.functions import *
    from LoginTest import *

#
# Start OpenOffice.org, listen for connections and open testing document
#

class NewReport(unohelper.Base, XJobExecutor):
    def __init__(self,ctx):
        self.ctx     = ctx
        self.module  = "tiny_report"
        self.version = "0.1"
        LoginTest()
        if not loginstatus and __name__=="package":
            exit(1)
        self.win=DBModalDialog(60, 50, 180, 135, "Open New Report")
        self.win.addFixedText("lblModuleSelection", 2, 12, 60, 15, "Module Selection")
        self.win.addComboListBox("lstModule", -2,9,123,80 , False)
        self.lstModule = self.win.getControl( "lstModule" )
        self.win.addFixedText("lblReportName", 2, 12, 60, 15, "Report Name")
        self.aModuleName=[]
        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        print docinfo.getUserFieldValue(0)
        sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')

        ids = sock.execute(docinfo.getUserFieldValue(2), 3, docinfo.getUserFieldValue(1), 'ir.model' , 'search',[])
        fields = [ 'model','name']
        res = sock.execute(docinfo.getUserFieldValue(2), 3, docinfo.getUserFieldValue(1), 'ir.model' , 'read', ids, fields)
        for i in range(res.__len__()):
            self.lstModule.addItem(res[i]['name'],self.lstModule.getItemCount())
            self.aModuleName.append(res[i]['model'])
        self.win.addButton('btnOK',-2 ,-5, 70,15,'Use Module in Report'
                      ,actionListenerProc = self.btnOkOrCancel_clicked )
        self.win.addButton('btnCancel',-2 - 70 - 5 ,-5, 35,15,'Cancel'
                      ,actionListenerProc = self.btnOkOrCancel_clicked )
        self.win.doModalDialog("",None)

    def btnOkOrCancel_clicked(self,oActionEvent):
        if oActionEvent.Source.getModel().Name=="btnOK":
            desktop=getDesktop()
            doc = desktop.getCurrentComponent()
            docinfo=doc.getDocumentInfo()
            print self.lstModule.getSelectedItemPos()
            docinfo.setUserFieldValue(3,self.aModuleName[self.lstModule.getSelectedItemPos()])
            self.win.endExecute()
        elif oActionEvent.Source.getModel().Name=="btnCancel":
            self.win.endExecute()

if __name__<>"package" and __name__=="__main__":
    NewReport(None)
elif __name__=="package":
    g_ImplementationHelper.addImplementation( \
            NewReport,
            "org.openoffice.tiny.report.opennewreport",
            ("com.sun.star.task.Job",),)



if __name__<>"package":
    from ServerParameter import *
    from lib.gui import *

class LoginTest:
    def __init__(self):
        if not loginstatus:
            ServerParameter(None)



import uno
import string
import unohelper
import xmlrpclib
import base64, tempfile

from com.sun.star.task import XJobExecutor
import os
import sys
if __name__<>'package':
    from lib.gui import *
    from lib.error import *
    from LoginTest import *

class ModifyExistingReport(unohelper.Base, XJobExecutor):
    def __init__(self,ctx):
        self.ctx     = ctx
        self.module  = "tiny_report"
        self.version = "0.1"
        LoginTest()
        if not loginstatus and __name__=="package":
            exit(1)
        self.win=DBModalDialog(60, 50, 180, 135, "Modify Existing Report")
        self.win.addFixedText("lblReport", 2, 3, 60, 15, "Report Selection")
        self.win.addComboListBox("lstReport", -1,15,178,80 , False,itemListenerProc=self.lstbox_selected)
        self.lstReport = self.win.getControl( "lstReport" )
        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
        self.ids = sock.execute(database, 3, docinfo.getUserFieldValue(1), 'ir.actions.report.xml' ,  'search', [('report_sxw_content','<>',False)])
        #res_sxw = sock.execute(docinfo.getUserFieldValue(2), 3, docinfo.getUserFieldValue(1), 'ir.actions.report.xml', 'report_get', ids[0])
        fields=['name','report_name','model']
        self.res_other = sock.execute(database, 3, docinfo.getUserFieldValue(1), 'ir.actions.report.xml', 'read', self.ids,fields)
        for i in range(self.res_other.__len__()):
            if self.res_other[i]['name']<>"":
                self.lstReport.addItem(self.res_other[i]['name'],self.lstReport.getItemCount())

        self.win.addFixedText("lblModuleSelection1", 2, 98, 178, 15, "Module Selection")
        self.win.addButton('btnSave',-2 ,-5,80,15,'Save to Temp Directory'
                      ,actionListenerProc = self.btnOkOrCancel_clicked )
        self.win.addButton('btnCancel',-2 -80 ,-5,45,15,'Cancel'
                      ,actionListenerProc = self.btnOkOrCancel_clicked )
        #os.system( "oowriter /home/hjo/Desktop/aaa.sxw &" )
        self.win.doModalDialog("lstReport",self.res_other[0]['name'])

    def lstbox_selected(self,oItemEvent):
        #print self.win.getListBoxSelectedItemPos("lstReport")
        self.win.setEditText("lblModuleSelection1",tempfile.mktemp('.'+"sxw"))
    def btnOkOrCancel_clicked(self, oActionEvent):
        if oActionEvent.Source.getModel().Name == "btnSave":
            desktop=getDesktop()
            doc = desktop.getCurrentComponent()
            docinfo=doc.getDocumentInfo()
            sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
            res = sock.execute(database, 3, docinfo.getUserFieldValue(1), 'ir.actions.report.xml', 'report_get', self.ids[self.win.getListBoxSelectedItemPos("lstReport")])
            if res['report_sxw_content']:
                data = base64.decodestring(res['report_sxw_content'])
                fp_name = self.win.getEditText("lblModuleSelection1")
                fp = file(fp_name, 'wb')
                fp.write(data)
                fp.close()
            url="file://"+self.win.getEditText("lblModuleSelection1")
            arr=Array()
            oDoc2 = desktop.loadComponentFromURL(url, "tiny", 55, arr)
            oVC= oDoc2.getCurrentController().getViewCursor()
            oText = oVC.getText()
            oCur=oText.createTextCursorByRange(oVC.getStart())
            oCur.insertDocumentFromURL(url, Array())
            docinfo2=oDoc2.getDocumentInfo()
            docinfo2.setUserFieldValue(2,self.ids[self.win.getListBoxSelectedItemPos("lstReport")])
            docinfo2.setUserFieldValue(1,docinfo.getUserFieldValue(1))
            docinfo2.setUserFieldValue(0,docinfo.getUserFieldValue(0))
            docinfo2.setUserFieldValue(3,self.res_other[self.win.getListBoxSelectedItemPos("lstReport")]['model'])
            if oDoc2.isModified():
                if oDoc2.hasLocation() and not oDoc2.isReadonly():
                    oDoc2.store()
                #End If
            #End If
            #os.system( "`which ooffice` '-accept=socket,host=localhost,port=2002;urp;'")
            ErrorDialog("Download is Completed","Your file has been placed here :\n"+ self.win.getEditText("lblModuleSelection1"),"Download Message")
            self.win.endExecute()
        elif oActionEvent.Source.getModel().Name == "btnCancel":
            self.win.endExecute()

if __name__<>"package" and __name__=="__main__":
    ModifyExistingReport(None)
elif __name__=="package":
    g_ImplementationHelper.addImplementation( \
            ModifyExistingReport,
            "org.openoffice.tiny.report.modifyreport",
            ("com.sun.star.task.Job",),)



import uno
import string
import unohelper
import xmlrpclib
import base64, tempfile
from com.sun.star.task import XJobExecutor
import os
import sys
if __name__<>'package':
    from lib.gui import *
    from lib.error import *
    from LoginTest import *
    from lib.functions import *

class SendtoServer(unohelper.Base, XJobExecutor):
    def __init__(self,ctx):
        self.ctx     = ctx
        self.module  = "tiny_report"
        self.version = "0.1"
        LoginTest()
        if not loginstatus and __name__=="package":
            exit(1)
#        else:
#            self.database="trunk_1"
        desktop=getDesktop()
        oDoc2 = desktop.getCurrentComponent()
        docinfo=oDoc2.getDocumentInfo()
        sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
        fields=['name','report_name','model']
        res_other = sock.execute(database, 3, docinfo.getUserFieldValue(1), 'ir.actions.report.xml', 'read',[docinfo.getUserFieldValue(2)] ,fields)
        print res_other
        self.win = DBModalDialog(60, 50, 180, 65, "Send To Server")
        self.win.addFixedText("lblExpression",10 , 9, 40, 15, "Report Name :")
        self.win.addEdit("txtExpression", -5, 5, 123, 15,res_other[0]['name'])
        self.win.addFixedText("lblName", 2, 30, 50, 15, "Technical Name :")
        self.win.addEdit("txtName", -5, 25, 123, 15,res_other[0]['report_name'])
        self.win.addButton( "btnSend", -5, -5, 80, 15, "Send Report to Server",
                        actionListenerProc = self.btnOkOrCancel_clicked )
        self.win.addButton( "btnCancel", -5 - 80 -5, -5, 40, 15, "Cancel",
                        actionListenerProc = self.btnOkOrCancel_clicked )
        self.win.doModalDialog("",None)
    def btnOkOrCancel_clicked(self, oActionEvent):
        if oActionEvent.Source.getModel().Name == "btnSend":
            desktop=getDesktop()
            oDoc2 = desktop.getCurrentComponent()
            docinfo=oDoc2.getDocumentInfo()
            print "abc",oDoc2.isModified(),oDoc2.hasLocation()
            if oDoc2.isModified() and not oDoc2.hasLocation():
                ErrorDialog("Please Save your file in filesystem !!!","File->Save OR File->Save As")
            elif oDoc2.isModified() and oDoc2.hasLocation():
                oDoc2.store()
                url=oDoc2.getURL().__getslice__(7,oDoc2.getURL().__len__())
                fp = file(url, 'rb')#"Love has the power to break all chains - Swim the deepest seas - Endure the strongest pains - Love is the glow in the darkest night leading you on until you have sight."
                data=fp.read()
                fp.close()
                sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
                res = sock.execute(database, 3, docinfo.getUserFieldValue(1), 'ir.actions.report.xml', 'upload_report', int(docinfo.getUserFieldValue(2)),base64.encodestring(data),{})
                self.win.endExecute()
        elif oActionEvent.Source.getModel().Name == "btnCancel":
            self.win.endExecute()
if __name__<>"package" and __name__=="__main__":
    SendtoServer(None)
elif __name__=="package":
    g_ImplementationHelper.addImplementation( \
            SendtoServer,
            "org.openoffice.tiny.report.sendtoserver",
            ("com.sun.star.task.Job",),)


