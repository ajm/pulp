SearchApp.controller('SettingsController', function($scope, $rootScope, $location, Api, QueryService){

  //$rootScope.settings.search_query = $location.search().query || '';

  //QueryService.setYearRange({ from: $location.search().year_from, to: $location.search().year_to });
  //QueryService.setQuery($location.search().query || ''); // comment out to go back to search bar

  $scope.setup = function(){

    QueryService.setQuery($rootScope.settings.search_query || '')
    $rootScope.max_iterations = parseInt($rootScope.settings.query_iterations)

    Api.setup({
      participant_id: $rootScope.settings.participant_id,
      exploration_rate: $rootScope.settings.exploration_rate,
      q: $rootScope.settings.search_query,
      model: $rootScope.settings.model,
      article_count: $rootScope.settings.article_count,
      iteration_count: $rootScope.settings.query_iterations,
      knowledge_level: $rootScope.settings.knowledge_level
      //task_type: $rootScope.settings.task_type,
      //study_type: $rootScope.settings.study_type
    }).success(function(){
      $rootScope.experiment_data.query = $rootScope.settings.search_query
      $scope.setup_saved = true;
    });
  }
});
