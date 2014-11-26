/*
This software is allowed to use under GPL or you need to obtain Commercial or Enterise License
to use it in non-GPL project. Please contact sales@dhtmlx.com for details
*/

scheduler.config.occurrence_timestamp_in_utc = false;
scheduler.form_blocks["recurring"] = {
	render:function(sns) {
		return scheduler.__recurring_template;
	},
	_ds: {},
	_init_set_value:function(node, value, ev) {
		scheduler.form_blocks["recurring"]._ds = {start:ev.start_date, end:ev._end_date};

		var str_date_format = scheduler.date.str_to_date(scheduler.config.repeat_date);
		var str_date = function(str_date) {
			var date = str_date_format(str_date);
			if (scheduler.config.include_end_by)
				date = scheduler.date.add(date, 1, 'day');
			return date;
		};

		var date_str = scheduler.date.date_to_str(scheduler.config.repeat_date);

		var top = node.getElementsByTagName("FORM")[0];
		var els = [];

		function register_els(inps) {
			for (var i = 0; i < inps.length; i++) {
				var inp = inps[i];
				if (inp.type == "checkbox" || inp.type == "radio") {
					if (!els[inp.name])
						els[inp.name] = [];
					els[inp.name].push(inp);
				} else
					els[inp.name] = inp;
			}
		}

		register_els(top.getElementsByTagName("INPUT"));
		register_els(top.getElementsByTagName("SELECT"));

		if (!scheduler.config.repeat_date_of_end) {
			var formatter = scheduler.date.date_to_str(scheduler.config.repeat_date);
			scheduler.config.repeat_date_of_end = formatter(scheduler.date.add(new Date(), 30, "day"));
		}
		els["date_of_end"].value = scheduler.config.repeat_date_of_end;

		var $ = function(a) {
			return document.getElementById(a);
		};

		function get_radio_value(name) {
			var col = els[name];
			for (var i = 0; i < col.length; i++)
				if (col[i].checked) return col[i].value;
		}

		function change_current_view() {
			$("dhx_repeat_day").style.display = "none";
			$("dhx_repeat_week").style.display = "none";
			$("dhx_repeat_month").style.display = "none";
			$("dhx_repeat_year").style.display = "none";
			$("dhx_repeat_" + this.value).style.display = "block";
		}

		function get_repeat_code(dates) {
			var code = [get_radio_value("repeat")];
			get_rcode[code[0]](code, dates);

			while (code.length < 5) code.push("");
			var repeat = "";
			if (els["end"][0].checked) {
				dates.end = new Date(9999, 1, 1);
				repeat = "no";
			}
			else if (els["end"][2].checked) {
				dates.end = str_date(els["date_of_end"].value);
			}
			else {
				scheduler.transpose_type(code.join("_"));
				repeat = Math.max(1, els["occurences_count"].value);
				var transp = ((code[0] == "week" && code[4] && code[4].toString().indexOf(scheduler.config.start_on_monday ? 1 : 0) == -1) ? 1 : 0);
				dates.end = scheduler.date.add(new Date(dates.start), repeat + transp, code.join("_"));
			}

			return code.join("_") + "#" + repeat;
		}

		scheduler.form_blocks["recurring"]._get_repeat_code = get_repeat_code;
		var get_rcode = {
			month:function(code, dates) {
				if (get_radio_value("month_type") == "d") {
					code.push(Math.max(1, els["month_count"].value));
					dates.start.setDate(els["month_day"].value);
				} else {
					code.push(Math.max(1, els["month_count2"].value));
					code.push(els["month_day2"].value);
					code.push(Math.max(1, els["month_week2"].value));
					dates.start.setDate(1);
				}
				dates._start = true;
			},
			week:function(code, dates) {
				code.push(Math.max(1, els["week_count"].value));
				code.push("");
				code.push("");
				var t = [];
				var col = els["week_day"];
				for (var i = 0; i < col.length; i++) {
					if (col[i].checked) t.push(col[i].value);
				}
				if (!t.length)
					t.push(dates.start.getDay());

				dates.start = scheduler.date.week_start(dates.start);
				dates._start = true;

				code.push(t.sort().join(","));
			},
			day:function(code) {
				if (get_radio_value("day_type") == "d") {
					code.push(Math.max(1, els["day_count"].value));
				}
				else {
					code.push("week");
					code.push(1);
					code.push("");
					code.push("");
					code.push("1,2,3,4,5");
					code.splice(0, 1);
				}
			},
			year:function(code, dates) {
				if (get_radio_value("year_type") == "d") {
					code.push("1");
					dates.start.setMonth(0);
					dates.start.setDate(els["year_day"].value);
					dates.start.setMonth(els["year_month"].value);

				} else {
					code.push("1");
					code.push(els["year_day2"].value);
					code.push(els["year_week2"].value);
					dates.start.setDate(1);
					dates.start.setMonth(els["year_month2"].value);
				}
				dates._start = true;
			}
		};
		var set_rcode = {
			week:function(code, dates) {
				els["week_count"].value = code[1];
				var col = els["week_day"];
				var t = code[4].split(",");
				var d = {};
				for (var i = 0; i < t.length; i++) d[t[i]] = true;
				for (var i = 0; i < col.length; i++)
					col[i].checked = (!!d[col[i].value]);
			},
			month:function(code, dates) {
				if (code[2] == "") {
					els["month_type"][0].checked = true;
					els["month_count"].value = code[1];
					els["month_day"].value = dates.start.getDate();
				} else {
					els["month_type"][1].checked = true;
					els["month_count2"].value = code[1];
					els["month_week2"].value = code[3];
					els["month_day2"].value = code[2];
				}
			},
			day:function(code, dates) {
				els["day_type"][0].checked = true;
				els["day_count"].value = code[1];
			},
			year:function(code, dates) {
				if (code[2] == "") {
					els["year_type"][0].checked = true;
					els["year_day"].value = dates.start.getDate();
					els["year_month"].value = dates.start.getMonth();
				} else {
					els["year_type"][1].checked = true;
					els["year_week2"].value = code[3];
					els["year_day2"].value = code[2];
					els["year_month2"].value = dates.start.getMonth();
				}
			}
		};

		function set_repeat_code(code, dates) {
			var data = code.split("#");
			code = data[0].split("_");
			set_rcode[code[0]](code, dates);
			var e = els["repeat"][({day:0, week:1, month:2, year:3})[code[0]]];
			switch (data[1]) {
				case "no":
					els["end"][0].checked = true;
					break;
				case "":
					els["end"][2].checked = true;
					els["date_of_end"].value = date_str(dates.end);
					break;
				default:
					els["end"][1].checked = true;
					els["occurences_count"].value = data[1];
					break;
			}

			e.checked = true;
			e.onclick();
		}

		scheduler.form_blocks["recurring"]._set_repeat_code = set_repeat_code;

		for (var i = 0; i < top.elements.length; i++) {
			var el = top.elements[i];
			switch (el.name) {
				case "repeat":
					el.onclick = change_current_view;
					break;
			}
		}
		scheduler._lightbox._rec_init_done = true;
	},
	set_value:function(node, value, ev) {
		var rf = scheduler.form_blocks["recurring"];
		if (!scheduler._lightbox._rec_init_done)
			rf._init_set_value(node, value, ev);
		node.open = !ev.rec_type;
		if (ev.event_pid && ev.event_pid != "0")
			node.blocked = true;
		else node.blocked = false;

		var ds = rf._ds;
		ds.start = ev.start_date;
		ds.end = ev._end_date;

		rf.button_click(0, node.previousSibling.firstChild.firstChild, node, node);
		if (value)
			rf._set_repeat_code(value, ds);
	},
	get_value:function(node, ev) {
		if (node.open) {
			var ds = scheduler.form_blocks["recurring"]._ds;
			var actual_dates = {};
			this.formSection('time').getValue(actual_dates);
			ds.start = actual_dates.start_date;
			ev.rec_type = scheduler.form_blocks["recurring"]._get_repeat_code(ds);
			if (ds._start) {
				ev.start_date = new Date(ds.start);
				ev._start_date = new Date(ds.start);
				ds._start = false;
			} else
				ev._start_date = null;

			ev._end_date = ev.end_date = ds.end;
			ev.rec_pattern = ev.rec_type.split("#")[0];
		} else {
			ev.rec_type = ev.rec_pattern = "";
			ev._end_date = ev.end_date;
		}
		return ev.rec_type;
	},
	focus:function(node) {
	},
	button_click:function(index, el, section, cont) {
		if (!cont.open && !cont.blocked) {
			cont.style.height = "115px";
			el.style.backgroundPosition = "-5px 0px";
			el.nextSibling.innerHTML = scheduler.locale.labels.button_recurring_open;
		} else {
			cont.style.height = "0px";
			el.style.backgroundPosition = "-5px 20px";
			el.nextSibling.innerHTML = scheduler.locale.labels.button_recurring;
		}
		cont.open = !cont.open;

		scheduler.setLightboxSize();
	}
};


//problem may occur if we will have two repeating events in the same moment of time
scheduler._rec_markers = {};
scheduler._rec_markers_pull = {};
scheduler._add_rec_marker = function(ev, time) {
	ev._pid_time = time;
	this._rec_markers[ev.id] = ev;
	if (!this._rec_markers_pull[ev.event_pid]) this._rec_markers_pull[ev.event_pid] = {};
	this._rec_markers_pull[ev.event_pid][time] = ev;
};
scheduler._get_rec_marker = function(time, id) {
	var ch = this._rec_markers_pull[id];
	if (ch) return ch[time];
	return null;
};
scheduler._get_rec_markers = function(id) {
	return (this._rec_markers_pull[id] || []);
};
scheduler._rec_temp = [];
(function() {
	var old_add_event = scheduler.addEvent;
	scheduler.addEvent = function(start_date, end_date, text, id, extra_data) {
		var ev_id = old_add_event.apply(this, arguments);

		if (ev_id) {
			var ev = scheduler.getEvent(ev_id);
			if (ev.event_pid != 0)
				scheduler._add_rec_marker(ev, ev.event_length * 1000);
			if (ev.rec_type)
				ev.rec_pattern = ev.rec_type.split("#")[0];
		}
	};
})();
scheduler.attachEvent("onEventIdChange", function(id, new_id) {
	if (this._ignore_call) return;
	this._ignore_call = true;

	for (var i = 0; i < this._rec_temp.length; i++) {
		var tev = this._rec_temp[i];
		if (tev.event_pid == id) {
			tev.event_pid = new_id;
			this.changeEventId(tev.id, new_id + "#" + tev.id.split("#")[1]);
		}
	}

	delete this._ignore_call;
});
scheduler.attachEvent("onBeforeEventDelete", function(id) {
	var ev = this.getEvent(id);
	if (id.toString().indexOf("#") != -1 || (ev.event_pid && ev.event_pid != "0" && ev.rec_type && ev.rec_type != 'none')) {
		id = id.split("#");
		var nid = this.uid();
		var tid = (id[1]) ? id[1] : (ev._pid_time / 1000);

		var nev = this._copy_event(ev);
		nev.id = nid;
		nev.event_pid = ev.event_pid || id[0];
		var timestamp = tid;
		nev.event_length = timestamp;
		nev.rec_type = nev.rec_pattern = "none";
		this.addEvent(nev);

		this._add_rec_marker(nev, timestamp * 1000);
	} else {
		if (ev.rec_type && this._lightbox_id)
			this._roll_back_dates(ev);
		var sub = this._get_rec_markers(id);
		for (var i in sub) {
			if (sub.hasOwnProperty(i)) {
				id = sub[i].id;
				if (this.getEvent(id))
					this.deleteEvent(id, true);
			}
		}
	}
	return true;
});

scheduler.attachEvent("onEventChanged", function(id) {
	if (this._loading) return true;

	var ev = this.getEvent(id);
	if (id.toString().indexOf("#") != -1) {
		var id = id.split("#");
		var nid = this.uid();
		this._not_render = true;

		var nev = this._copy_event(ev);
		nev.id = nid;
		nev.event_pid = id[0];
		var timestamp = id[1];
		nev.event_length = timestamp;
		nev.rec_type = nev.rec_pattern = "";
		this.addEvent(nev);

		this._not_render = false;
		this._add_rec_marker(nev, timestamp * 1000);
	} else {
		if (ev.rec_type && this._lightbox_id)
			this._roll_back_dates(ev);
		var sub = this._get_rec_markers(id);
		for (var i in sub) {
			if (sub.hasOwnProperty(i)) {
				delete this._rec_markers[sub[i].id];
				this.deleteEvent(sub[i].id, true);
			}
		}
		delete this._rec_markers_pull[id];

		// it's possible that after editing event is no longer exists, in such case we need to remove _select_id flag
		var isEventFound = false;
		for (var k = 0; k < this._rendered.length; k++) {
			if (this._rendered[k].getAttribute('event_id') == id)
				isEventFound = true;
		}
		if (!isEventFound)
			this._select_id = null;
	}
	return true;
});
scheduler.attachEvent("onEventAdded", function(id) {
	if (!this._loading) {
		var ev = this.getEvent(id);
		if (ev.rec_type && !ev.event_length)
			this._roll_back_dates(ev);
	}
	return true;
});
scheduler.attachEvent("onEventSave", function(id, data, is_new_event) {
	var ev = this.getEvent(id);
	if (!ev.rec_type && data.rec_type && (id + '').indexOf('#') == -1)
		this._select_id = null;
	return true;
});
scheduler.attachEvent("onEventCreated", function(id) {
	var ev = this.getEvent(id);
	if (!ev.rec_type)
		ev.rec_type = ev.rec_pattern = ev.event_length = ev.event_pid = "";
	return true;
});
scheduler.attachEvent("onEventCancel", function(id) {
	var ev = this.getEvent(id);
	if (ev.rec_type) {
		this._roll_back_dates(ev);
		// a bit expensive, but we need to be sure that event re-rendered, because view can be corrupted by resize , during edit process
		this.render_view_data();
	}
});
scheduler._roll_back_dates = function(ev) {
	ev.event_length = (ev.end_date.valueOf() - ev.start_date.valueOf()) / 1000;
	ev.end_date = ev._end_date;
	if (ev._start_date) {
		ev.start_date.setMonth(0);
		ev.start_date.setDate(ev._start_date.getDate());
		ev.start_date.setMonth(ev._start_date.getMonth());
		ev.start_date.setFullYear(ev._start_date.getFullYear());

	}
};

scheduler.validId = function(id) {
	return id.toString().indexOf("#") == -1;
};

scheduler.showLightbox_rec = scheduler.showLightbox;
scheduler.showLightbox = function(id) {
	var locale = this.locale;
	var c = scheduler.config.lightbox_recurring;
	var pid = this.getEvent(id).event_pid;
	var isVirtual = (id.toString().indexOf("#") != -1);
	if (isVirtual)
		pid = id.split("#")[0];
	if ( !pid || pid == 0 || ( (!locale.labels.confirm_recurring || c == 'instance') || (c == 'series' && !isVirtual)) ) {
		return this.showLightbox_rec(id); // editing instance or non recurring event
	}
	// show series
	var callback = function() {
		pid = this.getEvent(pid);
		pid._end_date = pid.end_date;
		pid.end_date = new Date(pid.start_date.valueOf() + pid.event_length * 1000);
		return this.showLightbox_rec(pid.id); // editing series
	};
	if (c == 'ask') {
		var that = this;
		dhtmlx.modalbox({
			text: locale.labels.confirm_recurring,
			title: locale.labels.title_confirm_recurring,
			width: "500px",
			position: "middle",
			buttons:[locale.labels.button_edit_series, locale.labels.button_edit_occurrence, locale.labels.icon_cancel],
			callback: function(index) {
				switch(+index) {
					case 0:
						return callback.call(that);
					case 1:
						return that.showLightbox_rec(id);
					case 2:
						return;
				}
			}
		});
	} else {
		callback();
	}

};


scheduler.get_visible_events_rec = scheduler.get_visible_events;
scheduler.get_visible_events = function(only_timed) {
	for (var i = 0; i < this._rec_temp.length; i++)
		delete this._events[this._rec_temp[i].id];
	this._rec_temp = [];

	var stack = this.get_visible_events_rec(only_timed);
	var out = [];
	for (var i = 0; i < stack.length; i++) {
		if (stack[i].rec_type) {
			//deleted element of serie
			if (stack[i].rec_pattern != "none")
				this.repeat_date(stack[i], out);
		}
		else out.push(stack[i]);
	}
	return out;
};


(function() {
	var old = scheduler.is_one_day_event;
	scheduler.is_one_day_event = function(ev) {
		if (ev.rec_type) return true;
		return old.call(this, ev);
	};
	var old_update_event = scheduler.updateEvent;
	scheduler.updateEvent = function(id) {
		var ev = scheduler.getEvent(id);
		if (ev && ev.rec_type && id.toString().indexOf('#') === -1) {
			scheduler.update_view();
		} else {
			old_update_event.call(this, id);
		}
	};
})();

scheduler.transponse_size = {
	day:1, week:7, month:1, year:12
};
scheduler.date.day_week = function(sd, day, week) {
	sd.setDate(1);
	week = (week - 1) * 7;
	var cday = sd.getDay();
	var nday = day * 1 + week - cday + 1;
	sd.setDate(nday <= week ? (nday + 7) : nday);
};
scheduler.transpose_day_week = function(sd, list, cor, size, cor2) {
	var cday = (sd.getDay() || (scheduler.config.start_on_monday ? 7 : 0)) - cor;
	for (var i = 0; i < list.length; i++) {
		if (list[i] > cday)
			return sd.setDate(sd.getDate() + list[i] * 1 - cday - (size ? cor : cor2));
	}
	this.transpose_day_week(sd, list, cor + size, null, cor);
};
scheduler.transpose_type = function(type) {
	var f = "transpose_" + type;
	if (!this.date[f]) {
		var str = type.split("_");
		var day = 60 * 60 * 24 * 1000;
		var gf = "add_" + type;
		var step = this.transponse_size[str[0]] * str[1];

		if (str[0] == "day" || str[0] == "week") {
			var days = null;
			if (str[4]) {
				days = str[4].split(",");
				if (scheduler.config.start_on_monday) {
					for (var i = 0; i < days.length; i++)
						days[i] = (days[i] * 1) || 7;
					days.sort();
				}
			}


			this.date[f] = function(nd, td) {
				var delta = Math.floor((td.valueOf() - nd.valueOf()) / (day * step));
				if (delta > 0)
					nd.setDate(nd.getDate() + delta * step);
				if (days)
					scheduler.transpose_day_week(nd, days, 1, step);
			};
			this.date[gf] = function(sd, inc) {
				var nd = new Date(sd.valueOf());
				if (days) {
					for (var count = 0; count < inc; count++)
						scheduler.transpose_day_week(nd, days, 0, step);
				} else
					nd.setDate(nd.getDate() + inc * step);

				return nd;
			};
		}
		else if (str[0] == "month" || str[0] == "year") {
			this.date[f] = function(nd, td) {
				var delta = Math.ceil(((td.getFullYear() * 12 + td.getMonth() * 1) - (nd.getFullYear() * 12 + nd.getMonth() * 1)) / (step));
				if (delta >= 0)
					nd.setMonth(nd.getMonth() + delta * step);
				if (str[3])
					scheduler.date.day_week(nd, str[2], str[3]);
			};
			this.date[gf] = function(sd, inc) {
				var nd = new Date(sd.valueOf());
				nd.setMonth(nd.getMonth() + inc * step);
				if (str[3])
					scheduler.date.day_week(nd, str[2], str[3]);
				return nd;
			};
		}
	}
};
scheduler.repeat_date = function(ev, stack, non_render, from, to) {

	from = from || this._min_date;
	to = to || this._max_date;

	var td = new Date(ev.start_date.valueOf());

	if (!ev.rec_pattern && ev.rec_type)
		ev.rec_pattern = ev.rec_type.split("#")[0];

	this.transpose_type(ev.rec_pattern);
	scheduler.date["transpose_" + ev.rec_pattern](td, from);
	while (td < ev.start_date || scheduler._fix_daylight_saving_date(td,from,ev,td,new Date(td.valueOf() + ev.event_length * 1000)).valueOf() <= from.valueOf() || td.valueOf() + ev.event_length * 1000 <= from.valueOf())
		td = this.date.add(td, 1, ev.rec_pattern);
	while (td < to && td < ev.end_date) {
		var timestamp = (scheduler.config.occurrence_timestamp_in_utc) ? Date.UTC(td.getFullYear(), td.getMonth(), td.getDate(), td.getHours(), td.getMinutes(), td.getSeconds()) : td.valueOf();
		var ch = this._get_rec_marker(timestamp, ev.id);
		if (!ch) { // unmodified element of series
			var ted = new Date(td.valueOf() + ev.event_length * 1000);
			var copy = this._copy_event(ev);
			//copy._timed = ev._timed;
			copy.text = ev.text;
			copy.start_date = td;
			copy.event_pid = ev.id;
			copy.id = ev.id + "#" + Math.ceil(timestamp / 1000);
			copy.end_date = ted;

			copy.end_date = scheduler._fix_daylight_saving_date(copy.start_date, copy.end_date, ev, td, copy.end_date);

			copy._timed = this.is_one_day_event(copy);

			if (!copy._timed && !this._table_view && !this.config.multi_day) return;
			stack.push(copy);

			if (!non_render) {
				this._events[copy.id] = copy;
				this._rec_temp.push(copy);
			}

		} else
		if (non_render) stack.push(ch);

		td = this.date.add(td, 1, ev.rec_pattern);
	}
};
scheduler._fix_daylight_saving_date = function(start_date, end_date, ev, counter, default_date) {
	var shift = start_date.getTimezoneOffset() - end_date.getTimezoneOffset();
	if (shift) {
		if (shift > 0) {
			// e.g. 24h -> 23h
			return new Date(counter.valueOf() + ev.event_length * 1000 - shift * 60 * 1000);
		}
		else {
			// e.g. 24h -> 25h
			return new Date(end_date.valueOf() - shift * 60 * 1000);
		}
	}
	return new Date(default_date.valueOf());
};
scheduler.getRecDates = function(id, max) {
	var ev = typeof id == "object" ? id : scheduler.getEvent(id);
	var count = 0;
	var result = [];
	max = max || 100;

	var td = new Date(ev.start_date.valueOf());
	var from = new Date(td.valueOf());

	if (!ev.rec_type) {
		return [
			{ start_date: ev.start_date, end_date: ev.end_date }
		];
	}
	if (ev.rec_type == "none") {
		return [];
	}
	this.transpose_type(ev.rec_pattern);
	scheduler.date["transpose_" + ev.rec_pattern](td, from);

	while (td < ev.start_date || (td.valueOf() + ev.event_length * 1000) <= from.valueOf())
		td = this.date.add(td, 1, ev.rec_pattern);
	while (td < ev.end_date) {
		var ch = this._get_rec_marker(td.valueOf(), ev.id);
		var res = true;
		if (!ch) { // unmodified element of series
			var sed = new Date(td);
			var ted = new Date(td.valueOf() + ev.event_length * 1000);

			ted = scheduler._fix_daylight_saving_date(sed, ted, ev, td, ted);

			result.push({start_date:sed, end_date:ted});
		} else {
			(ch.rec_type == "none") ?
					(res = false) :
					result.push({ start_date: ch.start_date, end_date: ch.end_date });
		}
		td = this.date.add(td, 1, ev.rec_pattern);
		if (res) {
			count++;
			if (count == max)
				break;
		}
	}
	return result;
};
scheduler.getEvents = function(from, to) {
	var result = [];
	for (var a in this._events) {
		var ev = this._events[a];
		if (ev && ev.start_date < to && ev.end_date > from) {
			if (ev.rec_pattern) {
				if (ev.rec_pattern == "none") continue;
				var sev = [];
				this.repeat_date(ev, sev, true, from, to);
				for (var i = 0; i < sev.length; i++) {
					// if event is in rec_markers then it will be checked by himself, here need to skip it
					if (!sev[i].rec_pattern && sev[i].start_date < to && sev[i].end_date > from && !this._rec_markers[sev[i].id]) {
						result.push(sev[i]);
					}
				}
			} else if (ev.id.toString().indexOf("#") == -1) { // if it's virtual event we can skip it
				result.push(ev);
			}
		}
	}
	return result;
};

scheduler.config.repeat_date = "%m.%d.%Y";
scheduler.config.lightbox.sections = [
	{name:"description", height:130, map_to:"text", type:"textarea" , focus:true},
	{name:"recurring", type:"recurring", map_to:"rec_type", button:"recurring"},
	{name:"time", height:72, type:"time", map_to:"auto"}
];


//drop secondary attributes
scheduler._copy_dummy = function(ev) {
	var start_date = new Date(this.start_date);
	var end_date = new Date(this.end_date);
	this.start_date = start_date;
	this.end_date = end_date;
	this.event_length = this.event_pid = this.rec_pattern = this.rec_type = null;
};

scheduler.config.include_end_by = false;
scheduler.config.lightbox_recurring = 'ask'; // series, instance
scheduler.__recurring_template='<div class="dhx_form_repeat"> <form> <div class="dhx_repeat_left"> <label><input class="dhx_repeat_radio" type="radio" name="repeat" value="day" />Daily</label><br /> <label><input class="dhx_repeat_radio" type="radio" name="repeat" value="week"/>Weekly</label><br /> <label><input class="dhx_repeat_radio" type="radio" name="repeat" value="month" checked />Monthly</label><br /> <label><input class="dhx_repeat_radio" type="radio" name="repeat" value="year" />Yearly</label> </div> <div class="dhx_repeat_divider"></div> <div class="dhx_repeat_center"> <div style="display:none;" id="dhx_repeat_day"> <label><input class="dhx_repeat_radio" type="radio" name="day_type" value="d"/>Every</label><input class="dhx_repeat_text" type="text" name="day_count" value="1" />day<br /> <label><input class="dhx_repeat_radio" type="radio" name="day_type" checked value="w"/>Every workday</label> </div> <div style="display:none;" id="dhx_repeat_week"> Repeat every<input class="dhx_repeat_text" type="text" name="week_count" value="1" />week next days:<br /> <table class="dhx_repeat_days"> <tr> <td> <label><input class="dhx_repeat_checkbox" type="checkbox" name="week_day" value="1" />Monday</label><br /> <label><input class="dhx_repeat_checkbox" type="checkbox" name="week_day" value="4" />Thursday</label> </td> <td> <label><input class="dhx_repeat_checkbox" type="checkbox" name="week_day" value="2" />Tuesday</label><br /> <label><input class="dhx_repeat_checkbox" type="checkbox" name="week_day" value="5" />Friday</label> </td> <td> <label><input class="dhx_repeat_checkbox" type="checkbox" name="week_day" value="3" />Wednesday</label><br /> <label><input class="dhx_repeat_checkbox" type="checkbox" name="week_day" value="6" />Saturday</label> </td> <td> <label><input class="dhx_repeat_checkbox" type="checkbox" name="week_day" value="0" />Sunday</label><br /><br /> </td> </tr> </table> </div> <div id="dhx_repeat_month"> <label><input class="dhx_repeat_radio" type="radio" name="month_type" value="d"/>Repeat</label><input class="dhx_repeat_text" type="text" name="month_day" value="1" />day every<input class="dhx_repeat_text" type="text" name="month_count" value="1" />month<br /> <label><input class="dhx_repeat_radio" type="radio" name="month_type" checked value="w"/>On</label><input class="dhx_repeat_text" type="text" name="month_week2" value="1" /><select name="month_day2"><option value="1" selected >Monday<option value="2">Tuesday<option value="3">Wednesday<option value="4">Thursday<option value="5">Friday<option value="6">Saturday<option value="0">Sunday</select>every<input class="dhx_repeat_text" type="text" name="month_count2" value="1" />month<br /> </div> <div style="display:none;" id="dhx_repeat_year"> <label><input class="dhx_repeat_radio" type="radio" name="year_type" value="d"/>Every</label><input class="dhx_repeat_text" type="text" name="year_day" value="1" />day<select name="year_month"><option value="0" selected >January<option value="1">February<option value="2">March<option value="3">April<option value="4">May<option value="5">June<option value="6">July<option value="7">August<option value="8">September<option value="9">October<option value="10">November<option value="11">December</select>month<br /> <label><input class="dhx_repeat_radio" type="radio" name="year_type" checked value="w"/>On</label><input class="dhx_repeat_text" type="text" name="year_week2" value="1" /><select name="year_day2"><option value="1" selected >Monday<option value="2">Tuesday<option value="3">Wednesday<option value="4">Thursday<option value="5">Friday<option value="6">Saturday<option value="7">Sunday</select>of<select name="year_month2"><option value="0" selected >January<option value="1">February<option value="2">March<option value="3">April<option value="4">May<option value="5">June<option value="6">July<option value="7">August<option value="8">September<option value="9">October<option value="10">November<option value="11">December</select><br /> </div> </div> <div class="dhx_repeat_divider"></div> <div class="dhx_repeat_right"> <label><input class="dhx_repeat_radio" type="radio" name="end" checked/>No end date</label><br /> <label><input class="dhx_repeat_radio" type="radio" name="end" />After</label><input class="dhx_repeat_text" type="text" name="occurences_count" value="1" />occurrences<br /> <label><input class="dhx_repeat_radio" type="radio" name="end" />End by</label><input class="dhx_repeat_date" type="text" name="date_of_end" value="'+scheduler.config.repeat_date_of_end+'" /><br /> </div> </form> </div> <div style="clear:both"> </div>';

