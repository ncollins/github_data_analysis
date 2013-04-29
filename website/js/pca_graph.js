function draw(data) {
    "use strict";

    // helper functions
    
   function drawLinks(links) {

        var lines = d3.select('svg')
            .selectAll('line')
            .data([])
            .exit()
            .remove();

        var lines = d3.select('svg')
            .selectAll('line')
            .data(links)
            .enter()
            .append('svg:line')
            .attr('x1', function(d) {return x_scale(d.x1)})
            .attr('y1', function(d) {return y_scale(d.y1)})
            .attr('x2', function(d) {return x_scale(d.x2)})
            .attr('y2', function(d) {return y_scale(d.y2)})
            .style('stroke', 'rgb(0, 52, 72)')
            .style('alpha', 1)
            .style('stroke-width', 1);
    } 
   
    function drawHackerLinks(hacker) {
        var id = hacker.id;
        var filteredlinks = _.filter(data.links,
                function(l) {
                    return l.source == id || l.target == id
                });

        drawLinks(filteredlinks);

        var hackerIDs = _.union(
                _.map(filteredlinks, function(l) {return l.source}),
                _.map(filteredlinks, function(l) {return l.target}));

        var hackers = _.map(
                hackerIDs,
                function(n) {return data.nodes[n]});

        d3.select('#collaborators')
        .selectAll('img')
        .data([])
        .exit()
        .remove();

        d3.select('#collaborators')
        .selectAll('img')
        .data(hackers)
        .enter()
        .append('img')
        .attr('height', '40px')
        .attr('width', '40px')
        .attr('src', function(d) {return d.avatar_url})
        .attr('title', function(d) {return d.login});

    }

    // main body

    var margin = 50,
        height = 500,
        width = 600,
        x_extent = d3.extent(data.nodes, function(d) {return d.x}),
        y_extent = d3.extent(data.nodes, function(d) {return d.y});

    var x_scale = d3.scale.sqrt()
        .range([margin, width-margin])
        .domain(x_extent);

    var y_scale = d3.scale.sqrt()
        .range([height-margin, margin]) // margin-height to reverse direction
        .domain(y_extent);

    d3.select('#graph')
    .append('svg')
    .attr('width', width)
    .attr('height', height);

    var x_axis = d3.svg.axis().scale(x_scale);
    var y_axis = d3.svg.axis().scale(y_scale).orient('left');

    d3.select('svg')
    .append('g')
    .attr('class', 'x axis')
    .attr('transform', 'translate(0,' + (height-margin) + ')')
    .call(x_axis);

    d3.select('svg')
    .append('g')
    .attr('class', 'y axis')
    .attr('transform', 'translate(' + margin + ',0)')
    .call(y_axis);

    drawLinks(data.links);

    d3.select('svg')
        .selectAll('circle')
        .data(data.nodes)
        .enter()
        .append('circle')
        .attr('cx', function(d) {return x_scale(d.x)})
        .attr('cy', function(d) {return y_scale(d.y)})
        .attr('r', function(d) {return 6})
        .append("svg:title")
        .text(function(d) { return d.login; })
        .attr("xlink:href", function(d) {
            return d.url
        });


    // pictures

    d3.select('#hackers')
    .selectAll('img')
    .data(data.nodes)
    .enter()
    .append('img')
    .attr('height', '40px')
    .attr('width', '40px')
    .attr('src', function(d) {return d.avatar_url})
    .attr('title', function(d) {return d.login})
    .on('click', drawHackerLinks);

}

