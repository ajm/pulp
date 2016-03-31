SearchApp.controller("SearchController", ["$scope", "$rootScope","$sce", "$location", "$interval", "Api", "Classifier", "QueryService", function($scope, $rootScope, $sce, $location, $interval, Api, Classifier, QueryService){

	$scope.topics_pointer = 0;
	$scope.chosen_highlight_color_index = 0;
	$scope.result_count = 20;
	$scope.bookmark_history = [];
	$scope.results = [];
	$scope.highlight_colors = UI.highlight_colors;
	$scope.selected_highlight_color = UI.highlight_colors[0];
  $scope.iteration = 1;

	var first_iteration_started = null;
	var keywords = {};

	$scope.search = function(){
		reset_variables();

    $scope.searching = true;
    $scope.loading = true;

    Api.search({ keyword: $scope.search_keyword, count: parseInt($scope.result_count), participant_id: $rootScope.settings.participant_id })
		.success(function(response){
      $scope.results = response.articles;
			$scope.visualization_data = { topics: response.topics, append: false };
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

	$scope.article_in_view = function(result){
		result.seen = true;
	}

  $scope.touch_article = function(article){
		$rootScope.experiment_data.articles.push({
				id: article.id,
				title: article.raw_title,
				url: article.url,
				rating: 1
		});

    article.clicked = true;
    article.reading_started = new Date();

    $scope.viewed_article = article;
  }

  $scope.close_article_view = function(){
    var now = new Date();
    var start = $scope.viewed_article.reading_started;
    var diff = (now.getTime() - start.getTime()) / 1000;

    $scope.viewed_article.reading_ended = now;
    $scope.viewed_article.reading_time = diff;
    $scope.viewed_article = null;
  }

	$scope.toggle_bookmark = function(result){
		result.bookmarked = !result.bookmarked;

		if(result.bookmarked){
			$rootScope.experiment_data.articles.push({
					id: result.id,
					title: result.raw_title,
					url: result.url,
					rating: 1
			});
		}else{
			_($rootScope.experiment_data.articles).remove(function(article){
				return article.id == result.id
			});
		}
	}

	$scope.next = function(){
		var options = {
			results: $scope.results,
			participant_id: $rootScope.settings.participant_id
		};
/*
		if($scope.iteration == 1){
			options.exploratory = is_exploratory() ? 1 : 0;
			$rootScope.experiment_data.classifier_value = ( options.exploratory == 1 ? 'exploratory' : 'look up' )
		}
*/
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

        if($scope.iteration == $rootScope.max_iterations) {
            Api.end(options).success(function(){
                $location.path('/settings');
            });
        }
        else {
            Api.next(options).success(function(response){
                $scope.results = response.articles;
			    $scope.visualization_data = { topics: response.topics, append: false };
			    $scope.loading = false;

                keywords = response.keywords;
                init_results();

                $scope.iteration++;

                $scope.search_heading = $scope.search_keyword;

                if($scope.highlight_keywords){
                    highlight();
                }
            }).error(function(){
                $scope.results = [];
                $scope.loading = false;
            });
	    }
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
		if($scope.viewed_article){
			var now = new Date();
	    var start = $scope.viewed_article.reading_started;
	    var diff = (now.getTime() - start.getTime()) / 1000;

	    $scope.viewed_article.reading_ended = now;
	    $scope.viewed_article.reading_time = diff;
		}

		var options = {
			results: $scope.results,
			participant_id: $rootScope.settings.participant_id
		};

		//$interval.cancel(query_timer);

		Api.end(options).success(function(){
			/*$rootScope.experiment_data.articles = _.uniq($rootScope.experiment_data.articles, function(article){
				return article.id;
			});

			alert('The query has ended!');

			$location.path('/ratings');*/

			$location.path('/settings');
		});
	}

	$scope.more_topics = function(){
		$scope.topics_pointer += 100;

		$scope.loading_topics = true;

		Api.topics({ from: $scope.topics_pointer, to: $scope.topics_pointer + 100, participant_id: $rootScope.settings.participant_id, normalise: 0 })
			.then(function(topics){
				$scope.visualization_data = { topics: topics.data, append: true };
				$scope.loading_topics = false;
			});
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

	$scope.toggle_plain_abstract = function(result){
		result.show_plain_abstract = !result.show_plain_abstract;
	}

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

	var init_results = function(articles){
		$scope.topics = [];

		$scope.results.forEach(function(result){
  			result.bookmarked = false;
				result.plain_abstract = $sce.trustAsHtml(result.abstract);
  			result.title = $sce.trustAsHtml(String(result.title).replace(/<[^>]+>/gm, ''));
				result.raw_title = String(result.title).replace(/<[^>]+>/gm, '');
				result.author = $sce.trustAsHtml(result.author);

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

		return Classifier.is_exploratory(params);
  }

	$scope.$watch('chosen_highlight_color_index', function(newVal, oldVal){
		$scope.selected_highlight_color = $scope.highlight_colors[parseInt(newVal)];
		highlight();
	});

	QueryService.setYearRange({ from: $location.search().year_from || 1993, to: $location.search().year_to || 2100 })
	//QueryService.setQuery($location.search().query || ''); // uncomment to go back to search bar

	$scope.search_keyword = QueryService.getQuery();

	if($scope.search_keyword){
		$scope.search();
	}
}]);
