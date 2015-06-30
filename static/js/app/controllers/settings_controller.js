SearchApp.controller('SettingsController', function($scope, $rootScope, Api){

  $scope.setup = function(){
    Api.setup({
      participant_id: $rootScope.settings.participant_id,
      exploration_rate: ( $rootScope.settings.study_type == 1 ? $rootScope.settings.exploration_rate : 1 ),
      task_type: $rootScope.settings.task_type,
      study_type: $rootScope.settings.study_type
    }).success(function(){
      $scope.setup_saved = true;
    });
  }
});
