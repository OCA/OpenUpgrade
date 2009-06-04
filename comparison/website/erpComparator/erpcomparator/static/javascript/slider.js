jQuery.fn.access = function(settings) {

    settings = jQuery.extend({
        Headline: "Top Stories",
        Speed: "normal"
    }, settings);
    return this.each(function(i) {    	
        aSlider.itemWidth = parseInt(jQuery(".item:eq(" + i + ")",".slider").css("width")) + parseInt(jQuery(".item:eq(" + i + ")",".slider").css("margin-right"));
        aSlider.init(settings,this);
        jQuery(".view_all > a", this).click(function() {
            aSlider.vAll(settings,this);
            return false;
        });
    });
};
var aSlider = {
    itemWidth: 0,
    
    init: function(s,p) { 
   
        jQuery(".messaging",p).css("display","none");
        jQuery(".scr_title",p).css("display","none");
        itemLength = jQuery(".item",p).length;
       	
       	if (itemLength < '4'){
       		jQuery(".next",p).css("display","none");
       		return false;
       	}
       	
       	if (itemLength == '4'){
       		jQuery(".next",p).css("display","none");
       		return false;
       	}
       
        newsContainerWidth = itemLength * aSlider.itemWidth;
        jQuery(".container",p).css("width",newsContainerWidth + "px");
        jQuery(".next",p).css("display","block");
        animating = false;
        jQuery(".next",p).click(function() {
        	
            if (animating == false) {
                animating = true;
                
                animateLeft = parseInt(jQuery(".container",p).css("left")) - (aSlider.itemWidth * 4);
                if (animateLeft + parseInt(jQuery(".container",p).css("width")) > 0) {
                    jQuery(".prev",p).css("display","block");
                    jQuery(".container",p).animate({left: animateLeft}, s.newsSpeed, function() {
                        jQuery(this).css("left",animateLeft);
                        if (parseInt(jQuery(".container",p).css("left")) + parseInt(jQuery(".container",p).css("width")) > aSlider.itemWidth * 2) {
                            jQuery(".next",p).css("display","none");
                        }
                        jQuery(".next",p).css("display","none");
                        animating = false;
                    });
                } else {
                	jQuery(".next",p).css("display","none");
                    animating = false;
                }
            }
            return false;
        });
        jQuery(".prev",p).click(function() {
            if (animating == false) {
                animating = true;
                animateLeft = parseInt(jQuery(".container",p).css("left")) + (aSlider.itemWidth * 4);
                if ((animateLeft + parseInt(jQuery(".container",p).css("width"))) <= parseInt(jQuery(".container",p).css("width"))) {
                    jQuery(".next",p).css("display","block");
                    jQuery(".container",p).animate({left: animateLeft}, s.newsSpeed, function() {
                        jQuery(this).css("left",animateLeft);
                        if (parseInt(jQuery(".container",p).css("left")) == 0) {
                            jQuery(".prev",p).css("display","none");
                        }
                        animating = false;
                    });
                } else {
                    animating = false;
                }
            }
            return false;
        });
    },
    vAll: function(s,p) {
    	
        var o = p;
        while (p) {
            p = p.parentNode;
            if (jQuery(p).attr("class") != undefined && jQuery(p).attr("class").indexOf("slider") != -1) {
                break;
            }
        }
        if (jQuery(o).text().indexOf("View All") != -1) {
            jQuery(".next",p).css("display","none");
            jQuery(".prev",p).css("display","none");
            jQuery(o).text("View Less");
            jQuery(".container",p).css("left","0px").css("width",aSlider.itemWidth * 2 + "px");
        } else {
            jQuery(o).text("View All");
            aSlider.init(s,p);
        }
    }
};
