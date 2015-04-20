SearchApp.service('Classifier', function(){
  this.is_exploratory = function(options){
    var query_length = options.query_length;
    var reading_time = options.reading_time;
    var cumulative_clicks = options.clicks_count;
    var scroll_depth = options.seen_count;
    var query_duration = options.query_duration;

    Exploratory = true;
    if (query_length <= 5) {
    	if (reading_time <= 131) {
    		if (cumulative_clicks <=0) {
    			Exploratory = true;
    		}
    		else if (cumulative_clicks > 0) {
    			Exploratory = false;

    		}
    	} else if (reading_time > 131) {
    		if (query_length <= 3) {
    			Exploratory = true;
    		}
    		else if (query_length > 3) {
    			if (cumulative_clicks <= 2) {
    				Exploratory = true;
    			}
    			else if (cumulative_clicks > 2) {
    				Exploratory =false;
    			}
    		}
    	}
    }
    else if( query_length > 5){
    	Exploratory = false;
    }

    return Exploratory;
  }
});
