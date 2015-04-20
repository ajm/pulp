SearchApp.controller("SearchController", ["$scope", "$rootScope","$sce", "$location", "Api", "Classifier", function($scope, $rootScope, $sce, $location, Api, Classifier){
	if(!$rootScope.settings || !$rootScope.settings.participant_id){
		$location.path('/settings');
	}

	$scope.chosen_highlight_color_index = 0;
	$scope.result_count = 20;
	$scope.bookmark_history = [];
	$scope.results = [];
	$scope.highlight_colors = UI.highlight_colors;
	$scope.selected_highlight_color = UI.highlight_colors[0];
  $scope.iteration = 1;

  var first_iteration_started = null;
	var keywords = {};

	// SCOPE FUNCTIONS
	$scope.search = function(){
		reset_variables();

    $scope.searching = true;
    $scope.loading = true;

    Api.search({ keyword: $scope.search_keyword, count: parseInt($scope.result_count) })
		.success(function(response){
      $scope.results = response;
      $scope.search_heading = $scope.search_keyword;
      $scope.loading = false;

      init_results();

      first_iteration_started = new Date();
    })
    .error(function(){
      $scope.search_heading = $scope.search_keyword;
      $scope.loading = false;

      $scope.results = [];
    });
	}

	$scope.toggle_bookmark_history = function(){
		$scope.bookmark_history_showing = !$scope.bookmark_history_showing;
	}

  $scope.touch_article = function(article){
    article.clicked = true;
    article.reading_started = new Date();

    $scope.viewed_article = article;
  }

  $scope.close_article_view = function(){
    var now = new Date();
    var start = $scope.viewed_article.reading_started;
    var diff = (now.getTime() - start.getTime()) / 1000;

    delete $scope.viewed_article.reading_started;
    $scope.viewed_article.reading_time = diff;
    $scope.viewed_article = null;
  }

	$scope.toggle_bookmark = function(result){
		result.bookmarked = !result.bookmarked;
	}

	$scope.next = function(){
		var options = {
			results: $scope.results,
			participant_id: $rootScope.settings.participant_id
		};

		if($scope.iteration == 1){
			options.exploratory = is_exploratory() ? 1 : 0;
		}

    UI.back_to_top();

		$scope.bookmark_history_showing = false;

		var history_obj = {
			iteration: $scope.iteration,
			articles: _.where($scope.results, { bookmarked: true })
		}

		if(history_obj.articles.length != 0){
			$scope.bookmark_history.push(history_obj);
		}

    $scope.loading = true;

    Api.next(options).success(function(response){
      $scope.results = response.articles;

      keywords = response.keywords;
      init_results();

      $scope.iteration++;

      $scope.search_heading = $scope.search_keyword;

      if($scope.highlight_keywords){
        highlight();
      }

      $scope.loading = false;
    })
    .error(function(){
      $scope.results = [];

      $scope.loading = false;
    });
	}

	$scope.back_to_top = function(){
		UI.back_to_top();
	}

	$scope.next_is_disabled = function(){
		if($scope.iteration > 1 || _.where($scope.results, { bookmarked: true }).length > 0){
			return false;
		}

		return true;
	}

	$scope.end = function(){
		if(confirm('Are you sure you wan\'t to end this query?')){
			$scope.search_keyword = '';
			$scope.loading = true;

	    Api.end().success(function(){
	      $scope.searching = false;
	      $scope.loading = false;
	    });
		}
	}

	$scope.toggle_highlight = function(){
		$scope.highlight_keywords = !$scope.highlight_keywords;

    if($scope.highlight_keywords){
			highlight();
		}else{
			un_highlight();
		}
	}

	$scope.show_full_abstract = function(result){
		result.abstract_synopsis = result.abstract;
		result.full_length_abstract = true;
	}

	$scope.bookmarked_results = function(result){
		return result.bookmarked == true;
	}

	// PRIVATE FUNCTIONS
	var un_highlight = function(){
		$scope.results.forEach(function(result){
			result.abstract = $sce.trustAsHtml(UI.un_highlight(result.abstract));
			result.abstract_synopsis = $sce.trustAsHtml(UI.un_highlight(result.abstract_synopsis));
			result.title = $sce.trustAsHtml(UI.un_highlight(result.title));
		});
	}

	var highlight = function(){
		un_highlight();

		$scope.results.forEach(function(result){
			result.abstract = $sce.trustAsHtml(UI.highlight(result.abstract, keywords, $scope.selected_highlight_color.rgb));
			result.abstract_synopsis = $sce.trustAsHtml(UI.highlight(result.abstract_synopsis, keywords, $scope.selected_highlight_color.rgb));
			result.title = $sce.trustAsHtml(UI.highlight(result.title, keywords, $scope.selected_highlight_color.rgb));
		});
	}

	var set_highlighting = function (value){
		if(!value){
			$scope.highlight_keywords = false;
		}else{
			$scope.highlight_keywords = true;
		}
	}

	var init_results = function(){
		$scope.results.forEach(function(result){
  			result.bookmarked = false;
  			result.abstract = $sce.trustAsHtml(String(result.abstract).replace(/<[^>]+>/gm, ''));
  			result.title = $sce.trustAsHtml(String(result.title).replace(/<[^>]+>/gm, ''));

        result.trusted_url = $sce.trustAsResourceUrl(result.url);

        var synopsis = ( String(result.abstract).length > 600 ? String(result.abstract).substring(0, 600) + "..." : String(result.abstract) );

        result.abstract_synopsis = $sce.trustAsHtml(synopsis);
  			result.full_length_abstract = ( String(result.abstract).length == String(result.abstract_synopsis).length );
  		});
	}

	var reset_variables = function(){
		$scope.iteration = 1;
		$scope.bookmark_history_showing = false;
		$scope.bookmark_history = [];
		$scope.results = [];
		$scope.keywords = {};
	}

  var is_exploratory = function(){
    var params = {
      query_time: Math.round(( (new Date).getTime() - first_iteration_started.getTime() ) / 1000),
      reading_time: Math.round(_.sum($scope.results, function(result){ return ( result.reading_time || 0 ) })),
			clicked_count: _.where($scope.results, { clicked: true }).length,
			seen_count: _.where($scope.results, { seen: true }).length,
			query_length: $scope.search_heading.split(' ').length
    };

		console.log(params);

		return Classifier.is_exploratory(params);
  }

	$scope.$watch('chosen_highlight_color_index', function(newVal, oldVal){
		$scope.selected_highlight_color = $scope.highlight_colors[parseInt(newVal)];
		highlight();
	});

	$(window).on("keydown", function( event ) {
		if(event.which == 39){
			$scope.next();
		}else if(event.which == 27){
			$scope.end();
		}
	});

}]);
