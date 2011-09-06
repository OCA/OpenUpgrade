function dhtmlXContainer(obj) {
	
	var that = this;
	
	this.obj = obj;
	this.dhxcont = null;
	
	this.setContent = function(data) {
		this.dhxcont = data;
		this.dhxcont.innerHTML = "<div id='dhxMainCont' style='position: relative; left: 0px; top: 0px; overflow: hidden;'></div>"+
					 "<div id='dhxContBlocker' class='dhxcont_content_blocker' style='display: none;'></div>";
		this.dhxcont.mainCont = this.dhxcont.childNodes[0];
		this.obj.dhxcont = this.dhxcont;
	}
	
	this.obj._genStr = function(w) {
		var s = ""; var z = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
		for (var q=0; q<w; q++) { s = s + z.charAt(Math.round(Math.random() * z.length)); }
		return s;
	}
	
	this.obj.setMinContentSize = function(w, h) {
		this._minDataSizeW = w;
		this._minDataSizeH = h;
	}
	
	this.obj.moveContentTo = function(cont) {
		
		
		// move dhtmlx components
		
		var pref = null;
		if (this.grid) pref = "grid";
		if (this.tree) pref = "tree";
		if (this.tabbar) pref = "tabbar";
		if (this.folders) pref = "folders";
		if (this.layout) pref = "layout";
		
		if (pref != null) {
			if (pref == "layout" && this._isCell && cont._isWindow) {
				var aDim = this.layout._defineWindowMinDimension(this, true);
				var bDim = cont.getDimension();
				cont.setDimension((aDim[1]>bDim[0]?aDim[1]:null), (aDim[2]>bDim[1]?aDim[2]:null));
			}
			if (pref == "tabbar" && cont._isCell) cont.hideHeader();
			cont.attachObject(this[pref+"Id"]);
			cont[pref] = this[pref];
			cont[pref+"Id"] = this[pref+"Id"];
			cont[pref+"Obj"] = this[pref+"Obj"];
			if (pref == "layout") {
				cont.layout._baseWFix = -2;
				cont.layout._baseHFix = -2;
				// from layout to window, attach event
				if (cont._isWindow) cont.attachEvent("_onBeforeTryResize", cont.layout._defineWindowMinDimension);
			}
			this[pref] = null;
			this[pref+"Id"] = null;
			this[pref+"Obj"] = null;
			if (pref == "tabbar" && this._isCell) this.showHeader();
		}
		
		// menu/toolbar/statusbar should be after any object
		if (this.menu != null) {
			cont.dhxcont.insertBefore(document.getElementById(this.menuId), cont.dhxcont.childNodes[0]);
			cont.menu = this.menu;
			cont.menuId = this.menuId;
			cont.menuHeight = this.menuHeight;
			this.menu = null;
			this.menuId = null;
			this.menuHeight = null;
			if (this._doOnAttachMenu) this._doOnAttachMenu("unload");
			if (cont._doOnAttachMenu) cont._doOnAttachMenu("move");
		}
		if (this.toolbar != null) {
			cont.dhxcont.insertBefore(document.getElementById(this.toolbarId), cont.dhxcont.childNodes[(cont.menu != null?1:0)]);
			cont.toolbar = this.toolbar;
			cont.toolbarId = this.toolbarId;
			cont.toolbarHeight = this.toolbarHeight;
			this.toolbar = null;
			this.toolbarId = null;
			this.toolbarHeight = null;
			if (this._doOnAttachToolbar) this._doOnAttachToolbar("unload");
			if (cont._doOnAttachToolbar) cont._doOnAttachToolbar("move");
		}
		if (this.sb != null) {
			cont.dhxcont.insertBefore(document.getElementById(this.sbId), cont.dhxcont.childNodes[cont.dhxcont.childNodes.length-1]);
			cont.sb = this.sb;
			cont.sbId = this.sbId;
			cont.sbHeight = this.sbHeight;
			this.sb = null;
			this.sbId = null;
			this.sbHeight = null;
			if (this._doOnAttachToolbar) this._doOnAttachToolbar("unload");
			if (cont._doOnAttachToolbar) cont._doOnAttachToolbar("move");
		}
		
		// other objects
		var objA = this.dhxcont.childNodes[0];
		var objB = cont.dhxcont.childNodes[0];
		while (objA.childNodes.length > 0) objB.appendChild(objA.childNodes[0]);
		//
		cont.updateNestedObjects();
	}
	
	this.obj.adjustContent = function(parentObj, offsetTop, marginTop, notCalcWidth, offsetBottom) {
		
		this.dhxcont.style.left = (this._offsetLeft||0)+"px";
		this.dhxcont.style.top = (this._offsetTop||0)+offsetTop+"px";
		//
		var cw = parentObj.clientWidth+(this._offsetWidth||0);
		if (notCalcWidth !== true) this.dhxcont.style.width = Math.max(0, cw)+"px";
		if (notCalcWidth !== true) if (this.dhxcont.offsetWidth > cw) this.dhxcont.style.width = Math.max(0, cw*2-this.dhxcont.offsetWidth)+"px";
		//
		var ch = parentObj.clientHeight+(this._offsetHeight||0);
		this.dhxcont.style.height = Math.max(0, ch-offsetTop)+(marginTop!=null?marginTop:0)+"px";
		if (this.dhxcont.offsetHeight > ch - offsetTop) this.dhxcont.style.height = Math.max(0, (ch-offsetTop)*2-this.dhxcont.offsetHeight)+"px";
		if (offsetBottom) if (!isNaN(offsetBottom)) this.dhxcont.style.height = Math.max(0, parseInt(this.dhxcont.style.height)-offsetBottom)+"px";
		
		// main window content
		if (this._minDataSizeH != null) {
			// height for menu/toolbar/status bar should be included
			if (parseInt(this.dhxcont.style.height) < this._minDataSizeH) this.dhxcont.style.height = this._minDataSizeH+"px";
		}
		if (this._minDataSizeW != null) {
			if (parseInt(this.dhxcont.style.width) < this._minDataSizeW) this.dhxcont.style.width = this._minDataSizeW+"px";
		}
		
		if (notCalcWidth !== true) {
			this.dhxcont.mainCont.style.width = this.dhxcont.clientWidth+"px";
			// allow border to this.dhxcont.mainCont
			if (this.dhxcont.mainCont.offsetWidth > this.dhxcont.clientWidth) this.dhxcont.mainCont.style.width = Math.max(0, this.dhxcont.clientWidth*2-this.dhxcont.mainCont.offsetWidth)+"px";
		}
		
		var menuOffset = (this.menu!=null?(!this.menuHidden?this.menuHeight:0):0);
		var toolbarOffset = (this.toolbar!=null?(!this.toolbarHidden?this.toolbarHeight:0):0);
		var statusOffset = (this.sb!=null?(!this.sbHidden?this.sbHeight:0):0);
		
		// allow border to this.dhxcont.mainCont
		this.dhxcont.mainCont.style.height = this.dhxcont.clientHeight+"px";
		if (this.dhxcont.mainCont.offsetHeight > this.dhxcont.clientHeight) this.dhxcont.mainCont.style.height = Math.max(0, this.dhxcont.clientHeight*2-this.dhxcont.mainCont.offsetHeight)+"px";
		this.dhxcont.mainCont.style.height = Math.max(0, parseInt(this.dhxcont.mainCont.style.height)-menuOffset-toolbarOffset-statusOffset)+"px";
		
	}
	this.obj.coverBlocker = function() {
		return this.dhxcont.childNodes[this.dhxcont.childNodes.length-1];
	}
	this.obj.showCoverBlocker = function() {
		this.coverBlocker().style.display = "";
	}
	this.obj.hideCoverBlocker = function() {
		this.coverBlocker().style.display = "none";
	}
	this.obj.updateNestedObjects = function() {
		if (this.grid) { this.grid.setSizes(); }
		if (this.tabbar) { this.tabbar.adjustOuterSize(); }
		if (this.folders) { this.folders.setSizes(); }
		if (this.editor) {
			if (!_isIE) this.editor._prepareContent(true);
			this.editor.setSizes();
		}
		 //if (_isOpera) { var t = this; window.setTimeout(function(){t.editor.adjustSize();},10); } else { this.editor.adjustSize(); } }
		if (this.layout) {
			this.layoutObj.style.width = this.dhxcont.mainCont.style.width;
			this.layoutObj.style.height = this.dhxcont.mainCont.style.height;
			
			if (this._isAcc && this.skin == "dhx_skyblue") {
				this.layoutObj.style.width = parseInt(this.dhxcont.mainCont.style.width)+2+"px";
				this.layoutObj.style.height = parseInt(this.dhxcont.mainCont.style.height)+2+"px";
			}
			
			this.layout.setSizes();
		}
		if (this.accordion != null) {
			this.accordionObj.style.width = parseInt(this.dhxcont.mainCont.style.width)+2+"px";
			this.accordionObj.style.height = parseInt(this.dhxcont.mainCont.style.height)+2+"px";
			this.accordion.setSizes();
		}
		// docked layout's cell
		if (this.dockedCell) { this.dockedCell.updateNestedObjects(); }
		/*
		if (win.accordion != null) { win.accordion.setSizes(); }
		if (win.layout != null) { win.layout.setSizes(win); }
		*/
	}
	/**
	*   @desc: attaches a status bar to a window
	*   @type: public
	*/
	this.obj.attachStatusBar = function() {
		var sbObj = document.createElement("DIV");
		
		if (this._isCell) {
			sbObj.className = "dhxcont_sb_container_layoutcell";
		} else {
			sbObj.className = "dhxcont_sb_container";
		}
		sbObj.id = "sbobj_"+this._genStr(12);
		sbObj.innerHTML = "<div class='dhxcont_statusbar'></div>";
		this.dhxcont.insertBefore(sbObj, this.dhxcont.childNodes[this.dhxcont.childNodes.length-1]);
		
		sbObj.setText = function(text) { this.childNodes[0].innerHTML = text; }
		sbObj.getText = function() { return this.childNodes[0].innerHTML; }
		sbObj.onselectstart = function(e) { e=e||event; e.returnValue=false; return false; }
		this.sb = sbObj;
		this.sbHeight = sbObj.offsetHeight;
		this.sbId = sbObj.id;
		
		if (this._doOnAttachStatusBar) this._doOnAttachStatusBar("init");
		this.adjust();
		return this.sb;
	}
	/**
	*   @desc: detaches a status bar from a window
	*   @type: public
	*/
	this.obj.detachStatusBar = function() {
		if (!this.sb) return;
		this.sb.setText = null;
		this.sb.getText = null;
		this.sb.onselectstart = null;
		this.sb.parentNode.removeChild(this.sb);
		this.sb = null;
		this.sbHeight = null;
		this.sbId = null;
		if (this._doOnAttachStatusBar) this._doOnAttachStatusBar("unload");
	}
	/**
	*   @desc: attaches a dhtmlxMenu to a window
	*   @type: public
	*/
	this.obj.attachMenu = function() {
		var menuObj = document.createElement("DIV");
		menuObj.style.position = "relative";
		menuObj.style.overflow = "hidden";
		
		menuObj.id = "dhxmenu_"+this._genStr(12);
		this.dhxcont.insertBefore(menuObj, this.dhxcont.childNodes[0]);
		
		this.menu = new dhtmlXMenuObject(menuObj.id, this.skin);
		
		this.menuHeight = menuObj.offsetHeight;
		this.menuId = menuObj.id;
		
		if (this._doOnAttachMenu) this._doOnAttachMenu("init");
		
		this.adjust();
		return this.menu;
	}
	/**
	*   @desc: detaches a dhtmlxMenu from a window
	*   @type: public
	*/
	this.obj.detachMenu = function() {
		if (!this.menu) return;
		var menuObj = document.getElementById(this.menuId);
		this.menu.unload();
		this.menu = null;
		this.menuId = null;
		this.menuHeight = null;
		menuObj.parentNode.removeChild(menuObj);
		menuObj = null;
		if (this._doOnAttachMenu) this._doOnAttachMenu("unload");
	}
	/**
	*   @desc: attaches a dhtmlxToolbar to a window
	*   @type: public
	*/
	this.obj.attachToolbar = function() {
		var toolbarObj = document.createElement("DIV");
		toolbarObj.style.position = "relative";
		toolbarObj.style.overflow = "hidden";
		toolbarObj.id = "dhxtoolbar_"+this._genStr(12);
		this.dhxcont.insertBefore(toolbarObj, this.dhxcont.childNodes[(this.menu!=null?1:0)]);
		this.toolbar = new dhtmlXToolbarObject(toolbarObj.id, this.skin);
		this.toolbarHeight = toolbarObj.offsetHeight+(this._isLayout&&this.skin=="dhx_skyblue"?2:0);
		this.toolbarId = toolbarObj.id;
		if (this._doOnAttachToolbar) this._doOnAttachToolbar("init");
		this.adjust();
		return this.toolbar;
	}
	/**
	*   @desc: detaches a dhtmlxToolbar from a window
	*   @type: public
	*/
	this.obj.detachToolbar = function() {
		if (!this.toolbar) return;
		var toolbarObj = document.getElementById(this.toolbarId);
		this.toolbar.unload();
		this.toolbar = null;
		this.toolbarId = null;
		this.toolbarHeight = null;
		toolbarObj.parentNode.removeChild(toolbarObj);
		toolbarObj = null;
		if (this._doOnAttachToolbar) this._doOnAttachToolbar("unload");
	}
	/**
	*   @desc: attaches a dhtmlxGrid to a window
	*   @type: public
	*/
	this.obj.attachGrid = function() {
		if (this._isWindow && this.skin == "dhx_skyblue") {
			this.dhxcont.mainCont.style.border = "#a4bed4 1px solid";
			this._redraw();
		}
		var obj = document.createElement("DIV");
		obj.id = "dhxGridObj_"+this._genStr(12);
		obj.style.width = "100%";
		obj.style.height = "100%";
		obj.cmp = "grid";
		document.body.appendChild(obj);
		this.attachObject(obj.id);
		this.grid = new dhtmlXGridObject(obj.id);
		this.grid.setSkin(this.skin);
		this.grid.entBox.style.border = "0px solid white";
		this.grid._sizeFix=0;
		
		this.gridId = obj.id;
		this.gridObj = obj;
		
		return this.grid;
	}
	/**
	*   @desc: attaches a dhtmlxScheduler to a window
	*   @type: public
	*/	
	this.obj.attachScheduler = function(day,mode) {
		var obj = document.createElement("DIV");
		obj.innerHTML='<div id="scheduler_here" class="dhx_cal_container" style="width:100%; height:100%;"><div class="dhx_cal_navline"><div class="dhx_cal_prev_button">&nbsp;</div><div class="dhx_cal_next_button">&nbsp;</div><div class="dhx_cal_today_button"></div><div class="dhx_cal_date"></div><div class="dhx_cal_tab" name="day_tab" style="right:204px;"></div><div class="dhx_cal_tab" name="week_tab" style="right:140px;"></div><div class="dhx_cal_tab" name="month_tab" style="right:76px;"></div></div><div class="dhx_cal_header"></div><div class="dhx_cal_data"></div></div>';
		
		document.body.appendChild(obj.firstChild);
		this.attachObject("scheduler_here");
		
		this.grid = scheduler;
		scheduler.setSizes = scheduler.update_view;
		scheduler.destructor=function(){};
		scheduler.init("scheduler_here",day,mode);
		
		//this.grid.entBox.style.border = "0px solid white";
		

		return this.grid;
	}	
	/**
	*   @desc: attaches a dhtmlxTree to a window
	*   @param: rootId - not mandatory, tree super root, see dhtmlxTree documentation for details
	*   @type: public
	*/
	this.obj.attachTree = function(rootId) {
		if (this._isWindow && this.skin == "dhx_skyblue") {
			this.dhxcont.mainCont.style.border = "#a4bed4 1px solid";
			this._redraw();
		}
		var obj = document.createElement("DIV");
		obj.id = "dhxTreeObj_"+this._genStr(12);
		obj.style.width = "100%";
		obj.style.height = "100%";
		obj.cmp = "tree";
		document.body.appendChild(obj);
		this.attachObject(obj.id);
		this.tree = new dhtmlXTreeObject(obj.id, "100%", "100%", (rootId||0));
		this.tree.setSkin(this.skin);
		// this.tree.allTree.style.paddingTop = "2px";
		this.tree.allTree.childNodes[0].style.marginTop = "2px";
		this.tree.allTree.childNodes[0].style.marginBottom = "2px";
		
		this.treeId = obj.id;
		this.treeObj = obj;
		
		return this.tree;
	}
	/**
	*   @desc: attaches a dhtmlxTabbar to a window
	*   @type: public
	*/
	this.obj.attachTabbar = function(mode) {
		
		if (this._isWindow && this.skin == "dhx_skyblue") {
			this.dhxcont.style.border = "none";
			this.setDimension(this.w, this.h);
		}
		
		var obj = document.createElement("DIV");
		obj.id = "dhxTabbarObj_"+this._genStr(12);
		obj.style.width = "100%";
		obj.style.height = "100%";
		obj.style.overflow = "hidden";
		obj.cmp = "tabbar";
		document.body.appendChild(obj);
		this.attachObject(obj.id);
		
		// manage dockcell if exists
		/*
		if (this._dockCell != null && that.dhxLayout != null) {
			var dockCell = that.dhxLayout.polyObj[this._dockCell];
			if (dockCell != null) {
				dockCell.childNodes[0]._tabbarMode = true;
				that.dhxLayout.hidePanel(this._dockCell);
				dockCell.className = "dhtmlxLayoutSinglePolyTabbar";
				// dockCell.childNodes[0]._h = -2;
				// dockCell.childNodes[1].style.height = parseInt(dockCell.childNodes[1].style.height) - dockCell.childNodes[0]._h + "px";
				// dockCell.className = "dhtmlxLayoutSinglePolyTabbar";
				// fix panel
				// that.dhxLayout._panelForTabs(this._dockCell);
			}
		}
		*/
		if (this.className == "dhtmlxLayoutSinglePoly") { this.hideHeader(); }
		//
		this.tabbar = new dhtmlXTabBar(obj.id, mode||"top", 20);
		if (!this._isWindow)
			this.tabbar._s.expand = true;
		this.tabbar.setSkin(this.skin);
		/*
		if ((_isIE)&&(document.compatMode == "BackCompat")){
			this.tabbar._lineAHeight=this.tabbar._lineA.style.height="6px";
			this.tabbar._bFix=5;
		} else{
			this.tabbar._lineAHeight=this.tabbar._lineA.style.height="4px";
			this.tabbar._bFix=4;
		}
		*/
		//this.tabbar.setSkin("dhx_blue");
		//this.tabbar.enableScroll(false)
		//this.tabbar._conZone.style.borderWidth="0px";
		//this.tabbar._EARS = true;
		//this.tabbar.setMargin(-1)
		//this.tabbar.setOffset(0)
		this.tabbar.adjustOuterSize();
		this.tabbarId = obj.id;
		this.tabbarObj = obj;
		
		return this.tabbar;
	}
	/**
	*   @desc: attaches a dhtmlxFolders to a window
	*   @type: public
	*/
	this.obj.attachFolders = function() {
		if (this._isWindow && this.skin == "dhx_skyblue") {
			this.dhxcont.mainCont.style.border = "#a4bed4 1px solid";
			this._redraw();
		}
		var obj = document.createElement("DIV");
		obj.id = "dhxFoldersObj_"+this._genStr(12);
		obj.style.width = "100%";
		obj.style.height = "100%";
		obj.style.overflow = "hidden";
		obj.cmp = "folders";
		document.body.appendChild(obj);
		this.attachObject(obj.id);
		this.folders = new dhtmlxFolders(obj.id);
		this.folders.setSizes();
		
		this.foldersId = obj.id;
		this.foldersObj = obj;
		
		return this.folders;
	}
	/**
	*   @desc: attaches a dhtmlxAccordion to a window
	*   @type: public
	*/
	this.obj.attachAccordion = function() {
		if (this._isWindow && this.skin == "dhx_skyblue") {
			this.dhxcont.mainCont.style.border = "#a4bed4 1px solid";
			this._redraw();
		}
		
		var obj = document.createElement("DIV");
		obj.id = "dhxAccordionObj_"+this._genStr(12);
		
		obj.style.left = "-1px";
		obj.style.top = "-1px";
		obj.style.width = parseInt(this.dhxcont.mainCont.style.width)+2+"px";
		obj.style.height = parseInt(this.dhxcont.mainCont.style.height)+2+"px";
		//
		obj.style.position = "relative";
		obj.cmp = "accordion";
		document.body.appendChild(obj);
		this.attachObject(obj.id);
		this.accordion = new dhtmlXAccordion(obj.id, this.skin);
		
		// win._content.childNodes[2].className += " dhtmlxAccordionAttached";
		this.accordion.setSizes();
		
		this.accordionId = obj.id;
		this.accordionObj = obj;
		
		return this.accordion;
	}
	/**
	*   @desc: attaches a dhtmlxLayout to a window
	*   @param: view - layout's pattern
	*   @param: skin - layout's skin
	*   @type: public
	*/
	this.obj.attachLayout = function(view, skin) {
		
		// attach layout to layout
		if (this._isCell && this.skin == "dhx_skyblue") {
			this.hideHeader();
			this.dhxcont.style.border = "0px solid white";
			this.adjustContent(this.childNodes[0], 0);
		}
		
		var obj = document.createElement("DIV");
		obj.id = "dhxLayoutObj_"+this._genStr(12);
		obj.style.overflow = "hidden";
		obj.style.position = "absolute";
		
		obj.style.left = "0px";
		obj.style.top = "0px";
		obj.style.width = parseInt(this.dhxcont.mainCont.style.width)+"px";
		obj.style.height = parseInt(this.dhxcont.mainCont.style.height)+"px";
		
		if (this._isAcc && this.skin == "dhx_skyblue") {
			obj.style.left = "-1px";
			obj.style.top = "-1px";
			obj.style.width = parseInt(this.dhxcont.mainCont.style.width)+2+"px";
			obj.style.height = parseInt(this.dhxcont.mainCont.style.height)+2+"px";
		}
		
		// needed for layout's init
		obj.dhxContExists = true;
		obj.cmp = "layout";
		document.body.appendChild(obj);
		this.attachObject(obj.id);
		
		this.layout = new dhtmlXLayoutObject(obj, view, this.skin);
		
		// window/layout events configuration
		
		if (this._isWindow) this.attachEvent("_onBeforeTryResize", this.layout._defineWindowMinDimension);
		
		this.layoutId = obj.id;
		this.layoutObj = obj;
		
		// this.adjust();
		return this.layout;
	}
	/**
	*   @desc: attaches a dhtmlxEditor to a window
	*   @param: skin - not mandatory, editor's skin
	*   @type: public
	*/
	this.obj.attachEditor = function(skin) {
		if (this._isWindow && this.skin == "dhx_skyblue") {
			this.dhxcont.mainCont.style.border = "#a4bed4 1px solid";
			this._redraw();
		}
		var obj = document.createElement("DIV");
		obj.id = "dhxEditorObj_"+this._genStr(12);
		obj.style.position = "relative";
		obj.style.display = "none";
		obj.style.overflow = "hidden";
		obj.style.width = "100%";
		obj.style.height = "100%";
		obj.cmp = "editor";
		document.body.appendChild(obj);
		//
		this.attachObject(obj.id);
		//
		this.editor = new dhtmlXEditor(obj.id, this.skin);
		
		this.editorId = obj.id;
		this.editorObj = obj;
		return this.editor;
		
	}
	
	/**
	*   @desc: attaches an object into a window
	*   @param: obj - object or object id
	*   @param: autoSize - set true to adjust a window to object's dimension
	*   @type: public
	*/
	this.obj.attachObject = function(obj, autoSize) {
		if (typeof(obj) == "string") obj = document.getElementById(obj);
		if (autoSize) {
			obj.style.visibility = "hidden";
			obj.style.display = "";
			var objW = obj.offsetWidth;
			var objH = obj.offsetHeight;
		}
		this._attachContent("obj", obj);
		if (autoSize && this._isWindow) {
			obj.style.visibility = "visible";
			this._adjustToContent(objW, objH);
			/* this._engineAdjustWindowToContent(this, objW, objH); */
		}
	}
	/**
	*
	*
	*/
	this.obj.detachObject = function(remove) {
		
		// detach dhtmlx components
		
		var pref = null;
		
		if (this.tree) pref = "tree";
		if (this.grid) pref = "grid";
		if (this.layout) pref = "layout";
		if (this.tabbar) pref = "tabbar";
		if (this.accordion) pref = "accordion";
		if (this.folders) pref = "folders";
		
		if (pref != null) {
			var objHandler = null;
			var objLink = null;
			if (remove == true) {
				// completely remove
				if (this[pref].unload) this[pref].unload();
				if (this[pref].destructor) this[pref].destructor();
				while (this[pref+"Obj"].childNodes.length > 0) this[pref+"Obj"].removeChild(this[pref+"Obj"].childNodes[0]);
			} else {
				// attach to body
				document.body.appendChild(this[pref+"Obj"]);
				this[pref+"Obj"].style.display = "none";
				objHandler = this[pref];
				objLink = this[pref+"Obj"];
			}
			this[pref] = null;
			this[pref+"Id"] = null;
			this[pref+"Obj"] = null;
			return new Array(objHandler, objLink);
		}
		
		// detach any other content
		var objA = this.dhxcont.childNodes[0];
		while (objA.childNodes.length > 0) {
			if (remove == true) {
				objA.removeChild(objA.childNodes[0]);
			} else {
				var obj = objA.childNodes[0];
				document.body.appendChild(obj);
				obj.style.display = "none";
			}
		}
	}
	
	/**
	*   @desc: appends an object into a window
	*   @param: obj - object or object id
	*   @type: public
	*/
	this.obj.appendObject = function(obj) {
		if (typeof(obj) == "string") { obj = document.getElementById(obj); }
		this._attachContent("obj", obj, true);
	}
	/**
	*   @desc: attaches an html string as an object into a window
	*   @param: str - html string
	*   @type: public
	*/
	this.obj.attachHTMLString = function(str) {
		this._attachContent("str", str);
		var z=str.match(/<script[^>]*>[^\f]*?<\/script>/g)||[];
		for (var i=0; i<z.length; i++){
			var s=z[i].replace(/<([\/]{0,1})script[^>]*>/g,"")
			if (window.execScript) {
				if (!s.length){
					var url =/src=('|")([^'"]+)('|")/.match(z[i]);
					debugger;
					if (!url) return;
					
					s=dhtmlxAjaxa.getSync(url);
				}
				window.execScript(s);
			}
			else window.eval(s);
		}
	}
	/**
	*   @desc: attaches an url into a window
	*   @param: url
	*   @param: ajax - loads an url with ajax
	*   @type: public
	*/
	this.obj.attachURL = function(url, ajax) {
		this._attachContent((ajax==true?"urlajax":"url"), url, false);
	}
	this.obj.adjust = function() {
		if (this.skin == "dhx_skyblue") {
			if (this.menu) {
				if (this._isWindow || this._isLayout) {
					this.menu._topLevelOffsetLeft = 0;
					document.getElementById(this.menuId).style.height = "26px";
					this.menuHeight = document.getElementById(this.menuId).offsetHeight;
					if (this._doOnAttachMenu) this._doOnAttachMenu("show");
				}
				if (this._isCell) {
					document.getElementById(this.menuId).className += " in_layoutcell";
					// document.getElementById(this.menuId).style.height = "25px";
					this.menuHeight = 25;
				}
				if (this._isAcc) {
					document.getElementById(this.menuId).className += " in_acccell";
					// document.getElementById(this.menuId).style.height = "25px";
					this.menuHeight = 25;
				}
				if (this._doOnAttachMenu) this._doOnAttachMenu("adjust");
			}
			if (this.toolbar) {
				if (this._isWindow || this._isLayout) {
					document.getElementById(this.toolbarId).style.height = "29px";
					this.toolbarHeight = document.getElementById(this.toolbarId).offsetHeight;
					if (this._doOnAttachToolbar) this._doOnAttachToolbar("show");
				}
				if (this._isCell) {
					document.getElementById(this.toolbarId).className += " in_layoutcell";
				}
				if (this._isAcc) {
					document.getElementById(this.toolbarId).className += " in_acccell";
				}
			}
		}
	}
	// attach content obj|url
	this.obj._attachContent = function(type, obj, append) {
		// clear old content
		if (append !== true) {
			while (that.dhxcont.mainCont.childNodes.length > 0) { that.dhxcont.mainCont.removeChild(that.dhxcont.mainCont.childNodes[0]); }
		}
		// attach
		if (type == "url") {
			if (this._isWindow && obj.cmp == null && this.skin == "dhx_skyblue") {
				this.dhxcont.mainCont.style.border = "#a4bed4 1px solid";
				this._redraw();
			}
			var fr = document.createElement("IFRAME");
			fr.frameBorder = 0;
			fr.border = 0;
			fr.style.width = "100%";
			fr.style.height = "100%";
			fr.setAttribute("src","javascript:false;");
			that.dhxcont.mainCont.appendChild(fr);
			fr.src = obj;
			this._frame = fr;
			if (this._doOnAttachURL) this._doOnAttachURL(true);
		} else if (type == "urlajax") {
			if (this._isWindow && obj.cmp == null && this.skin == "dhx_skyblue") {
				this.dhxcont.mainCont.style.border = "#a4bed4 1px solid";
				this.dhxcont.mainCont.style.backgroundColor = "#FFFFFF";
				this._redraw();
			}
			var t = this;
			var xmlParser = function(){
				t.attachHTMLString(this.xmlDoc.responseText,this);
				if (t._doOnAttachURL) t._doOnAttachURL(false);
				this.destructor();
			}
			var xmlLoader = new dtmlXMLLoaderObject(xmlParser, window);
			xmlLoader.dhxWindowObject = this;
			xmlLoader.loadXML(obj);
		} else if (type == "obj") {
			if (this._isWindow && obj.cmp == null && this.skin == "dhx_skyblue") {
				this.dhxcont.mainCont.style.border = "#a4bed4 1px solid";
				this.dhxcont.mainCont.style.backgroundColor = "#FFFFFF";
				this._redraw();
			}
			that.dhxcont._frame = null;
			that.dhxcont.mainCont.appendChild(obj);
			// this._engineGetWindowContent(win).style.overflow = (append===true?"auto":"hidden");
			// win._content.childNodes[2].appendChild(obj);
			that.dhxcont.mainCont.style.overflow = (append===true?"auto":"hidden");
			obj.style.display = "";
		} else if (type == "str") {
			if (this._isWindow && obj.cmp == null && this.skin == "dhx_skyblue") {
				this.dhxcont.mainCont.style.border = "#a4bed4 1px solid";
				this.dhxcont.mainCont.style.backgroundColor = "#FFFFFF";
				this._redraw();
			}
			that.dhxcont._frame = null;
			that.dhxcont.mainCont.innerHTML = obj;
		}
	}
	
	this.obj.showMenu = function() {
		if (!(this.menu && this.menuId)) return;
		if (document.getElementById(this.menuId).style.display != "none") return;
		this.menuHidden = false;
		if (this._doOnAttachMenu) this._doOnAttachMenu("show");
		document.getElementById(this.menuId).style.display = "";
	}
	
	this.obj.hideMenu = function() {
		if (!(this.menu && this.menuId)) return;
		if (document.getElementById(this.menuId).style.display == "none") return;
		document.getElementById(this.menuId).style.display = "none";
		this.menuHidden = true;
		if (this._doOnAttachMenu) this._doOnAttachMenu("hide");
	}
	
	this.obj.showToolbar = function() {
		if (!(this.toolbar && this.toolbarId)) return;
		if (document.getElementById(this.toolbarId).style.display != "none") return;
		this.toolbarHidden = false;
		if (this._doOnAttachToolbar) this._doOnAttachToolbar("show");
		document.getElementById(this.toolbarId).style.display = "";
	}
	
	this.obj.hideToolbar = function() {
		if (!(this.toolbar && this.toolbarId)) return;
		if (document.getElementById(this.toolbarId).style.display == "none") return;
		this.toolbarHidden = true;
		document.getElementById(this.toolbarId).style.display = "none";
		if (this._doOnAttachToolbar) this._doOnAttachToolbar("hide");
	}
	
	this.obj.showStatusBar = function() {
		if (!(this.sb && this.sbId)) return;
		if (document.getElementById(this.sbId).style.display != "none") return;
		this.sbHidden = false;
		if (this._doOnAttachStatusBar) this._doOnAttachStatusBar("show");
		document.getElementById(this.sbId).style.display = "";
	}
	
	this.obj.hideStatusBar = function() {
		if (!(this.sb && this.sbId)) return;
		if (document.getElementById(this.sbId).style.display == "none") return;
		this.sbHidden = true;
		document.getElementById(this.sbId).style.display = "none";
		if (this._doOnAttachStatusBar) this._doOnAttachStatusBar("hide");
	}
	
	this.obj._dhxContDestruct = function() {
		
		// clear attached objects
		this.detachMenu();
		this.detachToolbar();
		this.detachStatusBar();
		
		// remove any attached object
		this.detachObject(true);
		
		// remove attached components
		if (this.layout) this.layout.unlaod();
		if (this.accordion) this.accordion.unlaod();
		if (this.grid) this.grid.destructor();
		if (this.tree) this.tree.destructor();
		if (this.tabbar) this.tabbar.destructor();
		this.layout = null;
		this.accordion = null;
		this.grid = null;
		this.tree = null;
		this.tabbar = null;
		
		// clear methods
		this.adjust = null;
		this._genStr = null;
		this.setMinContentSize = null;
		this.moveContentTo = null;
		this.adjustContent = null;
		this.coverBlocker = null;
		this.showCoverBlocker = null;
		this.hideCoverBlocker = null;
		this.updateNestedObjects = null;
		this.attachStatusBar = null;
		this.detachStatusBar = null;
		this.attachMenu = null;
		this.detachMenu = null;
		this.attachToolbar = null;
		this.detachToolbar = null;
		
		this.attachGrid = this.attachTree = this.attachTabbar = this.attachFolders = this.attachAccordion = this.attachLayout = this.attachEditor = this.attachObject = this.detachObject = this.appendObject = this.attachHTMLString =  this.attachURL = this._attachContent = this.attachScheduler = null;
		
		this.showMenu = null;
		this.hideMenu = null;
		this.showToolbar = null;
		this.hideToolbar = null;
		this.showStatusBar = null;
		this.hideStatusBar = null;
		
		while (this.dhxcont.mainCont.childNodes.length > 0) this.dhxcont.mainCont.removeChild(this.dhxcont.mainCont.childNodes[0]);
		this.dhxcont.mainCont.innerHTML = "";
		this.dhxcont.mainCont = null;
		try { delete this.dhxcont["mainCont"]; } catch(e){};
		
		while (this.dhxcont.childNodes.length > 0) this.dhxcont.removeChild(this.dhxcont.childNodes[0]);
		this.dhxcont.innerHTML = "";
		this.dhxcont = null;
		try { delete this["dhxcont"]; } catch(e){};
	}
	
}
