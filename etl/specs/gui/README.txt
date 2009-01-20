Job Edition
-----------

The changes
~~~~~~~~~~~

sc_after.png : After modifications to generic diagram view
sc_before.png : Current workflow editor view (specific to workflow)

I think the palet of available nodes must be in tree, not in simple icons.

Details
~~~~~~~

We will implement a new kind of view in Open ERP of type diagram:

We will change the workflow editor of eTiny, so that it becomes a
generic new type of view (diagram) that can be applied on any object. For
example, the workflow editor should be the following view on the object
workflow.workflow:

<diagram string="Workflow Editor">
	<node object="workflow.activity">
		<field name="name"/>
	</node>
	<arrow object="workflow.transition" source="activity_from" destination="activity_to">
		<field name="name"/>
	</arrow>
</diagram>

So that we can edit everything as a graph:
* Developing an ETL application,
* Workflow Editor,
* Marketing Campaigns (with decisions/actions),
* Product's routing in the warehouse, ...
* Partners relations,

For the need of ETL, we will also improve it, so that:
* you can have different layout on nodes:
	a field that return SQUARE, CIRCLE, OVAL, SQUARE_ROUND, CUSTOM_PIXMAP
* background on node: a field that return the background color
* Bakcground on transitions
* Label on transitions

So that we can have very graphical tools.

This should be planified for just after v5. May be you should already assign
one of the new trainee on this, that works on a dedicated branch?  It must also
be able to render tree instead of diagram.

We should also think about how we display the switch view icons as, in a near
future, we will have at least 7 different views on each object !

We need a palet of different objects on the left that all inherits from the
same node object. So that we can mix between objects in one diagram.

On the left, the available components should be presented as a list or
a tree of available objects. (instead of icons like presented in the
screenshot)
