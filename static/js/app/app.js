MathJax.Hub.Config({
		tex2jax: {
		    inlineMath: [['$','$'], ['\\(','\\)']],
		    processEscapes: true
		    }
});

MathJax.Hub.Configured();

var SearchApp = angular.module("SearchApp", ["ngRoute", "angular-bootstrap-select", "angular-inview", "ui.bootstrap"]);

SearchApp.config(function($routeProvider){
	$routeProvider
	.when('/', {
		controller: 'SearchController',
		templateUrl: 'static/js/app/views/search.html'
	})
	.when('/settings', {
		controller: 'SettingsController',
		templateUrl: 'static/js/app/views/settings.html'
	})
	.when('/ratings', {
		controller: 'RatingsController',
		templateUrl: 'static/js/app/views/ratings.html'
	})
	.otherwise({
		redirectTo: '/settings'
	});
});

SearchApp.run(function($rootScope){
	$rootScope.settings = {
		participant_id: '',
		task_type: 0,
		exploration_rate: 0,
		query_time: 15,
		study_type: 1
	};

	$rootScope.experiment_data = {
		articles: [],
		query: null,
		classifier_value: null
	};
});

SearchApp.filter("strip_tags", function(){
	return function(text){
		return String(text).replace(/<[^>]+>/gm, '');
	};
});

SearchApp.filter('html', function($sce){
  return function(input){
    return $sce.trustAsHtml(input);
  }
});

SearchApp.filter("synopsis", function(){
	return function(text){
		return ( String(text).length > 300 ? String(text).substring(0,300) + "..." : String(text) );
	}
});
