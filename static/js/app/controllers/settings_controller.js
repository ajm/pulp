SearchApp.controller('SettingsController', function($scope, $rootScope, $location, Api, QueryService){

  $rootScope.settings.search_query = $location.search().query || '';

  QueryService.setYearRange({ from: $location.search().year_from, to: $location.search().year_to });
  //QueryService.setQuery($location.search().query || '');

  $scope.setup = function(){
    Api.setup({
      participant_id: $rootScope.settings.participant_id,
      exploration_rate: $rootScope.settings.exploration_rate,
      task_type: $rootScope.settings.task_type,
      study_type: $rootScope.settings.study_type
    }).success(function(){
      $rootScope.experiment_data.query = $rootScope.settings.search_query
      $scope.setup_saved = true;
    });
  }
});
