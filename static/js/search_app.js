var SearchApp = angular.module("SearchApp", []);

SearchApp.filter("strip_tags", function(){
	return function(text){
		return String(text).replace(/<[^>]+>/gm, '');
	};
});

SearchApp.filter("synopsis", function(){
	return function(text){
		return ( String(text).length > 300 ? String(text).substring(0,300) + "..." : String(text) );
	}
});

SearchApp.controller("SearchController", ["$scope","$sce", function($scope, $sce){

	$scope.bookmark_history = [];
	$scope.bookmark_history_showing = false;
	$scope.results = [];
	$scope.highlight_colors = UI.highlight_colors;
	$scope.selected_highlight_color = UI.highlight_colors[0];

	var highlight_keywords = false;
	var keywords = {};
	var iteration = 1;

	// SCOPE FUNCTIONS

	$scope.search = function(){
		reset_variables();

		UI.end_search_state();
		UI.loading_state(function(){
			fetch_articles();
		});
	}

	$scope.toggle_bookmark_history = function(){
		$scope.bookmark_history_showing = !$scope.bookmark_history_showing;
	}

	$scope.toggle_bookmark = function(result){
		if(result.bookmarked){
			var el = ".bookmark-info[data-result-id='" + result.id + "']";
			$(el).addClass("bounceOutDown");

			setTimeout(function(){
				result.bookmarked = false;
				$scope.$apply();
			}, 400);
		}else{
			result.bookmarked = true;
		}
	}

	$scope.next = function(){

		$scope.bookmark_history_showing = false;

		var history_obj = {
			iteration: iteration,
			articles: []
		}

		$scope.results.forEach(function(result){
			if(result.bookmarked){
				history_obj.articles.push(result);
			}
		});

		if(history_obj.articles.length != 0){
			$scope.bookmark_history.push(history_obj);
		}

		UI.loading_state(function(){
			$.get("/next", next_params())
			.done(function(response){
				$scope.results = response.articles;
				
				keywords = response.keywords;
				init_results();

				iteration++;

				$("#explain-search-results-trigger").fadeIn();
			})
			.fail(function(){
				$scope.results = [];
			})
			.always(function(){
				$scope.search_heading = $scope.search_keyword;
				$scope.$apply();

				if(highlight_keywords){
					highlight();
				}

				UI.end_loading_state();
				UI.display_mean_and_variance();
				UI.back_to_top();
			});
		});

	}

	$scope.end = function(){
		$scope.search_keyword = "";
		$scope.$apply();
		
		$("#explain-search-results-trigger").fadeOut();

		$.get("/end")
		.always(function(){
			UI.search_state(function(){
				reset_variables();
			});
		});
	}

	$scope.toggle_highlight = function(){
		$("#highlight-toggle").toggleClass("checked");
		$("#highlight-info").slideToggle();

		highlight_keywords = !highlight_keywords;
		if(highlight_keywords){
			highlight();
		}else{
			un_highlight();
		}
	}

	$scope.toggle_statistics = function(){
		$("#statistics-toggle").toggleClass("checked");
		$("#statistics-info").slideToggle();
	}

	$scope.show_full_abstract = function(result){
		result.abstract_synopsis = result.abstract;
		result.full_length_abstract = true;
	}

	$scope.bookmarked_results = function(result){
		return ( result.bookmarked == true );
	}

	// PRIVATE FUNCTIONS

	var un_highlight = function(){
		$scope.results.forEach(function(result){
			result.abstract = $sce.trustAsHtml(UI.un_highlight(result.abstract));
			result.abstract_synopsis = $sce.trustAsHtml(UI.un_highlight(result.abstract_synopsis));
			result.title = $sce.trustAsHtml(UI.un_highlight(result.title));
		});

		$scope.$apply();
	}

	var highlight = function(){
		un_highlight();

		$scope.results.forEach(function(result){
			result.abstract = $sce.trustAsHtml(UI.highlight(result.abstract, keywords, $scope.selected_highlight_color.rgb));
			result.abstract_synopsis = $sce.trustAsHtml(UI.highlight(result.abstract_synopsis, keywords, $scope.selected_highlight_color.rgb));
			result.title = $sce.trustAsHtml(UI.highlight(result.title, keywords, $scope.selected_highlight_color.rgb));
		});

		$scope.$apply();
	}

	var fetch_articles = function(){
		$.get("/query", { "q": $scope.search_keyword, "article-count": parseInt($("#article-count option:selected").val()) })
		.done(function(data){
      		$scope.results = data;
      		init_results();
		})
		.fail(function(){
			$scope.results = [];
		})
		.always(function(){
			$scope.search_heading = $scope.search_keyword;
			$scope.$apply();

      		UI.end_loading_state();
		});
	}

	var set_highlighting = function (value){
		if(!value){
			$("#highlight-toggle").removeClass("checked");
			$("#highlight-info").hide();
			highlight_keywords = false;
		}else{
			$("#highlight-toggle").addClass("checked");
			$("#highlight-info").show();
			highlight_keywords = true;
		}
	}

	var init_results = function(){
		$scope.results.forEach(function(result){
  			result.bookmarked = false;
  			result.abstract = $sce.trustAsHtml(String(result.abstract).replace(/<[^>]+>/gm, ''));
  			result.title = $sce.trustAsHtml(String(result.title).replace(/<[^>]+>/gm, ''));
  			var synopsis = ( String(result.abstract).length > 600 ? String(result.abstract).substring(0, 600) + "..." : String(result.abstract) );
  			result.abstract_synopsis = $sce.trustAsHtml(synopsis);
  			result.full_length_abstract = ( String(result.abstract).length == String(result.abstract_synopsis).length );
  		});
	}

	var next_params = function(){
		ids = [];
		$scope.results.forEach(function(result){
			if(result.bookmarked){
				ids.push(result.id);
			}
		});
		if(ids.length > 0){
			return "id=" + ids.join("&id=");
		}else{
			return "";
		}	
	}

	var reset_variables = function(){
		iteration = 1;
		$scope.bookmark_history_showing = false;
		$scope.bookmark_history = [];
		$scope.results = [];
		$scope.keywords = {};
	}

	$("#highlight-info .dropdown-menu ul li a").live("click", function(){
		$scope.selected_highlight_color = $scope.highlight_colors[parseInt($("#highlight-color option:selected").val())];
		highlight();
		$scope.$apply();
	});

	$(window).on("keydown", function( event ) {
		if(event.which == 39){
			$scope.next();
		}else if(event.which == 27){
			$scope.end();
		}
	});
	
}]);