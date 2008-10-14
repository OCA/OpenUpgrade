LiveChat Module
===============

Introduction
------------

The goal is to allow visitors to communicate with our salesman from our website.
There are 2 componants:
* The Tiny ERP module
* A web application

The configuration is managed by the Tiny ERP module. The communication is made
between the web application (that uses the python-jabber library) and the jabber
account of the user. The communication between the web application and the tiny
erp server is done through xmlrpc.

The Tiny ERP module manages:
* configuration of jabber accounts
* assignation of jabber accounts

The web application manages:
* the interface for displaying / writting messages
* the jabber communication with the client

When a visitor wants to talk, the system:
* calls the server to get:
** an available user jabber account
** an available visitor jabber account
** a session ID

He gets ID's of jabber accounts. He can call get_configuration on a session to 
get information about jabber accounts corresponding to these id's.

When the visitors stop the communication, he has to close the session using the session_id.

Status
------

The tiny erp module is nearly finnished. (written but untested)
The web application has not started yet.

Example
-------

http://www.rackspace.co.uk/
Click on Start a live chat.

Presentation
------------

Here is how it works:
* You define sessions for each website you want to use this module on
* A session contains:
** A list of jabber accounts for visitors
** A list of jabber accounts for users

You can only have one visitor on a visitor jabber account.
You can have several visitors that talks to the same user, up to the max_per_user value.

The web application calls start_session when a user wants to log in.
When the user logsout, it calls stop_session and send the history of the communication
to the Tiny ERP server.



Phase 2
=======

Languages Support
-----------------

Be able to route to some particular users according to the browser language.

Page Filter
-----------

Filter on the referrer.

Actions
-------

When it's working, we will implement actions that the user can do in his jabber to perform
actions at the web application side. Examples:

/redirect jabber@address.com
/close

