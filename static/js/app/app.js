var SearchApp = angular.module("SearchApp", ["ngRoute", "angular-bootstrap-select"]);

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
	.otherwise({
		redirectTo: '/'
	});
});

SearchApp.run(function($rootScope){
	$rootScope.settings = {
		participant_id: '',
		task_type: 0,
		exploration_rate: 0,
		query_time: 15
	};
});

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
