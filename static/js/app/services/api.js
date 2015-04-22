SearchApp.service('Api', function($http){
  this.next = function(options){
    var params = {
      selected: _.chain(options.results).where({ bookmarked: true }).map(function(bookmark){ return bookmark.id }).value(),
      participant_id: options.participant_id,
      clicked: _.chain(options.results).where({ clicked: true }).map(function(clicked){ return { id: clicked.id, reading_started: clicked.reading_started.getTime() / 1000, reading_ended: clicked.reading_ended.getTime() / 1000 } }).value(),
      seen: _.chain(options.results).where({ seen: true }).map(function(seen){ return seen.id }).value()
    }

    if(options.exploratory == 0 || options.exploratory == 1){
      params.exploratory = options.exploratory;
    }

    return $http.post('/next', params);
  }

  this.search = function(options){
    return $http.get('/query', { params: { 'q': options.keyword, 'article-count': options.count, 'participant_id': options.participant_id } });
  }

  this.setup = function(options){
    return $http.get('/setup', { params: { participant_id: options.participant_id, task_type: options.task_type, exploration_rate: options.exploration_rate, experiment_id: options.study_type } })
  }

  this.end = function(options){
    return $http.get('/end', { params: { participant_id: options.participant_id } });
  }
});
