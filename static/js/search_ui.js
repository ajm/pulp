var UI = (function(){

	var highlight_colors = [
		{ name: "Green", rgb: "74,201,112" },
		{ name: "Orange", rgb: "233,137,49" },
		{ name: "Red", rgb: "235,64,59" },
		{ name: "Turquoise", rgb: "42,176,197" },
		{ name: "Blue", rgb: "34,127,176" }
	]

	var back_to_top = function(){
		$("html, body").animate({ scrollTop: 0 }, "slow");
		return false;
	}

	var search_state = function(callback){
		$(".mean-bar").fadeOut(300);
		$(".bookmark-history-display").hide();
		$("#search-results").fadeOut(300, function(){
			$("#search-form-container").slideDown();
			$("#search-form-container input[type='text']").focus();
			callback();
		});
	}

	var end_search_state = function(){
		$("#search-form-container").slideUp();
		back_to_top();
	}

	var loading_state = function(callback){
		$(".layer").fadeIn(300);
		$("body").css("cursor", "wait");
		$("#search-results").fadeOut(300, function(){
			callback();
		});
	}

	var end_loading_state = function(){
		$(".bookmark-history-display").hide();
		$(".layer").fadeOut(300);
		$("body").css("cursor", "default");
		$("#search-results").fadeIn(300);
	}

	var display_mean_and_variance = function(){
		$(".mean-bar").fadeIn(300);
		$.each($(".mean-bar .progress-bar"), function(i, el){
			width = parseFloat($(el).attr("data-mean")) / (parseFloat($(el).attr("data-mean")) + parseFloat(parseFloat($(el).attr("data-variance"))));
			anim = { width: width*100 + "%" }
			$(el).animate(anim, 2500, "easeOutCubic");
			$(el).parent().tooltip({ title: Math.round(width*100) + "% based on previous selections, " + Math.round((1-width)*100) + "% variation" })
		});
	}

	var un_highlight = function(text){
		return String(text).replace(/<[^>]+>/gm, '')
	}

	var highlight = function(text, keywords, color){
		var content_words = String(text).split(" ");
		for(var i=0; i<content_words.length; i++){
			if(keywords[content_words[i].toLowerCase()]){
				weight = keywords[content_words[i].toLowerCase()];
				
				description = "";
				if(weight < 0.3){
					description = "Light weighted keyword";
				}else if(weight >= 0.3 && weight < 0.7){
					description = "Medium weighted keyword";
				}else{
					description = "Heavy weighted keyword";
				}

				content_words[i] = "<span class='word-weight animated bounceIn' data-toggle='tooltip' data-placement='top' title='" + description + "' style='background-color: rgba(" + color + "," + weight + "); border-bottom: 1px solid rgb(" + color + ")'>" + content_words[i] + "</span>";
			}
		}
		return content_words.join(" ");
	}

	return {
		search_state: search_state,
		end_search_state: end_search_state,
		loading_state: loading_state,
		end_loading_state: end_loading_state,
		highlight: highlight,
		un_highlight: un_highlight,
		highlight_colors: highlight_colors,
		back_to_top: back_to_top,
		display_mean_and_variance: display_mean_and_variance
	};
	
})();

$(document).on("ready", function(){

	UI.search_state(function(){});

	$("#back-to-top").on("click", function() {
		UI.back_to_top();
	});

	$("body").tooltip({
		selector: "#results-container .bookmark, .bookmarked-results-container .bookmark, .ellipsis, .bookmark-info, .word-weight"
	});

	$(".bookmark-info").live("mouseenter", function(){
		$(this).stop().animate({ bottom: 15 }, 300);
	});

	$(".bookmark-info").live("mouseleave", function(){
		$(this).stop().animate({ bottom: 0 }, 300, "easeOutCubic");
	});

	$(".bookmark-history-display-trigger").live("click", function(e){
		e.preventDefault();

		if($(".bookmark-history-display").is(":hidden")){
	
			$(".history-articles .bookmark").addClass("animated bounceIn");

			setTimeout(function(){
				$(".history-articles .bookmark").removeClass("animated bounceIn");
			}, 800);
		
		}
		
		$(".bookmark-history-display").stop().slideToggle();

		$(".history-articles .bookmark").popover({ trigger: "manual", html: true})
        .on("mouseenter", function () {
            var _this = this;
            $(this).popover("show");
            $(".popover").on("mouseleave", function () {
                $(_this).popover('hide');
            });
        }).on("mouseleave", function () {
            var _this = this;
            if (!$(".popover:hover").length) {
                    $(_this).popover("hide")
                }
            setTimeout(function () {
                
            }, 100);
        });

	});

	$("#article-count").selectpicker();
	$("#highlight-color").selectpicker();
	$("#back-to-top").removeAttr("disabled");

	$("#explain-search-results-modal").draggable();
	
	$(".color-palet-divider").tooltip();
});

$(document).on("scroll", function(){
	var scrollAmount = $(window).scrollTop();
	var documentHeight = $(document).height();
	var scrollPercent = (scrollAmount / documentHeight) * 100;

	if(scrollPercent > 0){
		$("#back-to-top").animate({
			bottom: 0
		},400);
	}else{
		$("#back-to-top").clearQueue().animate({
			bottom: -45
		},400);
	}
});