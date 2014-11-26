/*
This software is allowed to use under GPL or you need to obtain Commercial or Enterise License
to use it in non-GPL project. Please contact sales@dhtmlx.com for details
*/
scheduler._props = {};
scheduler.createUnitsView=function(name,property,list,size,step,skip_incorrect){
	if (typeof name == "object"){
		list = name.list;
		property = name.property;
		size = name.size||0;
		step = name.step||1;
		skip_incorrect = name.skip_incorrect;
		name = name.name;		
	}

	scheduler._props[name]={map_to:property, options:list, step:step, position:0 };
    if(size>scheduler._props[name].options.length){
        scheduler._props[name]._original_size = size;
        size = 0;
    }
    scheduler._props[name].size = size;
	scheduler._props[name].skip_incorrect = skip_incorrect||false;
	
	scheduler.date[name+"_start"]= scheduler.date.day_start;
	scheduler.templates[name+"_date"] = function(date){
		return scheduler.templates.day_date(date);
	};
	
	scheduler.templates[name+"_scale_date"] = function(date){
		var list = scheduler._props[name].options;
		if (!list.length) return "";
		var index = (scheduler._props[name].position||0)+Math.floor((scheduler._correct_shift(date.valueOf(),1)-scheduler._min_date.valueOf())/(60*60*24*1000));
		if (list[index].css) 
			return "<span class='"+list[index].css+"'>"+list[index].label+"</span>";
		else
			return list[index].label;
	};

	scheduler.date["add_"+name]=function(date,inc){ return scheduler.date.add(date,inc,"day"); };
	scheduler.date["get_"+name+"_end"]=function(date){
		return scheduler.date.add(date,scheduler._props[name].size||scheduler._props[name].options.length,"day");
	};
	
	scheduler.attachEvent("onOptionsLoad",function(){
        var pr = scheduler._props[name];
		var order = pr.order = {};
		var list = pr.options;
		for(var i=0; i<list.length;i++)
			order[list[i].key]=i;
        if(pr._original_size && pr.size==0){
            pr.size = pr._original_size;
            delete pr.original_size;
        }
		if(pr.size > list.length) {
            pr._original_size = pr.size;
            pr.size = 0;
        }
        else
            pr.size = pr._original_size||pr.size;
		if (scheduler._date && scheduler._mode == name) 
			scheduler.setCurrentView(scheduler._date, scheduler._mode);
	});
	scheduler.callEvent("onOptionsLoad",[]);
};
scheduler.scrollUnit=function(step){
	var pr = scheduler._props[this._mode];
	if (pr){
		pr.position=Math.min(Math.max(0,pr.position+step),pr.options.length-pr.size);
		this.update_view();		
	}
};
(function(){
	var _removeIncorrectEvents = function(evs) {
		var pr = scheduler._props[scheduler._mode];
		if(pr && pr.order && pr.skip_incorrect) {
            var correct_events = [];
			for(var i=0; i<evs.length; i++) {
				if(typeof pr.order[evs[i][pr.map_to]] != "undefined") {
                    correct_events.push(evs[i]);
				}
			}
            evs.splice(0,evs.length);
			evs.push.apply(evs,correct_events);
		}
		return evs;
	};
	var old_pre_render_events_table = scheduler._pre_render_events_table;
	scheduler._pre_render_events_table=function(evs,hold) {
		evs = _removeIncorrectEvents(evs);
		return old_pre_render_events_table.apply(this, [evs, hold]);
	};
	var old_pre_render_events_line = scheduler._pre_render_events_line;
	scheduler._pre_render_events_line = function(evs,hold){ 
		evs = _removeIncorrectEvents(evs);
		return old_pre_render_events_line.apply(this, [evs, hold]);
	};
	var fix_und=function(pr,ev){
		if (pr && typeof pr.order[ev[pr.map_to]] == "undefined"){
			var s = scheduler;
			var dx = 24*60*60*1000;
			var ind = Math.floor((ev.end_date - s._min_date)/dx);
			//ev.end_date = new Date(s.date.time_part(ev.end_date)*1000+s._min_date.valueOf());
			//ev.start_date = new Date(s.date.time_part(ev.start_date)*1000+s._min_date.valueOf());
			ev[pr.map_to] = pr.options[Math.min(ind+pr.position,pr.options.length-1)].key;
			return true;
		}
	};
	var t = scheduler._reset_scale;
    
	var oldive = scheduler.is_visible_events;
	scheduler.is_visible_events = function(e){
		var res = oldive.apply(this,arguments);
		if (res){
			var pr = scheduler._props[this._mode];
			if (pr && pr.size){
				var val = pr.order[e[pr.map_to]];
				if (val < pr.position || val >= pr.size+pr.position )
					return false;
			}
		}
		return res;
	};
	scheduler._reset_scale = function(){
		var pr = scheduler._props[this._mode];
		var ret = t.apply(this,arguments);
		if (pr){
			this._max_date=this.date.add(this._min_date,1,"day");
				
				var d = this._els["dhx_cal_data"][0].childNodes;
				for (var i=0; i < d.length; i++)
					d[i].className = d[i].className.replace("_now",""); //clear now class
				
			if (pr.size && pr.size < pr.options.length){
				
				var h = this._els["dhx_cal_header"][0];
				var arrow = document.createElement("DIV");				
				if (pr.position){
					arrow.className = "dhx_cal_prev_button";
					arrow.style.cssText="left:1px;top:2px;position:absolute;"
					arrow.innerHTML = "&nbsp;"				
					h.firstChild.appendChild(arrow);
					arrow.onclick=function(){
						scheduler.scrollUnit(pr.step*-1);
					}
				}
				if (pr.position+pr.size<pr.options.length){
					arrow = document.createElement("DIV");
					arrow.className = "dhx_cal_next_button";
					arrow.style.cssText="left:auto; right:0px;top:2px;position:absolute;"
					arrow.innerHTML = "&nbsp;"		
					h.lastChild.appendChild(arrow);
					arrow.onclick=function(){
						scheduler.scrollUnit(pr.step);
					}
				}
			}
		}
		return ret;
		
	};
	var r = scheduler._get_event_sday;
	scheduler._get_event_sday=function(ev){
		var pr = scheduler._props[this._mode];
		if (pr){
			fix_und(pr,ev);
			return pr.order[ev[pr.map_to]]-pr.position;	
		}
		return r.call(this,ev);
	};
	var l = scheduler.locate_holder_day;
	scheduler.locate_holder_day=function(a,b,ev){
		var pr = scheduler._props[this._mode];
		if (pr && ev) {
			fix_und(pr,ev);
			return pr.order[ev[pr.map_to]]*1+(b?1:0)-pr.position;	
		}
		return l.apply(this,arguments);
	};
	var p = scheduler._mouse_coords;
	scheduler._mouse_coords=function(){
		var pr = scheduler._props[this._mode];
		var pos=p.apply(this,arguments);
		if (pr){
			if(!this._drag_event) this._drag_event = {};
			var ev = this._drag_event;
			if (this._drag_id && this._drag_mode){
				ev = this.getEvent(this._drag_id);
				this._drag_event._dhx_changed = true;
			}
			var unit_ind = Math.min(pos.x+pr.position,pr.options.length-1);
			var key = pr.map_to;
			pos.section = ev[key]=pr.options[unit_ind].key;
			pos.x = 0;
		}
		return pos;
	};
	var o = scheduler._time_order;
	scheduler._time_order = function(evs){
		var pr = scheduler._props[this._mode];
		if (pr){
			evs.sort(function(a,b){
				return pr.order[a[pr.map_to]]>pr.order[b[pr.map_to]]?1:-1;
			});
		} else
			o.apply(this,arguments);
	};
	scheduler.attachEvent("onEventAdded",function(id,ev){
		if (this._loading) return true;
		for (var a in scheduler._props){
			var pr = scheduler._props[a];
			if (typeof ev[pr.map_to] == "undefined")
				ev[pr.map_to] = pr.options[0].key;
		}
		return true;
	});
	scheduler.attachEvent("onEventCreated",function(id,n_ev){
		var pr = scheduler._props[this._mode];
		if (pr && n_ev){
			var ev = this.getEvent(id);
			this._mouse_coords(n_ev);
			fix_und(pr,ev);
			this.event_updated(ev);
		}
		return true;
	})		
})();
