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
if __name__<>"package":
    os.system( "ooffice '-accept=socket,host=localhost,port=2002;urp;'" )
passwd=""
database=""
uid=""
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
    database="test"
    uid = 3

def genTree(object,aList,insField,host,level=3, ending=[], ending_excl=[], recur=[], root='', actualroot=""):
    try:
        sock = xmlrpclib.ServerProxy(host+'/xmlrpc/object')
        global passwd
        res = sock.execute(database, uid, passwd, object , 'fields_get')
        key = res.keys()
        key.sort()
        for k in key:
            if (not ending or res[k]['type'] in ending) and ((not ending_excl) or not (res[k]['type'] in ending_excl)):
                insField.addItem(root+'/'+res[k]["string"],len(aList))
                aList.append(actualroot+'/'+k)
            if (res[k]['type'] in recur) and (level>0):
                genTree(res[k]['relation'],aList,insField,host ,level-1, ending, ending_excl, recur,root+'/'+res[k]["string"],actualroot+'/'+k)
    except:
        import traceback;traceback.print_exc()

def VariableScope(oTcur,insVariable,aObjectList,aComponentAdd,aItemList,sTableName=""):
    if sTableName.find(".") != -1:
	for i in range(len(aItemList)):
            if aComponentAdd[i]==sTableName:
		sLVal=aItemList[i][1][aItemList[i][1].find(",'")+2:aItemList[i][1].find("')")]
                for j in range(len(aObjectList)):
		    if aObjectList[j][:aObjectList[j].find("(")] == sLVal:
                        insVariable.append(aObjectList[j])
	VariableScope(oTcur,insVariable,aObjectList,aComponentAdd,aItemList, sTableName[:sTableName.rfind(".")])
    else:
	for i in range(len(aItemList)):
            if aComponentAdd[i]==sTableName:
		sLVal=aItemList[i][1][aItemList[i][1].find(",'")+2:aItemList[i][1].find("')")]
                for j in range(len(aObjectList)):
		    if aObjectList[j][:aObjectList[j].find("(")] == sLVal and sLVal!="":
                        insVariable.append(aObjectList[j])

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
                    sItem=oPar.Items[1]
		    if sItem[sItem.find("(")+1:sItem.find(",")]=="objects":
			sMain = sItem[sItem.find(",'")+2:sItem.find("')")]
            oParEnum = doc.getTextFields().createEnumeration()
            aObjectList.append("List of " + docinfo.getUserFieldValue(3))
            while oParEnum.hasMoreElements():
                oPar = oParEnum.nextElement()
                if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                    sItem=oPar.Items[1]
		    if sItem[sItem.find("[[ ")+3:sItem.find("(")]=="repeatIn":
			if sItem[sItem.find("(")+1:sItem.find(",")]=="objects":
			    aObjectList.append(sItem[sItem.rfind(",'")+2:sItem.rfind("')")] + "(" + docinfo.getUserFieldValue(3) + ")")
                        else:
			    sTemp=sItem[sItem.find("(")+1:sItem.find(",")]
			    if sMain == sTemp[:sTemp.find(".")]:
				getRelation(docinfo.getUserFieldValue(3), sItem[sItem.find(".")+1:sItem.find(",")], sItem[sItem.find(",'")+2:sItem.find("')")],aObjectList,host)
                            else:
				sPath=getPath(sItem[sItem.find("(")+1:sItem.find(",")], sMain)
				getRelation(docinfo.getUserFieldValue(3), sPath[sPath.find(".")+1:], sItem[sItem.find(",'")+2:sItem.find("')")],aObjectList,host)
    else:
        aObjectList.append("List of " + docinfo.getUserFieldValue(3))

def getRelation(sRelName, sItem, sObjName, aObjectList, host ):
        sock = xmlrpclib.ServerProxy(host+'/xmlrpc/object')
        global passwd
        res = sock.execute(database, uid, passwd, sRelName , 'fields_get')
        key = res.keys()
        for k in key:
            if sItem.find(".") == -1:
                if k == sItem:
                    aObjectList.append(sObjName + "(" + res[k]['relation'] + ")")
                    return 0
	    if k == sItem[:sItem.find(".")]:
		getRelation(res[k]['relation'], sItem[sItem.find(".")+1:], sObjName,aObjectList,host)


def getPath(sPath,sMain):
    desktop=getDesktop()
    doc =desktop.getCurrentComponent()
    oParEnum = doc.getTextFields().createEnumeration()
    while oParEnum.hasMoreElements():
        oPar = oParEnum.nextElement()
        if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
            sItem=oPar.Items[1]
	    if sPath[:sPath.find(".")] == sMain:
                break;
            else:
                res = re.findall('\\[\\[ *([a-zA-Z0-9_\.]+) *\\]\\]',sPath)
                if len(res) <> 0:
		    if sItem[sItem.find(",'")+2:sItem.find("')")] == sPath[:sPath.find(".")]:
			sPath =  sItem[sItem.find("(")+1:sItem.find(",")] + sPath[sPath.find("."):]
                        getPath(sPath, sMain)
    return sPath

def EnumDocument(aItemList,aComponentAdd):
    desktop = getDesktop()
    parent=""
    bFlag = False
    Doc =desktop.getCurrentComponent()
    #oVC = Doc.CurrentController.getViewCursor()
    oParEnum = Doc.getTextFields().createEnumeration()
    while oParEnum.hasMoreElements():
        oPar = oParEnum.nextElement()
        if oPar.Anchor.TextTable:
            #parent = oPar.Anchor.TextTable.Name
            getChildTable(oPar.Anchor.TextTable,aItemList,aComponentAdd)
        elif oPar.Anchor.TextSection:
            parent = oPar.Anchor.TextSection.Name
        elif oPar.Anchor.Text:
            parent = "Document"
        sItem=oPar.Items[1]
	if sItem[sItem.find("[[ ")+3:sItem.find("(")]=="repeatIn" and not oPar.Items in aItemList:
	    aItemList.append( oPar.Items )
	    aComponentAdd.append( parent )

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
                            sItem=oSubSection.TextField.Items[1]
			    if sItem[sItem.find("[[ ")+3:sItem.find("(")]=="repeatIn":
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
    oFileDialog.appendFilter("OpenERP Report File","*.sxw")
    oFileDialog.setCurrentFilter("OpenERP Report File")
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
import pythonloader
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
pythonloader.DEBUG = 0
def getServiceManager( cHost="localhost", cPort="2002" ):
    """Get the ServiceManager from the running OpenOffice.org.
        Then retain it in the global variable goServiceManager for future use.
        This is similar to the GetProcessServiceManager() in OOo Basic.
    """
    global goServiceManager
    global pythonloader
    if not goServiceManager:
        # Get the uno component context from the PyUNO runtime
        oLocalContext = uno.getComponentContext()
        # Create the UnoUrlResolver on the Python side.

        # Connect to the running OpenOffice.org and get its context.
        if __name__<>"package":
            oLocalResolver = oLocalContext.ServiceManager.createInstanceWithContext(
                                    "com.sun.star.bridge.UnoUrlResolver", oLocalContext )
            oContext = oLocalResolver.resolve( "uno:socket,host=" + cHost + ",port=" + cPort + ";urp;StarOffice.ComponentContext" )
        # Get the ServiceManager object
            goServiceManager = oContext.ServiceManager
        else:
            goServiceManager=oLocalContext.ServiceManager

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
#getDesktop()


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
    cPathname = cPathname.replace( "\\", "/" )
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
                         cCtrlName, nPositionX, nPositionY, nWidth, nHeight, bDropdown=None, bMultiSelection=None,
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
                         cCtrlName, nPositionX, nPositionY, nWidth, nHeight, bDropdown=None,  bMultiSelection=None,
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
                         bDropdown=None, bMultiSelection=None,
                         cLabel=cLabel )

        return self.getControl( cCtrlName )

    #--------------------------------------------------
    #   Add Controls to dialog
    #--------------------------------------------------

    def addControl( self, cCtrlServiceName,
                        cCtrlName, nPositionX, nPositionY, nWidth, nHeight,
                        bDropdown=None,
                        bMultiSelection=None,
                        cLabel=None,
                        nTabIndex=None,
                        sImagePath=None,
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

        if bMultiSelection!=None:
            oControlModel.MultiSelection=bMultiSelection

        if cLabel != None:
            oControlModel.Label = cLabel

        if nTabIndex != None:
            oControlModel.TabIndex = nTabIndex

        if sImagePath != None:
            oControlModel.ImageURL = sImagePath
    #--------------------------------------------------
    #   Access controls and control models
    #--------------------------------------------------

    #--------------------------------------------------
    #   com.sun.star.awt.UnoContorlListBoxModel
    #--------------------------------------------------


    def addComboListBox( self, cCtrlName, nPositionX, nPositionY, nWidth, nHeight,
                        bDropdown=True,
                        bMultiSelection=False,
                        itemListenerProc=None,
                        actionListenerProc=None,
                        ):

        mod = self.addControl( "com.sun.star.awt.UnoControlListBoxModel",
                         cCtrlName, nPositionX, nPositionY, nWidth, nHeight,bDropdown,bMultiSelection )

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

    def getListBoxSelectedItems(self,cCtrlName):
        oControl = self.getControl( cCtrlName )
        return oControl.getSelectedItems()

    def getListBoxSelectedItemsPos(self,cCtrlName):

        oControl = self.getControl( cCtrlName )
        return oControl.getSelectedItemsPos()

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
    #---------------------------------------------------
    #    com.sun.star.awt.UnoControlImageControlModel
    #---------------------------------------------------
    def addImageControl( self, cCtrlName, nPositionX, nPositionY, nWidth, nHeight,
                        sImagePath="",
                        itemListenerProc=None,
                        actionListenerProc=None ):

        mod = self.addControl( "com.sun.star.awt.UnoControlImageControlModel",
                         cCtrlName, nPositionX, nPositionY, nWidth, nHeight, sImagePath=sImagePath)

        if itemListenerProc != None:
            self.addItemListenerProc( cCtrlName, itemListenerProc )
        if actionListenerProc != None:
            self.addActionListenerProc( cCtrlName, actionListenerProc )


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

    def setEchoChar(self, cCtrlName , cVal):
        self.setControlModelProperty(cCtrlName, "EchoChar", cVal)
    def getEchoChar(self, cCtrlName):
        return self.setControlModelProperty(cCtrlName, "EchoChar")

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

import urllib

def get_absolute_file_path( url ):
	url_unquoted = urllib.unquote(url)
	return os.name == 'nt' and url_unquoted[1:] or url_unquoted 

# This function reads the content of a file and return it to the caller
def read_data_from_file( filename ):
	fp = file( filename, "rb" )
	data = fp.read()
	fp.close()
	return data

# This function writes the content to a file
def write_data_to_file( filename, data ):
	fp = file( filename, 'wb' )
	fp.write( data )
	fp.close()

import uno
import string
import unohelper
import xmlrpclib
from com.sun.star.task import XJobExecutor
if __name__<>"package":
    from lib.gui import *
    from lib.error import ErrorDialog
    from lib.functions import *
#    from Change import *
    database="test"

class ServerParameter( unohelper.Base, XJobExecutor ):
    def __init__(self,ctx):
        self.ctx     = ctx
        self.module  = "openerp_report"
        self.version = "0.1"
        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        self.win=DBModalDialog(60, 50, 160, 108, "Server Connection Parameter")

        self.win.addFixedText("lblVariable", 2, 12, 35, 15, "Server URL")
        if docinfo.getUserFieldValue(0)=="":
            docinfo.setUserFieldValue(0,"http://localhost:8069")
        self.win.addEdit("txtHost",-34,9,91,15,docinfo.getUserFieldValue(0))
        self.win.addButton('btnChange',-2 ,9,30,15,'Change', actionListenerProc = self.btnChange_clicked )

        self.win.addFixedText("lblDatabaseName", 6, 31, 31, 15, "Database")
        #self.win.addFixedText("lblMsg", -2,28,123,15)
        self.win.addComboListBox("lstDatabase", -2,28,123,15, True)
        self.lstDatabase = self.win.getControl( "lstDatabase" )
        #self.win.selectListBoxItem( "lstDatabase", docinfo.getUserFieldValue(2), True )
        #self.win.setEnabled("lblMsg",False)

        self.win.addFixedText("lblLoginName", 17, 51, 20, 15, "Login")
        self.win.addEdit("txtLoginName",-2,48,123,15,docinfo.getUserFieldValue(1))

        self.win.addFixedText("lblPassword", 6, 70, 31, 15, "Password")
        self.win.addEdit("txtPassword",-2,67,123,15,)
        self.win.setEchoChar("txtPassword",42)


        self.win.addButton('btnOK',-2 ,-5, 60,15,'Connect' ,actionListenerProc = self.btnOk_clicked )

        self.win.addButton('btnCancel',-2 - 60 - 5 ,-5, 35,15,'Cancel' ,actionListenerProc = self.btnCancel_clicked )
        sValue=""
        if docinfo.getUserFieldValue(0)<>"":
            res=getConnectionStatus(docinfo.getUserFieldValue(0))
            if res == -1:
                sValue="Could not connect to the server!"
                self.lstDatabase.addItem("Could not connect to the server!",0)
            elif res == 0:
                sValue="No Database found !!!"
                self.lstDatabase.addItem("No Database found !!!",0)
            else:
                self.win.removeListBoxItems("lstDatabase", 0, self.win.getListBoxItemCount("lstDatabase"))
		for i in range(len(res)):
                    self.lstDatabase.addItem(res[i],i)
                sValue = database

        self.win.doModalDialog("lstDatabase",sValue)

        #self.win.doModalDialog("lstDatabase",docinfo.getUserFieldValue(2))

    def btnOk_clicked(self,oActionEvent):
        sock = xmlrpclib.ServerProxy(self.win.getEditText("txtHost")+'/xmlrpc/common')
        sDatabase=self.win.getListBoxSelectedItem("lstDatabase")
        sLogin=self.win.getEditText("txtLoginName")
        sPassword=self.win.getEditText("txtPassword")
        UID = sock.login(sDatabase,sLogin,sPassword)
        if not UID :
            ErrorDialog("Connection Refuse...","Please enter valid Login/Password")
            self.win.endExecute()
        try:
            sock_g = xmlrpclib.ServerProxy(self.win.getEditText("txtHost") +'/xmlrpc/object')
            ids  = sock_g.execute(sDatabase,UID,sPassword, 'res.groups' ,  'search', [('name','=','OpenOfficeReportDesigner')])
            ids_module = sock_g.execute(sDatabase, UID, sPassword, 'ir.module.module', 'search', [('name','=','base_report_designer'),('state', '=', 'installed')])
            dict_groups = sock_g.execute(sDatabase, UID,sPassword, 'res.groups' , 'read',ids,['users'])
        except :
            pass
        if not len(ids_module):
            ErrorDialog("Please Install base_report_designer module", "", "Module Uninstalled Error")
            self.win.endExecute()
            
        if UID not in dict_groups[0]['users']:
            ErrorDialog("Connection Refuse...","You have not access these Report Designer")
            self.win.endExecute()
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
            global uid
            uid=UID
            #docinfo.setUserFieldValue(2,self.win.getListBoxSelectedItem("lstDatabase"))
            #docinfo.setUserFieldValue(3,"")
            ErrorDialog(" You can start creating your report in \nthe current document.","Take care to save it as a .SXW file \nbefore sending to the server.","Message")
            self.win.endExecute()

    def btnCancel_clicked( self, oActionEvent ):
        self.win.endExecute()

    def btnChange_clicked(self,oActionEvent):
        aVal=[]
        url= self.win.getEditText("txtHost")
        Change(aVal,url)
        if aVal[1]== -1:
            ErrorDialog(aVal[0],"")
        elif aVal[1]==0:
            ErrorDialog(aVal[0],"")
        else:
            self.win.setEditText("txtHost",aVal[0])
            self.win.removeListBoxItems("lstDatabase", 0, self.win.getListBoxItemCount("lstDatabase"))
            for i in range(len(aVal[1])):
                self.lstDatabase.addItem(aVal[1][i],i)


if __name__<>"package" and __name__=="__main__":
    ServerParameter(None)
elif __name__=="package":
    g_ImplementationHelper = unohelper.ImplementationHelper()
    g_ImplementationHelper.addImplementation( ServerParameter, "org.openoffice.openerp.report.serverparam", ("com.sun.star.task.Job",),)


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
    database="test"
    uid = 3

#
class ModifyExistingReport(unohelper.Base, XJobExecutor):
    def __init__(self,ctx):
        self.ctx     = ctx
        self.module  = "openerp_report"
        self.version = "0.1"

        LoginTest()
        if not loginstatus and __name__=="package":
            exit(1)

        self.win = DBModalDialog(60, 50, 180, 120, "Modify Existing Report")
        self.win.addFixedText("lblReport", 2, 3, 60, 15, "Report Selection")
        self.win.addComboListBox("lstReport", -1,15,178,80 , False )
        self.lstReport = self.win.getControl( "lstReport" )

        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()

        self.hostname = docinfo.getUserFieldValue(0)
        global passwd
        self.password = passwd
        # Open a new connexion to the server
        sock = xmlrpclib.ServerProxy( self.hostname +'/xmlrpc/object')

        ids = sock.execute(database, uid, self.password, 'ir.module.module', 'search', [('name','=','base_report_designer'),('state', '=', 'installed')])
        if not len(ids):
            ErrorDialog("Please Install base_report_designer module", "", "Module Uninstalled Error")
            exit(1)

        ids = sock.execute(database, uid, self.password, 'ir.actions.report.xml', 'search', [('report_xsl', '=', False),('report_xml', '=', False),('model','=','dm.offer.document')])

        fields=['id', 'name','report_name','model' , 'actual_model']

        self.reports = sock.execute(database, uid, self.password, 'ir.actions.report.xml', 'read', ids, fields)
        self.report_with_id = []

        for report in self.reports:
            if report['name']<>"":
                model_ids = sock.execute(database, uid, self.password, 'ir.model' ,  'search', [('model','=', report['model'])])
                model_res_other = sock.execute(database, uid, self.password, 'ir.model', 'read', model_ids, [ 'name', 'model' ] )
                if model_res_other <> []:
                    name = model_res_other[0]['name'] + " - " + report['name']
                else:
                    name = report['name'] + " - " + report['model']
                self.report_with_id.append( (report['id'], name, report['model'], report['actual_model'] ) )

        self.report_with_id.sort( lambda x, y: cmp( x[1], y[1] ) )

        for id, report_name, model_name, actual_model in self.report_with_id:
            self.lstReport.addItem( report_name, self.lstReport.getItemCount() )

        self.win.addButton('btnSave',10,-5,50,15,'Open Report' ,actionListenerProc = self.btnOk_clicked )
        self.win.addButton('btnCancel',-10 ,-5,50,15,'Cancel' ,actionListenerProc = self.btnCancel_clicked )
        self.win.addButton('btnDelete',15 -80 ,-5,50,15,'Delete Report',actionListenerProc = self.btnDelete_clicked)
        self.win.doModalDialog("lstReport",self.report_with_id[0][1] )

    def btnOk_clicked(self, oActionEvent):
        try:
            desktop=getDesktop()
            doc = desktop.getCurrentComponent()
            docinfo=doc.getDocumentInfo()
            sock = xmlrpclib.ServerProxy( self.hostname +'/xmlrpc/object')
            selectedItemPos = self.win.getListBoxSelectedItemPos( "lstReport" )
            id = self.report_with_id[ selectedItemPos ][0]

            res = sock.execute(database, uid, self.password, 'ir.actions.report.xml', 'report_get', id)

            fp_name = tempfile.mktemp('.'+"sxw")
            fp_name1="r"+fp_name
            fp_path=os.path.join(fp_name1).replace("\\","/")
            fp_win=fp_path[1:]

            filename = ( os.name == 'nt' and fp_win or fp_name )
            if res['report_sxw_content']:
                write_data_to_file( filename, base64.decodestring(res['report_sxw_content']))
            url = "file:///%s" % filename

            arr=Array(makePropertyValue("MediaType","application/vnd.sun.xml.writer"),)
            oDoc2 = desktop.loadComponentFromURL(url, "openerp", 55, arr)
            docinfo2=oDoc2.getDocumentInfo()
            docinfo2.setUserFieldValue(0, self.hostname)
            docinfo2.setUserFieldValue(1,self.password)
            docinfo2.setUserFieldValue(2,id)
            model = self.report_with_id[selectedItemPos][3]  or self.report_with_id[selectedItemPos][2]
            docinfo2.setUserFieldValue(3,model)

            oParEnum = oDoc2.getTextFields().createEnumeration()
            while oParEnum.hasMoreElements():
                oPar = oParEnum.nextElement()
                if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                    oPar.SelectedItem = oPar.Items[0]
                    oPar.update()
            if oDoc2.isModified():
                if oDoc2.hasLocation() and not oDoc2.isReadonly():
                    oDoc2.store()

            ErrorDialog("Download is Completed","Your file has been placed here :\n"+ fp_name,"Download Message")
        except Exception, e:
            ErrorDialog("Report has not been downloaded", "Report: %s\nDetails: %s" % ( fp_name, e ),"Download Message")
        self.win.endExecute()

    def btnCancel_clicked( self, oActionEvent ):
        self.win.endExecute()

    def btnDelete_clicked( self, oActionEvent ):
         desktop=getDesktop()
         doc = desktop.getCurrentComponent()
         docinfo=doc.getDocumentInfo()
         sock = xmlrpclib.ServerProxy( self.hostname +'/xmlrpc/object')
         selectedItemPos = self.win.getListBoxSelectedItemPos( "lstReport" )
         name=self.win.getListBoxSelectedItem ("lstReport")
         id = self.report_with_id[ selectedItemPos ][0]
         temp = sock.execute(database, uid, self.password, 'ir.actions.report.xml', 'unlink', id,)
         str_value='ir.actions.report.xml,'+str(id)
         ids = sock.execute(database, uid, self.password, 'ir.values' ,  'search',[('value','=',str_value)])
         if ids:
              rec = sock.execute(database, uid, self.password, 'ir.values', 'unlink', ids,)
         else :
            pass
         if temp:
              ErrorDialog("Report","Report has been Delete:\n "+name,"Message")
         else:
             ErrorDialog("Report","Report has not Delete:\n"+name," Message")
         self.win.endExecute()



if __name__<>"package" and __name__=="__main__":
    ModifyExistingReport(None)
elif __name__=="package":
    g_ImplementationHelper.addImplementation( ModifyExistingReport, "org.openoffice.openerp.report.modifyreport", ("com.sun.star.task.Job",),)


import uno
import string
import unohelper
import random
import xmlrpclib
import base64, tempfile
from com.sun.star.task import XJobExecutor
import os
import sys
if __name__<>'package':
    from lib.gui import *
    from lib.error import *
    from lib.functions import *
    from lib.tools import * 
    from LoginTest import *
    database="dm"
    uid = 1
#
#
class SendtoServer(unohelper.Base, XJobExecutor):
    Kind = {
        'PDF' : 'pdf',
        'OpenOffice': 'sxw',
        'HTML' : 'html'
    }

    def __init__(self,ctx):
        self.ctx     = ctx
        self.module  = "openerp_report"
        self.version = "0.1"
        LoginTest()
        if not loginstatus and __name__=="package":
            exit(1)

        global passwd
        self.password = passwd
        self.password = 'admin'

        desktop=getDesktop()
        oDoc2 = desktop.getCurrentComponent()
        docinfo=oDoc2.getDocumentInfo()
        sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
        self.ids = sock.execute(database, uid, self.password, 'ir.module.module', 'search', [('name','=','base_report_designer'),('state', '=', 'installed')])
        if not len(self.ids):
            ErrorDialog("Please Install base_report_designer module", "", "Module Uninstalled Error")
            exit(1)

        report_name = ""
        name=""
        if docinfo.getUserFieldValue(2)<>"" :
            try:
                fields=['name','report_name']
                self.res_other = sock.execute(database, uid, self.password, 'ir.actions.report.xml', 'read', [docinfo.getUserFieldValue(2)],fields)
                name = self.res_other[0]['name']
                report_name = self.res_other[0]['report_name']
            except:
                pass
        elif docinfo.getUserFieldValue(3) <> "":
            name = ""
            result =  "rnd"
            for i in range(5):
                result =result + random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')

            report_name = docinfo.getUserFieldValue(3) + "." + result
        else:
            ErrorDialog("Please select appropriate module...","Note: use OpenERP Report -> Open a new Report", "Module selection ERROR");
            exit(1)

        self.win = DBModalDialog(60, 50, 180, 100, "Send To Server")
        self.win.addFixedText("lblName",10 , 9, 40, 15, "Report Name :")
        self.win.addEdit("txtName", -5, 5, 123, 15,name)
        self.win.addFixedText("lblReportName", 2, 30, 50, 15, "Technical Name :")
        self.win.addEdit("txtReportName", -5, 25, 123, 15,report_name)
        self.win.addCheckBox("chkHeader", 51, 45, 70 ,15, "Corporate Header")
        self.win.addFixedText("lblResourceType", 2 , 60, 50, 15, "Select Rpt. Type :")
        self.win.addComboListBox("lstResourceType", -5, 58, 123, 15,True,itemListenerProc=self.lstbox_selected)
        self.lstResourceType = self.win.getControl( "lstResourceType" )

        for kind in self.Kind.keys(): 
            self.lstResourceType.addItem( kind, self.lstResourceType.getItemCount() )

        self.win.addButton( "btnSend", -5, -5, 80, 15, "Send Report to Server", actionListenerProc = self.btnOk_clicked)
        self.win.addButton( "btnCancel", -5 - 80 -5, -5, 40, 15, "Cancel", actionListenerProc = self.btnCancel_clicked)

        self.win.doModalDialog("lstResourceType", self.Kind.keys()[0])

    def lstbox_selected(self,oItemEvent):
        pass

    def btnCancel_clicked( self, oActionEvent ):
        self.win.endExecute()

    def btnOk_clicked(self, oActionEvent):
        if self.win.getEditText("txtName") <> "" and self.win.getEditText("txtReportName") <> "":
            desktop=getDesktop()
            oDoc2 = desktop.getCurrentComponent()
            docinfo=oDoc2.getDocumentInfo()
            self.getInverseFieldsRecord(1)
            fp_name = tempfile.mktemp('.'+"sxw")
            global dm_data            
            if not oDoc2.hasLocation():
                oDoc2.storeAsURL("file://"+fp_name,Array(makePropertyValue("MediaType","application/vnd.sun.xml.writer"),))
            sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
            if docinfo.getUserFieldValue(2)=="":
                id=self.getID()
                docinfo.setUserFieldValue(2,id)
                model = docinfo.getUserFieldValue(3)
                if dm_data :
                    model ='dm.offer.document'
                rec = { 
                    'name': self.win.getEditText("txtReportName"), 
                    'key': 'action', 
                    'model': model,
                    'value': 'ir.actions.report.xml,'+str(id),
                    'key2': 'client_print_multi',
                    'object': True 
                }
            else:
                id = docinfo.getUserFieldValue(2)
                rec = { 'name': self.win.getEditText("txtReportName") }
            oDoc2.store()
            data = read_data_from_file( get_absolute_file_path( oDoc2.getURL()[7:] ) )
            self.getInverseFieldsRecord(0)
            res = sock.execute(database, uid, self.password, 'ir.actions.report.xml', 'upload_report', int(docinfo.getUserFieldValue(2)),base64.encodestring(data),{'actual_model' : model[1]})
            params = {
                'name': self.win.getEditText("txtName"),
                'model': docinfo.getUserFieldValue(3),
                'report_name': self.win.getEditText("txtReportName"),
                'header': (self.win.getCheckBoxState("chkHeader") <> 0),
                'report_type': self.Kind[self.win.getListBoxSelectedItem("lstResourceType")],
            }
            if dm_data : 
                params['model'] ='dm.offer.document'
                params['actual_model'] = dm_data['model']
                params['document_id'] = dm_data['document_id']
            res = sock.execute(database, uid, self.password, 'ir.actions.report.xml', 'write', int(docinfo.getUserFieldValue(2)), params)
#            res = sock.execute(database, uid, self.password, 'ir.actions.report.xml', 'upload_report', int(docinfo.getUserFieldValue(2)),base64.encodestring(data))
            self.win.endExecute()
        else:
            ErrorDialog("Either Report Name or Technical Name is blank !!!\nPlease specify appropriate Name","","Blank Field ERROR")

    def getID(self):
        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        params = {
            'name': self.win.getEditText("txtName"),
            'model': docinfo.getUserFieldValue(3),
            'report_name': self.win.getEditText('txtReportName')
        }

        sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
        id=sock.execute(database, uid, self.password, 'ir.actions.report.xml' ,'create', params)
        return id

    def getInverseFieldsRecord(self,nVal):
        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        count=0
        oParEnum = doc.getTextFields().createEnumeration()
        while oParEnum.hasMoreElements():
            oPar = oParEnum.nextElement()
            if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                oPar.SelectedItem = oPar.Items[nVal]
                if nVal==0:
                    oPar.update()

if __name__<>"package" and __name__=="__main__":
    SendtoServer(None)
elif __name__=="package":
    g_ImplementationHelper.addImplementation( SendtoServer, "org.openoffice.openerp.report.sendtoserver", ("com.sun.star.task.Job",),)

import uno
from com.sun.star.task import XJobExecutor

if __name__<>'package':
    from lib.gui import *

class About(unohelper.Base, XJobExecutor):
    def __init__(self,ctx):
        self.ctx     = ctx
        self.module  = "openerp_report"
        self.version = "0.1"
        self.win = DBModalDialog(60, 50, 175, 115, ".:: About Direct Marketing Document Creation ::.")

        fdBigFont = createUnoStruct("com.sun.star.awt.FontDescriptor")
        fdBigFont.Width = 20
        fdBigFont.Height = 25
        fdBigFont.Weight = 120
        fdBigFont.Family= 3

#        oLabelTitle1 = self.win.addFixedText("lblTitle1", 1, 1, 35, 30)
#        oLabelTitle1.Model.TextColor = 16056320
#        oLabelTitle1.Model.FontDescriptor = fdBigFont
#        oLabelTitle1.Model.FontRelief = 1
#        oLabelTitle1.Text = "Open"

        oLabelTitle2 = self.win.addFixedText("lblTitle2", 35, 1, 30, 30)
        oLabelTitle2.Model.TextColor = 1
        oLabelTitle2.Model.FontDescriptor = fdBigFont
        oLabelTitle2.Model.FontRelief = 1
        oLabelTitle2.Text = "Direct Marketing Reporting" 

        oLabelProdDesc = self.win.addFixedText("lblProdDesc", 1, 30, 173, 75)
        oLabelProdDesc.Model.TextColor = 1
        fdBigFont.Width = 10
        fdBigFont.Height = 11
        fdBigFont.Weight = 76
        oLabelProdDesc.Model.FontDescriptor = fdBigFont
        oLabelProdDesc.Model.Align = 1
        oLabelProdDesc.Model.FontRelief = 1
        oLabelProdDesc.Model.MultiLine = True
        oLabelProdDesc.Text = "Direct Marketing Reporting tool helps one to generate \ndocuments,for the end client.Once your connected with \nserver you can select document of particular offer,for\nwhich you want to generate document for end user.After\ncreating it one need to send it back to the server and\ncheck it in selected document record."

        oLabelFooter = self.win.addFixedText("lblFooter", -1, -1, 173, 25)
        oLabelFooter.Model.TextColor = 255
        #oLabelFooter.Model.BackgroundColor = 1
        oLabelFooter.Model.Border = 2
        oLabelFooter.Model.BorderColor = 255
        fdBigFont.Width = 8
        fdBigFont.Height = 9
        fdBigFont.Weight = 100
        oLabelFooter.Model.FontDescriptor = fdBigFont
        oLabelFooter.Model.Align = 1
        oLabelFooter.Model.FontRelief = 1
        oLabelFooter.Model.MultiLine = True
        sMessage = "OpenERP Report Designer v1.0 \nCopyright 2007-TODAY Tiny sprl \nThis product is free software, under the GPL licence."
        oLabelFooter.Text = sMessage

        self.win.doModalDialog("",None)

if __name__<>"package" and __name__=="__main__":
    About(None)
elif __name__=="package":
    g_ImplementationHelper.addImplementation( About, "org.openoffice.openerp.report.about", ("com.sun.star.task.Job",),)

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
    database="dm"
    uid = 1

def genDmTree(object,aList,insField,host,level=3, ending=[], ending_excl=[], recur=[], root='', actualroot=""):
    try:
        sock = xmlrpclib.ServerProxy(host+'/xmlrpc/object')
        global passwd
        passwd = 'admin'
        global dm_data
        document_id = dm_data['document_id']
        model = dm_data['model']
        field = dm_data['field']
        res = sock.execute(database, uid, passwd, object , 'fields_get')
        key = res.keys()
        key.sort()
        if document_id and model and object == model:
            custom = sock.execute(database, uid, passwd, 'dm.offer.document' , 'read', [document_id],[field] )[0]
            custom_field_ids = custom[field]
            custom_fields =sock.execute(database, uid, passwd, 'ir.model.fields' , 'read', custom_field_ids, )
            key = map(lambda c:c['name'],custom_fields)
            key.sort()
        for k in key:
            if (not ending or res[k]['type'] in ending) and ((not ending_excl) or not (res[k]['type'] in ending_excl)):
                insField.addItem(root+'/'+res[k]["string"],len(aList))
                aList.append(actualroot+'/'+k)
            if (res[k]['type'] in recur) and (level>0):
                genTree(res[k]['relation'],aList,insField,host ,level-1, ending, ending_excl, recur,root+'/'+res[k]["string"],actualroot+'/'+k)
    except:
        import traceback;traceback.print_exc()
def getDmList(aObjectList,host,count):
    desktop=getDesktop()
    doc =desktop.getCurrentComponent()
    docinfo=doc.getDocumentInfo()
    sMain=""
    if not count == 0:
        if count >=1:
            oParEnum = doc.getTextFields().createEnumeration()
            while oParEnum.hasMoreElements():
                oPar = oParEnum.nextElement()
                if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                    sItem=oPar.Items[1]
                    if sItem[sItem.find("[[ ")+3:sItem.find("(")]=="repeatIn":
                        if sItem[sItem.find("(")+1:sItem.find(",")]=="objects":
                            aObjectList.append(sItem[sItem.rfind(",'")+2:sItem.rfind("')")] + "(" + docinfo.getUserFieldValue(3) + ")")
                        else:
                            sTemp=sItem[sItem.find("(")+1:sItem.find(",")]
                            if sMain == sTemp[:sTemp.find(".")]:
                                getDmRelation(docinfo.getUserFieldValue(3), sItem[sItem.find(".")+1:sItem.find(",")], sItem[sItem.find(",'")+2:sItem.find("')")],aObjectList,host)
                            else:
                                sPath=getPath(sItem[sItem.find("(")+1:sItem.find(",")], sMain)
                                getDmRelation(docinfo.getUserFieldValue(3), sPath[sPath.find(".")+1:], sItem[sItem.find(",'")+2:sItem.find("')")],aObjectList,host)
    else:
        aObjectList.append("List of " + docinfo.getUserFieldValue(3))
def getDmRelation(sRelName, sItem, sObjName, aObjectList, host ):
    sock = xmlrpclib.ServerProxy(host+'/xmlrpc/object')
    global passwd
    global dm_data
    document_id = dm_data['document_id']
    model = dm_data['model']
    field = dm_data['field']
    res = sock.execute(database, uid, passwd, sRelName , 'fields_get')
    key = res.keys()
    if document_id and model and object == model[0]:
        custom = sock.execute(database, uid, passwd, 'dm.offer.document' , 'read', [document_id],field )[0]
        custom_field_ids = custom[field]
        custom_fields =sock.execute(database, uid, passwd, 'ir.model.fields' , 'read', custom_field_ids, )
        key = map(lambda c:c['name'],custom_fields)
        key.sort()

    for k in key:
        if sItem.find(".") == -1:
            if k == sItem:
                aObjectList.append(sObjName + "(" + res[k]['relation'] + ")")
                return 0
    if k == sItem[:sItem.find(".")]:
        getRelation(res[k]['relation'], sItem[sItem.find(".")+1:], sObjName,aObjectList,host)
    
#class directmarketing:
class Directmarketing( unohelper.Base, XJobExecutor ):
    def __init__(self,ctx):
        self.ctx     = ctx
        self.module  = "openerp_report"
        self.version = "0.1"
        LoginTest()
        if not loginstatus and __name__=="package":
            exit(1)
        global passwd
        global dm_data
        dm_data={}
        self.password = passwd
        self.password = 'admin'
        self.OfferCode={}
        self.OfferStepCode={}
        self.OfferDocument={}
        self.aListModel={}

        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        self.docinfo=doc.getDocumentInfo()
        
        self.sock = xmlrpclib.ServerProxy(self.docinfo.getUserFieldValue(0) +'/xmlrpc/object')
        self.sMyHost = self.docinfo.getUserFieldValue(0)
        self.win = DBModalDialog(60, 50, 180, 105, "Direct Marketing")

        ids = self.sock.execute(database, uid, self.password, 'ir.module.module', 'search', [('name','=','base_report_designer'),('state', '=', 'installed')])
        if not len(ids):
            ErrorDialog("Please Install base_report_designer  module first!", "", "Module Uninstalled Error")
            exit(1)

        ids = self.sock.execute(database, uid, self.password, 'ir.module.module', 'search', [('name','=','dm'),('state', '=', 'installed')])
        if not len(ids):
            ErrorDialog("Please Install Direct Marketing  module to continue!", "", "Module Uninstalled Error")
            exit(1)

        self.win.addFixedText("lblOffer", 2, 12, 60, 15, "Select Offer:")

        self.win.addComboBox("cmbOffer", 180-120-2, 10, 120, 15,True,itemListenerProc=self.changeOffer)
        self.cmbOffer = self.win.getControl( "cmbOffer" )
        
        ids = self.sock.execute(database, uid, self.password, 'dm.offer', 'search', [('state','=','draft')])
        res = self.sock.execute(database, uid, self.password, 'dm.offer' , 'read', ids,['code'] )
        res.sort(lambda x, y: cmp(x['code'],y['code']))

        for r in res:
            self.cmbOffer.addItem(r['code'],self.cmbOffer.getItemCount())
            self.OfferCode[r['code']] = r['id']

        self.win.addFixedText("lblOfferStep", 2, 28, 60, 15 ,"Select Offer Step :")
        self.win.addComboBox("cmbOfferStep", 180-120-2, 28, 120, 15 , True ,itemListenerProc=self.changeOfferStep)
        self.cmbOfferStep = self.win.getControl( "cmbOfferStep" )

        self.win.addFixedText("lblDocument", 2, 44, 60, 15 ,"Document :")
        self.win.addComboBox("cmbDocument", 180-120-2, 46, 120, 15 , True,itemListenerProc=self.selectDocument)
        self.cmbDocument = self.win.getControl( "cmbDocument" )

        self.win.addFixedText("lblmodel", 2, 62, 60, 15 ,"Model :")
        self.win.addComboBox("cmbmodel", 180-120-2, 64, 120, 15 , True)#,itemListenerProc=self.selectDocument)
        self.cmbmodel = self.win.getControl( "cmbmodel" )
        
        self.win.addButton('btnOK',-2 ,-5,45,15,'Ok', actionListenerProc = self.btnOk_clicked )

        self.win.addButton('btnCancel',-2 - 45 - 5 ,-5,45,15,'Cancel', actionListenerProc = self.btnCancel_clicked )

        self.win.doModalDialog("cmbOffer",None)

    def selectDocument(self,oActionEvent):
        document_code = self.win.getComboBoxSelectedText("cmbDocument")
        res = self.sock.execute(database, uid, self.password, 'dm.offer.document' , 'fields_get')
        key = res.keys()
        key.sort()
        for k in key:
            if res[k]['type'] =='many2many' and res[k]['relation']=='ir.model.fields':
                self.cmbmodel.addItem(res[k]["string"],len(self.aListModel))
                self.aListModel[res[k]["string"]]=(res[k]['context']['model'],k)
                
    def changeOfferStep(self,oActionEvent):
        offer_step=self.win.getComboBoxSelectedText("cmbOfferStep")

        offer_step_id = self.OfferStepCode[offer_step]
        
        ids = self.sock.execute(database, uid, self.password, 'dm.offer.document', 'search', [('step_id','=',offer_step_id)])
        res = self.sock.execute(database, uid, self.password, 'dm.offer.document' , 'read', ids,['code','customer_field_ids','customer_order_field_ids'] )

        res.sort(lambda x, y: cmp(x['code'],y['code']))

        self.win.removeListBoxItems("cmbDocument", 0, self.win.getListBoxItemCount("cmbDocument"))

        for r in res:
            self.cmbDocument.addItem(r['code'],self.cmbDocument.getItemCount())
            self.OfferDocument[r['code']] = (r['id'],r['customer_field_ids'],r['customer_order_field_ids'])

    def changeOffer(self,oActionEvent):

        offer=self.win.getComboBoxSelectedText("cmbOffer")
        offer_id = self.OfferCode[offer]
        
        ids = self.sock.execute(database, uid, self.password, 'dm.offer.step', 'search', [('offer_id','=',offer_id)])
        res = self.sock.execute(database, uid, self.password, 'dm.offer.step' , 'read', ids,['code'] )
        res.sort(lambda x, y: cmp(x['code'],y['code']))
        
        self.win.removeListBoxItems("cmbOfferStep", 0, self.win.getListBoxItemCount("cmbOfferStep"))

        self.OfferStepCode={}
        
        for r in res:
            self.cmbOfferStep.addItem(r['code'],self.cmbOfferStep.getItemCount())
            self.OfferStepCode[r['code']] = r['id']


    def btnOk_clicked(self,oActionEvent):
        if self.win.getComboBoxSelectedText("cmbDocument") :
            document_code = self.win.getComboBoxSelectedText("cmbDocument")
            document_id =  self.OfferDocument[document_code][0]
            sMain=self.win.getComboBoxSelectedText("cmbmodel")
            global dm_data
            dm_data['document_id']=document_id                
            dm_data['field'] = self.aListModel[sMain][1]
            dm_data['model'] = self.aListModel[sMain][0]
            self.docinfo.setUserFieldValue(3,dm_data['model'])
            obj = dm_data['model'].split('.')[-1]
            sValue="[[ repeatIn(objects,'%s') ]]"%obj
            sKey = "|-."+obj+".-|"            
            desktop=getDesktop()
            doc = desktop.getCurrentComponent()
            cursor = doc.getCurrentController().getViewCursor()
            oInputList = doc.createInstance("com.sun.star.text.TextField.DropDown")
            oInputList.Items = (sKey,sValue)
            doc.Text.insertTextContent(cursor,oInputList,False)
        else :
            ErrorDialog('You have not selected any document \n First select document','',"Direct Marketing")
        self.win.endExecute()
    def btnCancel_clicked( self, oActionEvent ):
        self.win.endExecute()

if __name__<>"package" and __name__=="__main__":
    Directmarketing(None)
elif __name__=="package":
    g_ImplementationHelper.addImplementation( \
            Directmarketing,
            "org.openoffice.openerp.report.directmarketing",
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
    database="dm"
    uid = 1
    
class AddFields(unohelper.Base, XJobExecutor ):
    def __init__(self,sVariable="",sFields="",sDisplayName="",bFromModify=False):
        LoginTest()
        if not loginstatus and __name__=="package":
            exit(1)
        self.win = DBModalDialog(60, 50, 200, 225, "Field Builder")

        self.win.addFixedText("lblVariable", 27, 12, 60, 15, "Variable :")
        self.win.addComboBox("cmbVariable", 180-120-2, 10, 130, 15,True, itemListenerProc=self.cmbVariable_selected)
        self.insVariable = self.win.getControl( "cmbVariable" )

        self.win.addFixedText("lblFields", 10, 32, 60, 15, "Variable Fields :")
        self.win.addComboListBox("lstFields", 180-120-2, 30, 130, 150, False,True,itemListenerProc=self.lstbox_selected)
        self.insField = self.win.getControl( "lstFields" )

        self.win.addFixedText("lblUName", 8, 187, 60, 15, "Displayed name :")
        self.win.addEdit("txtUName", 180-120-2, 185, 130, 15,)

        self.win.addButton('btnOK',-5 ,-5,45,15,'Ok' ,actionListenerProc = self.btnOk_clicked )
        self.win.addButton('btnCancel',-5 - 45 - 5 ,-5,45,15,'Cancel' ,actionListenerProc = self.btnCancel_clicked )

        global passwd
        self.password = passwd

        self.sValue=None
        self.sObj=None
        self.aSectionList=[]
        self.sGDisplayName=sDisplayName
        self.aItemList=[]
        self.aComponentAdd=[]
        self.aObjectList=[]
        self.aListFields=[]
        self.aVariableList=[]
        EnumDocument(self.aItemList,self.aComponentAdd)
        desktop=getDesktop()
        doc =desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        self.sMyHost= ""

        if not docinfo.getUserFieldValue(3) == "" and not docinfo.getUserFieldValue(0)=="":
            self.sMyHost = docinfo.getUserFieldValue(0)
            self.count = 0
            oParEnum = doc.getTextFields().createEnumeration()

            while oParEnum.hasMoreElements():
                oPar = oParEnum.nextElement()
                if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                    self.count += 1

            getList(self.aObjectList, self.sMyHost,self.count)
            cursor = doc.getCurrentController().getViewCursor()
            text = cursor.getText()
            tcur = text.createTextCursorByRange(cursor)
            self.aVariableList.extend( filter( lambda obj: obj[:obj.find("(")] == "Objects", self.aObjectList ) )
            for i in range(len(self.aItemList)):
                anItem = self.aItemList[i][1]
                component = self.aComponentAdd[i]
                if component == "Document":
                    sLVal = anItem.split("'")[-2]
                    self.aVariableList.extend( filter( lambda obj: obj[:obj.find("(")] == sLVal, self.aObjectList ) )
                if tcur.TextSection:
                    getRecersiveSection(tcur.TextSection,self.aSectionList)
                    if component in self.aSectionList:
                        sLVal = anItem[anItem.find(",'") + 2:anItem.find("')")]
                        self.aVariableList.extend( filter( lambda obj: obj[:obj.find("(")] == sLVal, self.aObjectList ) )
                if tcur.TextTable:
                    if not component == "Document" and component[component.rfind(".")+1:] == tcur.TextTable.Name:
                        VariableScope(tcur, self.aVariableList, self.aObjectList, self.aComponentAdd, self.aItemList, component)

            self.bModify=bFromModify
            if self.bModify==True:
                sItem=""
                for anObject in self.aObjectList:
                    if anObject[:anObject.find("(")] == sVariable:
                        sItem = anObject
                        self.insVariable.setText(sItem)
                genDmTree(
                    sItem[sItem.find("(")+1:sItem.find(")")],
                    self.aListFields,
                    self.insField,
                    self.sMyHost,
                    2,
                    ending_excl=['one2many','many2one','many2many','reference'],
                    recur=['many2one']
                )
                self.sValue= self.win.getListBoxItem("lstFields",self.aListFields.index(sFields))
            for var in self.aVariableList:
                    sock = xmlrpclib.ServerProxy(self.sMyHost + '/xmlrpc/object')
                    self.model_ids = sock.execute(database, uid, self.password, 'ir.model' ,  'search', [('model','=',var[var.find("(")+1:var.find(")")])])
                    fields=['name','model']
                    self.model_res = sock.execute(database, uid, self.password, 'ir.model', 'read', self.model_ids,fields)
                    if self.model_res <> []:
                        self.insVariable.addItem(var[:var.find("(")+1] + self.model_res[0]['name'] + ")" ,self.insVariable.getItemCount())
                    else:
                        self.insVariable.addItem(var ,self.insVariable.getItemCount())

            self.win.doModalDialog("lstFields",self.sValue)
        else:
            ErrorDialog("You have not selected document and model for \n the report.Please select it first from \n Direct Marketing Reporting ->Select Document")
            self.win.endExecute()

    def lstbox_selected(self,oItemEvent):
        try:
            sock = xmlrpclib.ServerProxy(self.sMyHost + '/xmlrpc/object')
            desktop=getDesktop()
            doc =desktop.getCurrentComponent()
            docinfo=doc.getDocumentInfo()
            sItem= self.win.getComboBoxText("cmbVariable")
            for var in self.aVariableList:
                if var[:var.find("(")+1]==sItem[:sItem.find("(")+1]:
                    sItem = var
            sMain=self.aListFields[self.win.getListBoxSelectedItemPos("lstFields")]
            sObject=self.getRes(sock,sItem[sItem.find("(")+1:-1],sMain[1:])
            ids = sock.execute(database, uid, self.password, sObject ,  'search', [])
            if ids:
                res = sock.execute(database, uid, self.password, sObject , 'read',[ids[0]])
                self.win.setEditText("txtUName",res[0][sMain[sMain.rfind("/")+1:]])
        except:
            import traceback;traceback.print_exc()
            self.win.setEditText("txtUName","TTT")
        if self.bModify:
            self.win.setEditText("txtUName",self.sGDisplayName)

    def getRes(self,sock ,sObject,sVar):
        desktop=getDesktop()
        doc =desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        res = sock.execute(database, uid, self.password, sObject , 'fields_get')
        key = res.keys()
        key.sort()
        myval=None
        if not sVar.find("/")==-1:
            myval=sVar[:sVar.find("/")]
        else:
            myval=sVar
        if myval in key:
            if (res[myval]['type'] in ['many2one']):
                sObject = res[myval]['relation']
                return self.getRes(sock,res[myval]['relation'], sVar[sVar.find("/")+1:])
            else:
                return sObject

    def cmbVariable_selected(self,oItemEvent):
        if self.count > 0 :
            try:
                desktop=getDesktop()
                doc =desktop.getCurrentComponent()
                docinfo=doc.getDocumentInfo()
                self.win.removeListBoxItems("lstFields", 0, self.win.getListBoxItemCount("lstFields"))
                self.aListFields=[]
                tempItem = self.win.getComboBoxText("cmbVariable")
                for var in self.aVariableList:
                    if var[:var.find("(")] == tempItem[:tempItem.find("(")]:
                        sItem=var

                genDmTree(
                    sItem[sItem.find("(")+1:sItem.find(")")],
                    self.aListFields,
                    self.insField,
                    self.sMyHost,
                    2,
                    ending_excl=['one2many','many2one','many2many','reference'],
                    recur=['many2one']
                )
            except:
                import traceback;traceback.print_exc()

    def btnOk_clicked( self, oActionEvent ):
        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        cursor = doc.getCurrentController().getViewCursor()
        for i in self.win.getListBoxSelectedItemsPos("lstFields"):
                itemSelected = self.aListFields[i]
                itemSelectedPos = i
                txtUName=self.win.getEditText("txtUName")
                sKey=u""+txtUName
                if itemSelected != "" and txtUName != "" and self.bModify==True :
                    txtUName=self.sGDisplayName
                    sKey=u""+txtUName
                    txtUName=self.sGDisplayName
                    oCurObj=cursor.TextField
                    sObjName=self.insVariable.getText()
                    sObjName=sObjName[:sObjName.find("(")]
                    sValue=u"[[ " + sObjName + self.aListFields[itemSelectedPos].replace("/",".") + " ]]"
                    oCurObj.Items = (sKey,sValue)
                    oCurObj.update()
                    self.win.endExecute()
                elif itemSelected != "" and txtUName != "" :

                    oInputList = doc.createInstance("com.sun.star.text.TextField.DropDown")
                    sObjName=self.win.getComboBoxText("cmbVariable")
                    sObjName=sObjName[:sObjName.find("(")]

                    widget = ( cursor.TextTable and cursor.TextTable.getCellByName( cursor.Cell.CellName ) or doc.Text )

                    sValue = u"[[ " + sObjName + self.aListFields[itemSelectedPos].replace("/",".") + " ]]"
                    oInputList.Items = (sKey,sValue)
                    widget.insertTextContent(cursor,oInputList,False)
                    self.win.endExecute()
                else:
                        ErrorDialog("Please Fill appropriate data in Name field \nor select perticular value from the list of fields")

    def btnCancel_clicked( self, oActionEvent ):
        self.win.endExecute()

if __name__<>"package" and __name__=="__main__":
    AddFields()
elif __name__=="package":
    g_ImplementationHelper.addImplementation( AddFields, "org.openoffice.openerp.report.addfields", ("com.sun.star.task.Job",),)
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
    from Directmarketing import genDmTree
    from Directmarketing import getDmList
    database="dm"
    uid = 1

#class DmLoop:
class DmLoop( unohelper.Base, XJobExecutor ):
    def __init__(self,sObject="",sVariable="",sFields="",sDisplayName="",bFromModify=False):
        # Interface Design
        LoginTest()

        if not loginstatus and __name__=="package":
            exit(1)
        
        self.win = DBModalDialog(60, 50, 180, 250, "RepeatIn Builder")
        self.win.addFixedText("lblVariable", 2, 12, 60, 15, "Objects to loop on :")
        self.win.addComboBox("cmbVariable", 180-120-2, 10, 120, 15,True, itemListenerProc=self.cmbVariable_selected)
        self.insVariable = self.win.getControl( "cmbVariable" )

        self.win.addFixedText("lblFields", 10, 32, 60, 15, "Field to loop on :")
        self.win.addComboListBox("lstFields", 180-120-2, 30, 120, 150, False,itemListenerProc=self.lstbox_selected)
        self.insField = self.win.getControl( "lstFields" )

        self.win.addFixedText("lblName", 12, 187, 60, 15, "Variable name :")
        self.win.addEdit("txtName", 180-120-2, 185, 120, 15,)

        self.win.addFixedText("lblUName", 8, 207, 60, 15, "Displayed name :")
        self.win.addEdit("txtUName", 180-120-2, 205, 120, 15,)

        self.win.addButton('btnOK',-2 ,-10,45,15,'Ok', actionListenerProc = self.btnOk_clicked )

        self.win.addButton('btnCancel',-2 - 45 - 5 ,-10,45,15,'Cancel', actionListenerProc = self.btnCancel_clicked )

        global passwd
        self.password = passwd
        
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
        self.aVariableList=[]
        # Call method to perform Enumration on Report Document
        EnumDocument(self.aItemList,self.aComponentAdd)
        # Perform checking that Field-1 and Field - 4 is available or not alos get Combobox
        # filled if condition is true
        desktop = getDesktop()
        doc = desktop.getCurrentComponent()
        docinfo = doc.getDocumentInfo()
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
            getDmList(self.aObjectList, self.sMyHost,self.count)
            cursor = doc.getCurrentController().getViewCursor()
            text = cursor.getText()
            tcur = text.createTextCursorByRange(cursor)
            self.aVariableList.extend( filter( lambda obj: obj[:obj.find(" ")] == "List", self.aObjectList ) )
            for i in range(len(self.aItemList)):
                anItem = self.aItemList[i][1]
                component = self.aComponentAdd[i]
                if component == "Document":
                    sLVal = anItem.split("'")[-2]
                    self.aVariableList.extend( filter( lambda obj: obj[:obj.find("(")] == sLVal, self.aObjectList ) )
                if tcur.TextSection:
                    getRecersiveSection(tcur.TextSection,self.aSectionList)
                if component in self.aSectionList:
                    sLVal = anItem[anItem.find(",'") + 2:anItem.find("')")]
                    self.aVariableList.extend( filter( lambda obj: obj[:obj.find("(")] == sLVal, self.aObjectList ) )
                if tcur.TextTable:
                    if not component == "Document" and component[component.rfind(".") + 1:] == tcur.TextTable.Name:
                        VariableScope( tcur, self.insVariable, self.aObjectList, self.aComponentAdd, self.aItemList, component )
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
                    for anObject in self.aObjectList:
                        if anObject[:anObject.find("(")] == sObject:
                            sItem = anObject
                            self.insVariable.setText( sItem )

                            genDmTree(
                            sItem[sItem.find("(")+1:sItem.find(")")], 
                            self.aListRepeatIn, 
                            self.insField, 
                            self.sMyHost, 
                            2, 
                            ending=['one2many','many2many'], 
                            recur=['one2many','many2many']
                            )

                    self.sValue= self.win.getListBoxItem("lstFields",self.aListRepeatIn.index(sFields))
            for var in self.aVariableList:
                sock = xmlrpclib.ServerProxy(self.sMyHost + '/xmlrpc/object')
                if var[:8] <> 'List of ':
                    self.model_ids = sock.execute(database, uid, self.password, 'ir.model' ,  'search', [('model','=',var[var.find("(")+1:var.find(")")])])
                else:
                    self.model_ids = sock.execute(database, uid, self.password, 'ir.model' ,  'search', [('model','=',var[8:])])
                fields=['name','model']
                self.model_res = sock.execute(database, uid, self.password, 'ir.model', 'read', self.model_ids,fields)
                if self.model_res <> []:
                    if var[:8]<>'List of ':
                        self.insVariable.addItem(var[:var.find("(")+1] + self.model_res[0]['name'] + ")" ,self.insVariable.getItemCount())
                    else:
                        self.insVariable.addItem('List of ' + self.model_res[0]['name'] ,self.insVariable.getItemCount())
                else:
                    self.insVariable.addItem(var ,self.insVariable.getItemCount())

            self.win.doModalDialog("lstFields",self.sValue)
        else:
            ErrorDialog("Please Select Appropriate Document first" ,"Select document from : \nOpenERP -> Direct Marketing -> Select Document")
            self.win.endExecute()

    def lstbox_selected(self,oItemEvent):
        sItem=self.win.getListBoxSelectedItem("lstFields")
        sMain=self.aListRepeatIn[self.win.getListBoxSelectedItemPos("lstFields")]

        if self.bModify==True:
            self.win.setEditText("txtName", self.sGVariable)
            self.win.setEditText("txtUName",self.sGDisplayName)
        else:
            self.win.setEditText("txtName",sMain[sMain.rfind("/")+1:])
            self.win.setEditText("txtUName","|-."+sItem[sItem.rfind("/")+1:]+".-|")

    def cmbVariable_selected(self,oItemEvent):

        if self.count > 0 :
            try :
                sock = xmlrpclib.ServerProxy(self.sMyHost + '/xmlrpc/object')
                desktop=getDesktop()
                doc =desktop.getCurrentComponent()
                docinfo=doc.getDocumentInfo()
                self.win.removeListBoxItems("lstFields", 0, self.win.getListBoxItemCount("lstFields"))
                sItem=self.win.getComboBoxText("cmbVariable")
                for var in self.aVariableList:
                    if var[:8]=='List of ':
                        if var[:8]==sItem[:8]:
                            sItem = var
                        elif var[:var.find("(")+1] == sItem[:sItem.find("(")+1]:
                            sItem = var
                        self.aListRepeatIn=[]
                data = ( sItem[sItem.rfind(" ") + 1:] == docinfo.getUserFieldValue(3) ) and docinfo.getUserFieldValue(3) or sItem[sItem.find("(")+1:sItem.find(")")]
                genDmTree( data, self.aListRepeatIn, self.insField, self.sMyHost, 2, ending=['one2many','many2many'], recur=['one2many','many2many'] )
                self.win.selectListBoxItemPos("lstFields", 0, True )
            except :
                print "Exception :::::::::"
        else:
            sItem=self.win.getComboBoxText("cmbVariable")
            for var in self.aVariableList:
                if var[:8]=='List of ' and var[:8] == sItem[:8]:
                    sItem = var
                    self.win.setEditText("txtName",sItem[sItem.rfind(".")+1:])
                    self.win.setEditText("txtUName","|-."+sItem[sItem.rfind(".")+1:]+".-|")
            self.insField.addItem("objects",self.win.getListBoxItemCount("lstFields"))
            self.win.selectListBoxItemPos("lstFields", 0, True )

    def btnOk_clicked(self, oActionEvent):
        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        cursor = doc.getCurrentController().getViewCursor()
        selectedItem = self.win.getListBoxSelectedItem( "lstFields" )
        selectedItemPos = self.win.getListBoxSelectedItemPos( "lstFields" )
        txtName = self.win.getEditText( "txtName" )
        txtUName = self.win.getEditText( "txtUName" )
        if selectedItem != "" and txtName != "" and txtUName != "":
            sKey=u""+ txtUName
            if selectedItem == "objects":
                sValue=u"[[ repeatIn(" + selectedItem + ",'" + txtName + "') ]]"
            else:
                sObjName=self.win.getComboBoxText("cmbVariable")
                sObjName=sObjName[:sObjName.find("(")]
                sValue=u"[[ repeatIn(" + sObjName + self.aListRepeatIn[selectedItemPos].replace("/",".") + ",'" + txtName +"') ]]"
            if self.bModify == True:
                oCurObj = cursor.TextField
                oCurObj.Items = (sKey,sValue)
                oCurObj.update()
            else:
                oInputList = doc.createInstance("com.sun.star.text.TextField.DropDown")
                if self.win.getListBoxSelectedItem("lstFields") == "objects":
                    oInputList.Items = (sKey,sValue)
                    widget = ( cursor.TextTable or selectedItem <> 'objects' ) and cursor.TextTable.getCellByName( cursor.Cell.CellName ) or doc.Text
                    widget.insertTextContent(cursor,oInputList,False)
                else:
                    oInputList.Items = (sKey,sValue)
                    doc.Text.insertTextContent(cursor,oInputList,False)
            self.win.endExecute()
        else:
            ErrorDialog("Please Fill appropriate data in Object Field or Name field \nor select perticular value from the list of fields")

    def btnCancel_clicked( self, oActionEvent ):
        self.win.endExecute()

if __name__<>"package" and __name__=="__main__":
    DmLoop()
elif __name__=="package":
    g_ImplementationHelper.addImplementation( \
            DmLoop,
            "org.openoffice.openerp.report.dmloop",
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
    from lib.tools import write_data_to_file
    from LoginTest import *
    database="dm"
    dm_data ={}
    dm_data['document_id']=1
    passwd = 'admin'
    uid = 1
import base64
import uno
import pyuno
import getopt, sys, string
import os
from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK
from com.sun.star.text.TextContentAnchorType import AT_PARAGRAPH, AS_CHARACTER     
    
class AddImage(unohelper.Base, XJobExecutor ):
    def __init__(self,sVariable="",sFields="",sDisplayName="",bFromModify=False):
        LoginTest()
        if not loginstatus and __name__=="package":
            exit(1)
        self.win = DBModalDialog(60, 50, 190, 90, "Field Builder")

        self.win.addFixedText("lblImage", 10, 12, 60, 15, "Attachment :")
        self.win.addComboBox("cmbImage", 180-130, 10, 130, 15,True)
        
        self.win.addButton('btnOK',-5 ,-5,45,15,'Ok' ,actionListenerProc = self.btnOk_clicked )
        self.win.addButton('btnCancel',-5 - 45 - 5 ,-5,45,15,'Cancel' ,actionListenerProc = self.btnCancel_clicked )
        
        self.cmbImage = self.win.getControl( "cmbImage" )

        global passwd
        self.password = passwd
        self.sGDisplayName=sDisplayName
        desktop=getDesktop()
        doc =desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        self.sMyHost= ""
        self.datas={}
        if not docinfo.getUserFieldValue(3) == "" and not docinfo.getUserFieldValue(0)=="":
            self.sMyHost = docinfo.getUserFieldValue(0)
            sock = xmlrpclib.ServerProxy(self.sMyHost + '/xmlrpc/object')
            
            self.attachment_ids = sock.execute(database, uid, self.password, 'ir.attachment' ,  'search', [('res_model','=','dm.offer.document'),('res_id','=',dm_data['document_id'])])
            res = sock.execute(database, uid, self.password, 'ir.attachment' ,  'read',self.attachment_ids, ['datas_fname','datas'])
            for r in res:
                self.cmbImage.addItem(r['datas_fname'],self.cmbImage.getItemCount())
                self.datas[r['datas_fname']]=r['datas']
            self.win.doModalDialog("cmbImage",None)                    
        else:
            ErrorDialog("You have not selected document and model for \n the report.Please select it first from \n Direct Marketing Reporting ->Select Document")
            self.win.endExecute()

    def create_image(self,image_file_name):
        image_ext= image_file_name.split(".")[-1]
        fp_name = tempfile.mktemp("."+image_ext)
        fp_name1="r"+fp_name
        fp_path=os.path.join(fp_name1).replace("\\","/")
        fp_win=fp_path[1:]
        filename = ( os.name == 'nt' and fp_win or fp_name )
        if image_file_name in self.datas and self.datas[image_file_name]:
            write_data_to_file( filename, base64.decodestring(self.datas[image_file_name]))
        return filename      
      
    def insert_image(self,filename):
        desktop=getDesktop()
        doc =desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        text = doc.Text
        cursor = doc.getCurrentController().getViewCursor()
        oBitmaps = doc.createInstance('com.sun.star.drawing.BitmapTable')
        oBitmaps.insertByName(filename, filename)
        url = oBitmaps.getByName(filename)
        mySize = uno.createUnoStruct('com.sun.star.awt.Size')
        mySize.Width = 5000
        mySize.Height = 5000
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        oShape = doc.createInstance("com.sun.star.drawing.GraphicObjectShape")
        oShape.GraphicURL =url 
        oShape.AnchorType = AS_CHARACTER 
        oShape.Size = mySize
        myPosition = uno.createUnoStruct('com.sun.star.awt.Point') 
        myPosition.X = oShape.Position.X-400
        myPosition.Y = oShape.Position.Y-400                    
        oShape.Position=myPosition
        text.insertTextContent(cursor,oShape,uno.Bool(0))
        
    def btnOk_clicked( self, oActionEvent ):
        try :
            image_file_name = self.win.getComboBoxSelectedText("cmbImage")
            filename = self.create_image(image_file_name)
            self.insert_image(filename)
        except Exception,e:
            print "Exception e",e
        self.win.endExecute()            
    def btnCancel_clicked( self, oActionEvent ):
        self.win.endExecute()

if __name__<>"package" and __name__=="__main__":
    AddImage()
elif __name__=="package":
    g_ImplementationHelper.addImplementation( AddImage, "org.openoffice.openerp.report.addimage", ("com.sun.star.task.Job",),)
