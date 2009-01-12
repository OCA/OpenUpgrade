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

* Add a system of triggering/listening events. Some events can be raised by
default: start, stop, end, error. Others can be user defined.

* Add different kinds of transitions. We implemented the data transition, we
will have to add the event/signal transition. Transition that are triggered
when receiving a particular event from original node.

* Use a class to store the data, not a simple dict. We should be able to put
meta information on this class, so that information is transfered from one node
to another. The class should also store the metadata of the current
information.  (the list of fields and their type)

* Currently, I am passing the same data structure to all channels. It's efficient,
but when we split from one node to two, we have two pointers to the same data.
So if one node change data, it's also changed in the splitted branch. On the
transition, we should be allowed to decide if we copy() or not the data.

* Change the run execution on jobs and nodes so that it process one element at
a time and not the complete flow of elements. So that the job execution can decide
to stop running, run one element at a time to trace, or run until it's finnished.

* If you send an empty data to output, it does not go to input of the relateds
nodes. So that we have a system to manage loops and recursivity.

* Create a new node type which is sub-job or sub-process. It calls a new process.

* I implemented a push mechanism, we should also add a pull mechanism: a node
can request information to another node, and then receive the requested result.
This is not existent in most common ETL's so we have to design something smart.


Questions
~~~~~~~~~

* What's the best solution to store the data ? a list of dict is easy but may
take some place in memory. Is it better to use a list of lists ? We should
evaluate the difference in memory occupation. If it's less than 50%, we keep
list of dict.

Time Line
~~~~~~~~~

1. Finnish requirements (Deadline: 15/01) - assigned to hmo
 * Prototype (done)
 * All menus
 * All screens
 * List of components to develop
 * Review by third-party

2. Development (Deadline: 29/01) - assigned to trainee
 * Implement all objects/menus/views in Open ERP
 * Improve the current prototype, integrating the above notes

3. Development of the Open ERP interface (Deadline: 22/02)
 * eTiny: generalisation of the workflow editor to create a new type of view
     (assigned to noz, sana or ame)
 * etl addons: Integrate prototype logic on Open ERP objects
     (assigned to trainee)

4. Develop real use cases (Deadline: 15/03)
     (assigned to trainee)
 * Sage -> Open ERP
 * Tally -> Open ERP
 * SugarCRM -> Open ERP
Implement what's missing to integrate these usecases as modules.

5. Full integrator documentation, 200 pages (Deadline: 31/03)
     (assigned to trainee)
 * In english

Project Manager: hmo

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

