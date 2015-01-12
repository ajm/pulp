$(".loading-layer").ready(function(){
    $(".loading-layer").show();
});

var UTILS = (function(){

    var shuffle = function (o){
        for(var j, x, i = o.length; i; j = Math.floor(Math.random() * i), x = o[--i], o[i] = o[j], o[j] = x);
        return o;
    }

    var synopsis = function(text, max_length){
        if(text.length > max_length){
            return text.substring(0, max_length) + "...";
        }else{
            return text;
        }
    }

    var highlight_single_abstract = function(abstract, keyword){
        var words = abstract.split(" ");
        var highlighted_index = 0;
        for(var i=0; i<words.length; i++){
            if(words[i].toLowerCase() == keyword.toLowerCase()){
                words[i] = "<span class='highlighted-word'>" + keyword + "</span>";
                highlighted_index = i;
            }
        }

        var slice_start = Math.max(highlighted_index-7, 0);
        var slice_end = Math.min(highlighted_index+7, words.length);

        var start_ellipsis = ( slice_start > 0 ? "..." : "" );
        var end_ellipsis = ( slice_end < words.length -1 ? "..." : "" );

        words = words.slice(slice_start, slice_end); 

        return (  "\"" + start_ellipsis + words.join(" ") + end_ellipsis  + "\"" );
    }

    var highlight_abstracts = function(abstracts, keyword){
        var highlighted = [];
        var locations = {};

        for(var i=0; i<15; i++){
            highlighted[i] = "";
            locations[i] = false;
        }

        abstracts.forEach(function(abstract){
            var location = Math.floor(Math.random() * 15);
            while(locations[location]){
                location = Math.floor(Math.random() * 15);
            }
            locations[location] = true;
            highlighted[location] = highlight_single_abstract(abstract, keyword);
        });

        $(".abstract-highlights-container").fadeIn(300);
        $(".abstract-highlights-container").html(Mustache.to_html($("#abstract-highlight-template").html(), { abstract_highlights: highlighted }));
    }

    return {
        shuffle: shuffle,
        synopsis: synopsis,
        highlight_abstracts: highlight_abstracts
    };

})();

var VISUALIZATION = (function(UTILS){

    $clusters = [];
    $current_cluster_group = 0;
    $base_size = 100;
    $cluster_size = 10;
    $cluster_coloring = {};
    $articles = [];
    $articles_by_id = {};
    $keywords = {};
    $group_keywords = {};

    var construct_cluster_group = function(){

        var data = fetch_data($current_cluster_group * $cluster_size, 50);

        var clusters = construct_clusters(data);
        var group = [];
        var count = 0;

        for(var i=0; i<Math.min(clusters.length, $cluster_size); i++){
            if(clusters[i].middle.mean * $base_size < 10){
                break;
            }

            group.push(clusters[i]);
            count++;
        }

        $current_cluster_group += count;

        return group;
    }

    var bind_all = function(){
        $(".article-bubble").fadeIn(300);

        $(".color-palet-divider").tooltip();

        $(".keyword").hover(function(){
            $(this).css("z-index","1010");
            highlight_articles_containing_keyword(parseInt($(this).attr("data-group")), $(this).text());
        }, function(){
            $(this).css("z-index", "0");
            un_highlight_all();
        });

        $(".article-bubble").popover({ trigger: "manual", html: true})
        .on("mouseenter", function () {
            var _this = this;
            $(this).popover("show");
            $(".popover").on("mouseleave", function () {
                $(_this).popover('hide');
            });
        }).on("mouseleave", function () {
            var _this = this;
            if (!$(".popover:hover").length) {
                    $(_this).popover("hide")
                }
            setTimeout(function () {
                
            }, 100);
        });

        $(".article-bubble").hover(function(){
            $(this).css("z-index","1000");
            $(".bubble-layer").show();
            $(".bubble-layer").stop().animate({ opacity: 1 }, 300);
        }, function(){
            var bubble = this;
            $(".bubble-layer").stop().animate({ opacity: 0 }, function(){
                $(".bubble-layer").hide();
                $(bubble).css("z-index","0");
            });
        });
    }

    var render = function(){
        $(".loading-layer").stop().fadeIn(300);

        var group = construct_cluster_group();
        if(group.length != 0){
            $(".visualization-container").append(Mustache.to_html($("#cluster-group-template").html(), { cluster_groups: group }));
        }else{
            $(".visualization-over-container").show();
        }

        $(".article-bubble").addClass("animated bounceIn");

        setTimeout(function(){
            $(".article-bubble").removeClass("animated bounceIn");
        }, 1000);

        $(".loading-layer").stop().fadeOut(300);

        bind_all();
    }

    var separate_into_clusters = function(data){
        var clusters = [];
        var current_cluster = 0;
        var counter = $current_cluster_group * $cluster_size + $cluster_size;

        for(var i=0; i<data.length; i++){
            if(!clusters[current_cluster]){
                clusters[current_cluster] = {
                    middle: data[i],
                    surround: [],
                    counter: counter
                }
                counter += $cluster_size;
            }else{
                clusters[current_cluster].surround.push(data[i]);
            }

            if(i != 0 && i%$cluster_size == 0){
                current_cluster++;
            }
        }   

        return clusters;
    }

    

    var fetch_data = function(start, count){

        if($articles.length == 0){
            $.ajax({
                url: "/state",
                type: "GET",
                async: false
            }).done(function(data){
                for(article in data.article_data){
                    var current = data.article_data[article];
                    var mean = current[0];
                    var variance = current[1];
                    var current_article = data.all_articles[article];
                    var obj = {
                        id: article,
                        mean: mean,
                        title: current_article.title,
                        abstract: current_article.abstract.replace(/<[^>]+>/gm, ''),
                        abstract_synopsis: UTILS.synopsis(current_article.abstract.replace(/<[^>]+>/gm, ''), 250),
                        link: current_article.url,
                        variance: variance,
                        visual: { width: mean * $base_size, height: mean * $base_size, opacity: -1 * variance + 1 }
                    };
                    $articles_by_id[article] = obj;
                    $articles.push(obj);
                }
                $keywords = data.keywords;
                $articles.sort(function(a, b){
                    return b.mean - a.mean;
                });
            });
            return $articles.slice(0, count);
        }else{
            return $articles.slice(start, Math.min($articles.length, start + count));
        }
    }


    var highlight_articles_containing_keyword = function(cluster_id, keyword){
        var articles = $group_keywords[cluster_id][keyword];
        var abstracts = $.map(articles, function(article){
            return $articles_by_id[article].abstract;
        });

        UTILS.highlight_abstracts(abstracts, keyword);

        if(articles.length > 0){
            articles.forEach(function(article){
                var el = ".article-bubble[data-article-id='" + article + "']"; 
                $(el).css("z-index","1000");
                $(el).css("transform", "scale(1.25");
                $(".bubble-layer").show();
                $(".bubble-layer").stop().animate({ opacity: 1 }, 300);
            });
        }
    }

    var un_highlight_all = function(){
        $(".abstract-highlights-container").fadeOut(300);
        $(".bubble-layer").stop().animate({ opacity: 0 }, function(){
            $(".bubble-layer").hide();
            $(".article-bubble").css("z-index","0");
            $(".article-bubble").css("transform", "scale(1)");
        });
    }

    var common_keywords = function(cluster, count){
        var articles = cluster.surround.concat([cluster.middle]);

        $group_keywords[cluster.counter] = {};

        articles.forEach(function(article){
            var abstract = article.abstract;
            var words = abstract.split(" ");
            var seen_words = {};

            words.forEach(function(word){
                word = word.toLowerCase();
                if(!seen_words[word]){
                    if(!$group_keywords[cluster.counter][word]){
                        $group_keywords[cluster.counter][word] = [article.id];

                    }else{
                        $group_keywords[cluster.counter][word].push(article.id);
                    }
                    seen_words[word] = true;
                }
            });
        });

        var word_points = [];

        for(word in $group_keywords[cluster.counter]){
            var value = 0;
            if($keywords[word]){
                value = ( $group_keywords[cluster.counter][word].length + 1 ) * $keywords[word]
            }
            word_points.push({ points: value, keyword: word });

        }

        word_points.sort(function(a, b){
            return b.points - a.points;
        });

        return word_points.slice(0, count);
    }

    var construct_clusters = function(data){
        var cluster_arr = [];
        var clusters = separate_into_clusters(data);
        clusters.forEach(function(cluster){
            
            var cluster_color = [Math.round(Math.random()*240), Math.round(Math.random()*240), Math.round(Math.random()*240)].join(",");
            while($cluster_coloring[cluster_color]){
                cluster_color = [Math.round(Math.random()*240), Math.round(Math.random()*240), Math.round(Math.random()*240)].join(",");
                $cluster_coloring[cluster_color] = cluster_color;
            }

            cluster_min_top = Math.pow(10,12);
            cluster_min_left = Math.pow(10,12);
            cluster_max_top = 0;
            cluster_max_left = 0;
            
            var unit_vector = { x: 0, y: 1 };
            var iteration_angle = (2 * Math.PI)/cluster.surround.length;
            var current_angle = 0;
            var max_mean_diff = Math.abs(cluster.middle.mean - cluster.surround[cluster.surround.length-1].mean);

            cluster.surround = UTILS.shuffle(cluster.surround);
            cluster.surround.forEach(function(surround){
                
                var vector_width =  Math.max(cluster.middle.visual.width, Math.abs(cluster.middle.mean - surround.mean) / max_mean_diff * 300);

                surround.vector = { x: unit_vector.x * vector_width, y: unit_vector.y * vector_width };

                current_angle += iteration_angle;
                unit_vector.x = 0 * Math.cos(current_angle) - 1 * Math.sin(current_angle);
                unit_vector.y = 0 * Math.sin(current_angle) + 1 * Math.cos(current_angle);

                if(surround.vector.x + surround.visual.width > cluster_max_left){
                    cluster_max_left = surround.vector.x + surround.visual.width;
                }
                if(surround.vector.x < cluster_min_left){
                    cluster_min_left = surround.vector.x;
                }
                if(surround.vector.y + surround.visual.height > cluster_max_top){
                    cluster_max_top = surround.vector.y + surround.visual.height;
                }
                if(surround.vector.y < cluster_min_top){
                    cluster_min_top = surround.vector.y;
                }

            });
            
            cluster.color = cluster_color;
            cluster.width = cluster_max_left + Math.abs(cluster_min_left);
            cluster.height = cluster_max_top + Math.abs(cluster_min_top);
            cluster.middle.visual.x = Math.abs(cluster_min_left);
            cluster.middle.visual.y = Math.abs(cluster_min_top);
            cluster.middle.visual.color = cluster.color;

            var cluster_articles = cluster.surround.concat([cluster.middle]);
            cluster.common_keywords = common_keywords(cluster, 5);

            cluster.surround.forEach(function(surround){
                surround.visual.x = cluster.middle.visual.x + surround.vector.x;
                surround.visual.y = cluster.middle.visual.y + surround.vector.y;
                surround.visual.color = cluster.color;
            });

            cluster_arr.push(cluster); 
        });
        
        return cluster_arr;
    }

    return {
        render: render
    }

})(UTILS);

$(window).scroll(function() {
    if(document.documentElement.clientHeight + $(document).scrollTop() >= document.body.offsetHeight){ 
        VISUALIZATION.render();
    }
});
    
$(document).bind("ready", function(){
    VISUALIZATION.render();

    $("#visualization-info-modal").draggable();
});
