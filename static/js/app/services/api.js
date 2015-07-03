SearchApp.service('Api', function($http){
  function parseIterationData(options){
    return {
      selected: _.chain(options.results).where({ bookmarked: true }).map(function(bookmark){ return bookmark.id }).value(),
      participant_id: options.participant_id,
      clicked: _.chain(options.results).where({ clicked: true }).map(function(clicked){ return { id: clicked.id, reading_started: clicked.reading_started.getTime() / 1000, reading_ended: clicked.reading_ended.getTime() / 1000 } }).value(),
      seen: _.chain(options.results).where({ seen: true }).map(function(seen){ return seen.id }).value()
    }
  }

  this.next = function(options){
    var params = parseIterationData(options);

    if(options.exploratory == 0 || options.exploratory == 1){
      params.exploratory = options.exploratory;
    }

    return $http.post('/next', params);
  }

  this.search = function(options){
    return $http.get('/query', { params: { 'q': options.keyword, 'article-count': options.count, 'participant_id': options.participant_id } });
  }

  this.setup = function(options){
    return $http.get('/setup', { params: { participant_id: options.participant_id, task_type: options.task_type, exploration_rate: options.exploration_rate, experiment_id: options.study_type, baseline_system: ( options.baseline_system ? 1 : 0 ) } })
  }

  this.end = function(options){
    var params = parseIterationData(options);

    return $http.post('/end', params);
  }
});
