function setupButtons() {
    
    d3.select('#pcbutton')
        .on('click', function(d) {
            d3.json("data/hacker_links.json",
                function(d) {
                    draw(d, 'pc0', 'pc1', 'Python', 'Javascript');
                })
            });

    d3.select('#contributionsbutton')
        .on('click', function(d) {
            d3.json("data/hacker_links.json",
                function(d) {
                    draw(d, 'total_collaboration', 'hs_collaboration',
                        'Total Collaboration', 'Hacker School Collaboration');
                })
            });

}


function draw(data, xval, yval, xlab, ylab) {
    "use strict";

    // main body
    var margin = 50,
        height = 400,
        width = 600,
        x_extent = d3.extent(data.nodes, function(d) { return d[xval] }),
        y_extent = d3.extent(data.nodes, function(d) { return d[yval] });

    console.log(y_extent)

    var x_scale = d3.scale.sqrt()
        .range([margin, width-margin])
        .domain(x_extent);

    var y_scale = d3.scale.sqrt()
        .range([height-margin, margin]) // margin-height to reverse direction
        .domain(y_extent);

    var xfunc = function(d) {return x_scale(d[xval])};
    var yfunc = function(d) {return y_scale(d[yval])};

    var svg = document.getElementById('mainSVG')
    while (svg.lastChild) {
        svg.removeChild(svg.lastChild);
    }

    var hackersDiv = document.getElementById('hackers')
    while (hackersDiv.lastChild) {
        hackersDiv.removeChild(hackersDiv.lastChild);
    }

    var collaboratorsDiv = document.getElementById('collaborators')
    while (collaboratorsDiv.lastChild) {
        collaboratorsDiv.removeChild(collaboratorsDiv.lastChild);
    }

    d3.select('#mainSVG')
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

    d3.select('.x.axis')
    .append('text')
    .text(xlab)
    .attr('x', function(){return (width / 2) - margin})
    .attr('y', margin/1.5);

     d3.select('.y.axis')
    .append('text')
    .text(ylab)
    .attr('transform', "rotate (-90, -30, 0) translate(-240)")

    // pictures
    d3.select('#hackers')
        .selectAll('img')
        .data(data.nodes)
        .enter()
        .append('img')
        .attr('height', '30px')
        .attr('width', '30px')
        .attr('src', function(d) {return d.avatar_url})
        .attr('title', function(d) {return d.login})
        .on('click', function(d) {selectHacker(d, data.links, data.nodes, xfunc, yfunc)}); 

    // nodes
    drawNodes(data, xfunc, yfunc);
    drawLinks([], data.nodes, xfunc, yfunc);

}


function selectHacker(hacker, links, nodes, xfunc, yfunc) {

    var id = hacker.id;

    var filteredlinks = links.filter(
            function(l) {return l.source == id || l.target == id}
            );

    drawLinks(filteredlinks, nodes, xfunc, yfunc);

    var hackerIDs = _.union(
            _.map(filteredlinks, function(l) {return l.source}),
            _.map(filteredlinks, function(l) {return l.target}));

    hackerIDs = [id].concat(_.without(hackerIDs, id));

    var hackers = _.map(hackerIDs, function(n) {return nodes[n]});

    d3.select('#collaborators')
        .selectAll('div')
        .data([])
        .exit()
        .remove();

    var divs = d3.select('#collaborators')
        .selectAll('div')
        .data(hackers)
        .enter()
        .append('div')
        .attr('class', 'collaborator')
        .attr('height', '40px')
        .attr('width', '200px')

        divs.append('img')
        .attr('class', 'collaborator-image')
        .attr('height', '30px')
        .attr('width', '30px')
        .attr('vertical-align', 'center')
        .attr('src', function(d) {return d.avatar_url})
        .attr('title', function(d) {return d.login})

        divs.append('div')
        .attr('class', 'collaborator-name')
        .append('span')
        .text(function(d) {return d.login});

}


function drawLinks(links, nodes, xfunc, yfunc) {

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
        .attr('x1', function(d) {return xfunc(nodes[d.source])})
        .attr('y1', function(d) {return yfunc(nodes[d.source])})
        .attr('x2', function(d) {return xfunc(nodes[d.target])})
        .attr('y2', function(d) {return yfunc(nodes[d.target])})
        .style('stroke', 'rgb(0, 52, 72)')
        .style('alpha', 1)
        .style('stroke-width', 1);

} 


function drawNodes(data, xfunc, yfunc) {

    d3.select('svg')
        .selectAll('circle')
        .data(data.nodes)
        .enter()
        .append('circle')
        .attr('cx', function(d) {return xfunc(d)})
        .attr('cy', function(d) {return yfunc(d)})
        .attr('r', function(d) {return 6})
        .on('click', function(d) {selectHacker(d, data.links, data.nodes, xfunc, yfunc)})
        .append("svg:title")
        .text(function(d) { return d.login; });

}

