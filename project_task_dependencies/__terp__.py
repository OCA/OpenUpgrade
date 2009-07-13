{
	"name" : "ChriCar Task Dependencies",
	"version" : "0.1",
	"author"  : "ChriCar Beteiligungs und Beratungs GmbH" ,
	"website" : "http://www.chricar.at/ChriCar",
        "description"  : """This module adds dependencies between tasks 
         and recalculates the sequence numbers, which are used 
         * to print the Gantt graph
         * to order the tasks
	 Be ware
	 * sequence.sql has to be installed MANUALLY !!
     * Do not add more then ONE Leading or dependant task at once 
       - One by one with commit between works
	 """,
	"category" : "Generic Modules/Others",
	"depends" : ["base","project"],
	"init_xml" : [],
	"demo_xml" : ["chricar_task_dependencies_demo.xml"],
	"update_xml" : ["chricar_task_dependencies_view.xml"],
	"active": False,
	"installable": True
}
