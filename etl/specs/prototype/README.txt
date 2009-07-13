Prototypes for the ETL system
=============================


Notes on the prototype
~~~~~~~~~~~~~~~~~~~~~~

The prototype prooved it's quite easy and fast to develop a complete ETL.
It takes about 15 lines per simple connector to develop. The whole prototype
including the framework and the connectors takes 150 lines, including the
following connectors:
* CSV input, csv output, data logger, data logger in one block
* Sort, diff, merge

The concept used by the prototype:
* Channel: name of transition used by connector to read/write
    for example, the diff connector read two channels (original, modified)
    and write to four channels: same, added, removed, updated

Summary of improvements to apply
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Don't put the logic in the node but in the job execution. That's the job
that should schedule the node function calls. And not the node itself.
OK - DONE

* Add a system of triggering/listening events. Some events can be raised by
default: start, stop, end, error. Others can be user defined.

* Add different kinds of transitions. We implemented the data transition, we
will have to add the event/signal transition. Transition that are triggered
when receiving a particular event from original node.

* Use a class to store the data, not a simple dict. We should be able to put
meta information on this class, so that information is transfered from one node
to another. The class should also store the metadata of the current
information.  (the list of fields and their type)
OK - SHOULD NOT BE DONE !

* Currently, I am passing the same data structure to all channels. It's efficient,
but when we split from one node to two, we have two pointers to the same data.
So if one node change data, it's also changed in the splitted branch. On the
transition, we should be allowed to decide if we copy() or not the data.
After Remark: we keep like that but we implement a fork() node that copy data
into several different outgoing transition.

* Change the run execution on jobs and nodes so that it process one element at
a time and not the complete flow of elements. So that the job execution can decide
to stop running, run one element at a time to trace, or run until it's finnished.
I think using 'yield' function in python could be a good idea.
OK - DONE

* If you send an empty data to output, it does not go to input of the relateds
nodes. So that we have a system to manage loops and recursivity.
OK - DONE

* Create a new node type which is sub-job or sub-process. It calls a new process.

* Each component can send signals. Trigger Transitions can listen to these signals
and launch new components of type input (sub-jobs, csv.in). Signals are automatically
generated:
   - start : When the component starts
   - start_input : At the first row received by the component
   - start_output : At the first row send by the component
   - no_input : At the end of the process, if no data received
   - stop : when the component is set as pause
   - continue : when the component restart after a pause
   - end : When the component finnished is process

* All components should inherit from a etl.statitic class. This class computes
  basic statistics ans return them at the end of the process like data in a
  channel called "statistics":
    Input Channel | # of Records | Time To Process | Time/Record | Memory Usage
    main          | 1244         | 123 sec         | 0.1 sec     | 1Mb
    other         | 144          | 12 sec          | 0.1 sec     | 1Mb

Questions
~~~~~~~~~

* What's the best solution to store the data ? a list of dict is easy but may
take some place in memory. Is it better to use a list of lists ? We should
evaluate the difference in memory occupation. If it's less than 50%, we keep
list of dict. For now on, let's start with a list of dict.
OK - DONE We don't maintain list of dicts, we maintain iterators of dict

* I didn't thought about code generation to build a processor that will convert
the data. Is this really usefull ? Why is Talend providing this ? I think code
generation is stupid. A static engine that uses a data file explaining how to
parse data is more interresting.
If needed, we can isolate the ETL processor so that it works outside Open ERP
for the process. And, if we need a gui, then we use Open ERP. May be the easiest
is this: develop a standalone ETL application (like this proto), use Open ERP
to automatically instanciate objects for this ETL. Open ERP is able to store
in pickle the instanciated objects so that another engine just have to load
these objects and use the standalone lib to process data, being Open ERP
independant.

Time Line
~~~~~~~~~

1. Finnish requirements (Deadline: 15/01) - assigned to hmo
 * Prototype (done)
 * All menus (done)
 * All screens
 * List of components to develop
 * Review by third-party

2. Development (Deadline: 29/01) - assigned to trainee
 * Improve the current prototype, integrating the above notes

3. Develop real use cases (Deadline: 15/03)
     (assigned to trainee)
 * SugarCRM -> Open ERP
 * Outlook -> Open ERP
Implement what's missing to integrate these usecases as modules.

4. Development of the Open ERP interface (Deadline: 22/02)
 * Implement all objects/menus/views in Open ERP
 * etl addons: Once all views are designed, implement the logic, using etl
     module (assigned to trainee)
 * eTiny: generalisation of the workflow editor to create a new type of view
     (assigned to noz, sana or ame)

5. Full integrator documentation, 200 pages (Deadline: 31/03)
     (assigned to trainee)
 * In english

Project Manager: hmo

Standalone ETL Application
~~~~~~~~~~~~~~~~~~~~~~~~~~

We should do two teams:
1. Standalone ETL application
2. GUI using Open ERP web client

The first one dedicates to create a standalone ETL application using Python.
This should be similar to the provided prototype which is already standalone.
This should be a python library.

The second one creates a Gui that uses this lib to define and instanciate jobs.
It instanciates the objects in memory based on Open ERP datas in the database.

So that we can use the ETL as a standalone application or as a part of Open ERP.
We should find a way to connect the ETL's results to Open ERP applications.

The Open ERP application should be able to save in a pickle a full project.
So that it can be run latter by the standalone application.

The Process
~~~~~~~~~~~

1. Run

First, the job process calls run on each starting node.

The run calls:
* start()
* input()
* stop()

2. Start

The start calls all start of related nodes through outgoing transitions.

3. Input

Then, the run call input with the data it reads from sources (csv, sql).

The input process the data and calls output on resulting data, on a dedicated
channel.  None channel means all channels.

The output calls input on related transitions with the data to related
nodes through outgoing transitions and channels.

4. The stop

The stop ends the process.

When all related nodes through incoming transistions have stopped, the current
node stops and propagate the stop call.



List of tests in the prototype
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

test.py
-------

data/partner.csv -> sort(name) -> output/partner.csv
                               -> logger

test2.py
--------

data/partner.csv
    -> log('PartnerLogger')
        -> output/partner.csv
            -> log('OutputLogger')

test3.py
--------

data/partner.csv
    -> log('PartnerLogger')
        -> sort('name')
            -> output/partner.csv
                -> log('OutputLogger')

diff.py
-------

First Job:
* Perform a diff between partner.csv and partner2.csv and store
   - intermediate/add.csv : added records
   - intermediate/remove.csv : removed records
   - intermediate/update.csv : updated records

data/partner.csv
data/partner2.csv
    -> diff()
       - csv.output(intermediate/add.csv)
       - csv.output(intermediate/remove.csv)
       - csv.output(intermediate/update.csv)

Second Job:
* Apply on partner3.csv to produce output/partner3.csv
   - add records from intermediate/add.csv
   - del records from intermediate/remove.csv (not yet implemented)
   - update records from intermediate/update.csv (not yet implemented)

data/partner3.csv
    -> merge(intermediate/add.csv)
        -> filter(intermediate/remove.csv)
            -> update(intermediate/update.csv)


Reusing another ETL
-------------------

> Why developping an ETL from scratch instead of developping connectors for an
> existing open source ETL ?

Our biggest motivation about an ETL development is to be able to capitalize
every integration with another application made on Open ERP. (for example,
as an easy reuseable and out-of-the-box module). So that, once we made
an application, we can reuse simply by installing a module.  To do so, we need
a system that is used by all Open ERP partners.

I don't think Talend will fit because:

* We can not ask partners to learn a new technology for importing data. Some
will follow, others not. It costs a lot to invest on a new technology. And I
think Talend is complex. If we want efficient results and contributions, we
should provide a system that everyone follows. We have several integrations per
month: connectors will be developped quite quickly.

* My first goal is packaging for end-users and re-useability. Having something
as Open ERP module is perfect for this. A user just have to install the
outlook_import plugin and run a simple wizard.

More over, on the technical part:

* I think we will take less time to redevelop a full ETL than to develop
OpenObject connectors for Talend. Mostly because we just have to develop the
ETL kernel and components (20 is enough for most jobs) and the rest is already
available from the ERP kernel: access rights, web-service interface, job editor,
forms and lists, migration of jobs, etc. The estimated time for the first
useable version of the ETL (without the interface) is between 2 and 3 weeks.

* The maintenance (evolution of Open ERP's version) will be hard with Talend
and nearly 0 per new version with Open ERP.

* I read the way Talend is developped and it seems like a "usine à gaz".
I think we will have much better results, either after a few weeks. Having a
script language, non typed and object is very good for an ETL. We have big
changes in mind that will simplify the way you design jobs:
  - don't describe the interface, just describe the changes
      -> MUCH MORE flexible.
      -> MUCH LESS work for integration
      -> AVOID to describe connectors for every object/table
      -> COMPATIBLE with the modularity and flexibility of Open ERP
         (objects may be very different based on the modules you install)
  - ability to easily reuse. (like you pointed, db connections)
  - use introspection everywhere (to detect Open ERP connectors on the fly based
    on SQL introspection, Open ERP fields-view_get, CSV headers, ...) And don't
    store and describe schema, unless you explictly need a validation. In this case
    you describe only the part you want to validate.

* I think that developping a component, in a good etl, should not take more than
a few hours. It's not the case with current Open Source ETL.

* ETL is like BI, having an integrated ETL offers a new dimension of possibility
for the ERP: for example, we decided that, for our direct marketing module, a
segmentation of customers for a campaign is defined by an ETL job.

But, we don't plan to try to compete with Talend:
* We will not implement high-end-user interfaces. For example, we do not plan
to develop a SQL query designer. Users will have to write their SQL queries by
themselves. (at least at the beginning)

PULL instead of PUSH
--------------------

An ETL component read flows of data in input, process and push this flow of data
to outputs. But sometimes it's more interresting to pull data instead of pushing
it. (an inverted flow or part of a flow) In this situation, a flow request specific
data (invert the processing direction) instead of waiting data to process.
Most of the time, if you want to join two flows of data, it's easier and more efficient
to use PUSH on the main flow and pull on secondary flows so that it can request only
waht he needs. That's what most developpers do when they develop migration scripts
by themselves.

I will try to write some usecases.

Business Connectors
-------------------

> For Open Object, we should provide business connectors (Partners V4.2, products V5...)

I don't think we will need this. I put an introspection button on the Open Object
connector that loads the schema and constraints automatically. Based on the note above
(we don't describe all data, only the changes we want to apply), it will be very
flexible most connectors will easily work together without performing operations.

Having said that, in most of the case, this flow will work with the same
connectors for OutlookToOpenERP, and Open ERP.
	Outlook 2003 -> OutlookTOOpenERP -> Open ERP
	Outlook 2007 -> OutlookTOOpenERP -> Open ERP
So we just have to provide different connectors if needed.

Of course, if needed for complex objects that changed too much between versions, we
will provide connectors.

But if such components are needed, it's not component to develop, it's just a
parametrization (of components or part of jobs) saved as a module. So anybody
could easily change it.

File & DB access
----------------

For files, we will use URL lib that support most protocols: webdav, ftp, http, etc.
For DB Access, we will use SQLAlchemy that support most relationnal DB.

So, with only 2 components, we will manage most input connectors. Python libraries
exists for lots of format of files (DBF, XLS, ...) so it will be quite easy to develop
these connectors: from 5 to 20 lines of Python :)

Note that we plan to dissociate server connection connectors and file input connections.
So that you can use the server connection connector to retrieve a file through any
protocol (HTTP, FTP, ...) and connect a file input process on this one after (DBF, CSV).

Everything as object
--------------------

I agree with you. Every data should be an object and every field also. For example,
dates will be mx.DateTime objects (that already support all kind of operations)
and string will be unicode objects.

Toolbox
-------

I don't have a clear vision of what you call Toolbox. May be we should discuss on this.
But, in my opinion, Python is a very good toolbox in itself. Really easy
scripting language and lots of available functions or libraries. Managing
transformations in Python is really easy.

Naming convention
-----------------

Yes, we should NOT use terms like Talend. Any proposition for a better term for
'component' ?

Dependency with Open ERP
------------------------

There will be no dependency with Open ERP !

We plan to develop a fully independant python library called etl. So that, any
python application can use it. This library manages all components and jobs
processes but has no gui.

Then, we will develop an etl module on Open ERP that provides the GUI to easily
define components and jobs. Means you can use it from the GUI or directly in
Python. The Open ERP module will save the defined jobs/components (like pickle
that includes all etl object). So that you can use the system with only the etl
library, without having to install Open ERP.

I don't like code generation tools at all. This approach is much more efficient and
request less effort in the development of components.

So you have:
* Development/Testing environment: Open ERP
* Deployment on Production: fully independant, only need to install a python etl lib


