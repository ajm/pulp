SearchApp.controller('RatingsController', function($scope, $rootScope, $location, Api){
  if(!$rootScope.settings || !$rootScope.settings.participant_id){
      $location.path('/settings');
  }

  $scope.save_ratings = function(){
    var ratings = _($rootScope.experiment_data.articles)
      .map(function(article){
        return {
          title: article.title,
          rating: article.rating
        }
      });

    Api.ratings({
      participant_id: $rootScope.settings.participant_id,
      task_type: $rootScope.settings.task_type == 0 ? 'exploratory' : 'look up',
      study_type: $rootScope.settings.study_type == 1 ? 'full system' : 'baseline',
      classifier_value: $rootScope.experiment_data.classifier_value,
      query: $rootScope.experiment_data.query,
      ratings: ratings
    }).success(function(res){
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

      alert('Thanks for participating!');

      $location.path('/settings');
    });
  }
});
