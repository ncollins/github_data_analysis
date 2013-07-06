/*global d3, _ */
/*jslint browser: true*/

function setup_chord(data) {
    "use strict";

    var id, filteredlinks, selected_hackers, matrix;

    // BASE DATA

    var hackers = data.nodes.map(function (d) {
        d.selected = false;
        return d;
    });

    _.each([52,31,43,8,29,16,11,1,3], function (i) {
        hackers[i].selected = true;
    });

    // SETUP

    var width = 1000,
        height = 600,
        innerRadius = Math.min(width, height) *  .3, //.41,
        outerRadius = innerRadius * 1.1;

    var fill = d3.scale.ordinal()
        .domain(d3.range(4))
        .range(["#000000", "#FFDD89", "#957244", "#F26223"]);

    var svg = d3.select("#mainSVG") //.append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

    d3.select("#mainSVG")
        .append("defs")
        .selectAll("pattern")
        .data(hackers)
        .enter()
        .append("pattern")
        .attr("id", function (d) { return "avatar-" + d.login; })
        .attr("height", 30)
        .attr("width", 30)
        .attr("x", 0)
        .attr("y", 0)
        .attr("patternUnits", "userSpaceOnUse")
        .attr("patternUnits", "objectBoundingBox")
        .append("image")
        .attr("height", 30)
        .attr("width", 30)
        .attr("x", 0)
        .attr("y", 0)
        .attr("xlink:href", function (d) {
            return d.avatar_url;
        });



    selected_hackers = _.filter(hackers, function (d) { return d.selected });

    function connection_matrix(selected_hackers) {
        var matrix = [];

        var index = {};
        for (var i = 0; i < selected_hackers.length; i++) {
            matrix[i] = [];
            index[selected_hackers[i].id] = i;
            for (var j = 0; j < selected_hackers.length; j++) {
                matrix[i].push(0);
            }
        }

        _.each(data.links,
                function (l) {
                    var selected_ids = _.map(selected_hackers, function (d) { return d.id });
                    if (_.contains(selected_ids, l.source) && _.contains(selected_ids, l.target)) {
                        matrix[index[l.source]][index[l.target]] = l.weight;
                        matrix[index[l.target]][index[l.source]] = l.weight;
                    }
                }
              );

        return matrix;
    }

    matrix = connection_matrix(selected_hackers);

    /*
       var chord = d3.layout.chord()
       .padding(.05)
       .sortSubgroups(d3.descending)
       .matrix(matrix);
       */

    var matrix2chord = d3.layout.chord().padding(.05).sortSubgroups(d3.descending).matrix,
        chord = matrix2chord(matrix);

    svg.append("g")
        .attr("class", "groups")
        .selectAll("g")
        .data(chord.groups)
        .enter()
        .append("g")
        .attr("class", "group")
        .append("svg:path")
        .style("fill", function(d) { return fill(d.index); })
        .style("stroke", function(d) { return fill(d.index); })
        .attr("d", d3.svg.arc().innerRadius(innerRadius).outerRadius(outerRadius))
        .attr("id", function (d) { return "group" + d.index /*+ "-" + j*/; })
        .on("mouseover", fade(.1))
        .on("mouseout", fade(1));

    var total = _.reduce(chord.groups(), function (acc, d) {return acc + d.value}, 0);

    svg.selectAll(".group")
        .append("svg:text")
        .attr("x", 6)
        .attr("dy", 15)
        .filter(function (d) {
            //return true;
            return d.value > total / 6;
        })
    .append("svg:textPath")
        .attr("xlink:href", function (d) { return "#group" + d.index /*+ "-" + j*/; })
        .text(function (d) {
            //console.log('test');
            return selected_hackers[d.index].login
        });

    // Returns an array of tick angles and labels, given a group.
    function groupTicks(d) {
        var k = (d.endAngle - d.startAngle) / d.value;
        return d3.range(0, d.value, 10).map(function(v, i) {
            return {
                angle: v * k + d.startAngle,
               label: i % 5 ? null : v / 10
            };
        });
    }

    // Returns an event handler for fading a given chord group.
    function fade(opacity) {
        return function(g, i) {
            svg.selectAll(".chords path")
                .filter(function(d) { return d.source.index != i && d.target.index != i; })
                .transition()
                .style("opacity", opacity);
        };
    }

    svg.append("g")
        .attr("class", "chords")
        .selectAll("path")
        .data(chord.chords)
        .enter().append("path")
        .attr("class", "chord")
        .attr("d", d3.svg.chord().radius(innerRadius))
        .style("fill", function(d) { return fill(d.target.index); })
        .style("opacity", 1);

    // selection callback

    function select(d) {
        d.selected = !d.selected;
        console.log('selected: ' + d.login);
        var selected_hackers = _.filter(hackers, function (d) { return d.selected });
        console.log('now ' + selected_hackers.length + ' are selected!');
        redraw();
    }

    function redraw() {
        var selected_hackers = _.filter(hackers, function (d) { return d.selected }),
            matrix = connection_matrix(selected_hackers),
            chord = matrix2chord(matrix);

        plot_avatars(chord.groups());
    }

    // AVATARS

    function layout_avatars(hackers, groups) {
        // takes the array of hackers, either with "selected"
        // true or false and the chord groups and adds "x" and "y"
        // coordinates.
        var selected = _.filter(hackers, function (d) { return d.selected }),
            unselected = hackers.filter(function (d) { return !d.selected; });

        for (var i=0; i < unselected.length; i++) {
            var col = i % 4,
                row = Math.floor(i / 4);
            unselected[i].x = 20 + col * 40 - width / 2;
            unselected[i].y = 20 + row * 40 - height / 2;
        }

        var center_x = width / 2,
            angle,
            rotate = - Math.PI / 2;

        for (var i=0; i < selected.length; i++) {
            angle = (groups[i].startAngle + groups[i].endAngle) / 2;
            selected[i].x = 1.2 * outerRadius * Math.cos(rotate + angle);
            selected[i].y = 1.2 * outerRadius * Math.sin(rotate + angle);
        }
    }

    var first_time = true;

    function plot_avatars(groups) {

        layout_avatars(hackers, groups);


        if (first_time) {
            svg.selectAll(".mugshot")
                .data(hackers)
                .enter()
                .append("svg:circle")
                .attr("class", "mugshot")
                .attr("cx", function (d) {return d.x})
                .attr("cy", function (d) {return d.y})
                .attr("r", 15)
                .attr("stroke", "black")
                .attr("stroke-width", 2)
                .attr("fill", function (d) {
                    return "url(#avatar-" + d.login + ")";
                })
            .on('click', select);
            first_time = false;
        }
        else {
            console.log('TRANSITION!');
            svg.selectAll(".mugshot")
                .data(hackers)
                .transition()
                .duration(2000)
                //.append("svg:circle")
                .attr("cx", function (d) {console.log(d.x);return d.x})
                .attr("cy", function (d) {return d.y})
                .attr("r", 15)
                .attr("stroke", "black")
                .attr("stroke-width", 2)
                .attr("fill", function (d) {
                    return "url(#avatar-" + d.login + ")";
                })
            //.on('click', select);
            ;
        }

    }

    plot_avatars(chord.groups());

}
