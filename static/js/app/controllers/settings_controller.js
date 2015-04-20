SearchApp.controller('SettingsController', function($scope, $rootScope, Api){
  $scope.setup = function(){
    Api.setup({
      participant_id: $rootScope.settings.participant_id,
      exploration_rate: $rootScope.settings.exploration_rate,
      task_type: $rootScope.settings.task_type
    }).success(function(){
      $scope.setup_saved = true;
    });
  }
});
