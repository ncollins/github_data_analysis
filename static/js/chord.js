/*global d3, _ */
/*jslint browser: true*/

function setup_chord(data) {
    "use strict";

    var id, filteredlinks, selected_hackers, matrix;

    // base data:
    var hackers = data.nodes.map(function (d) {
        d.selected = false;
        return d;
    });

    // sample matrix, the group centered on Zach
    matrix = [];
    id = 3; // Zach Allaun

    filteredlinks = data.links.filter(
            function (l) { return l.source === id || l.target === id; }
            );

    selected_hackers = _.union(
            _.map(filteredlinks, function (l) { return l.source; }),
            _.map(filteredlinks, function (l) { return l.target; })
            );

    for (var i=0; i< selected_hackers.length; i++) {
        hackers[selected_hackers[i]].selected = true;
    }

    var index = {};
    for (var i = 0; i < selected_hackers.length; i++) {
        matrix[i] = [];
        index[selected_hackers[i]] = i;
        for (var j = 0; j < selected_hackers.length; j++) {
            matrix[i].push(0);
        }
    }

    _.each(data.links,
            function (l) {
                if (_.contains(selected_hackers, l.source) && _.contains(selected_hackers, l.target)) {
                    matrix[index[l.source]][index[l.target]] = l.weight;
                    matrix[index[l.target]][index[l.source]] = l.weight;
                }
            }
          );

    var chord = d3.layout.chord()
        .padding(.05)
        .sortSubgroups(d3.descending)
        .matrix(matrix);

    var width = 1000,
        height = 500,
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
        .attr("id", function (d) { return "group" + d.index + "-" + j; })
        .on("mouseover", fade(.1))
        .on("mouseout", fade(1));

    svg.selectAll(".group")
        .append("svg:text")
        .attr("x", 6)
        .attr("dy", 15)
        .filter(function (d) {
            //console.log(d);
            return d.value > 60;
        })
    .append("svg:textPath")
        .attr("xlink:href", function (d) { return "#group" + d.index + "-" + j; })
        .text(function (d) {
            //return "hello"
            return data.nodes[selected_hackers[d.index]].login;
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

    // AVATARS

    d3.select("#mainSVG")
        .append("defs")
        .selectAll("pattern")
        //.data(chord.groups)
        .data(hackers)
        .enter()
        .append("pattern")
        //.attr("id", function (d) { return "avatar" + d.index; })
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
            //return data.nodes[selected_hackers[d.index]].avatar_url;
            return d.avatar_url;
        });


    function layout_avatars(groups) {

        groups.forEach(function (d) {
            d.login = hackers[selected_hackers[d.index]].login;
            d.selected = true;
        });

        var unselected = hackers.filter(function (d) { return !d.selected; });

        for (var i=0; i < unselected.length; i++) {
            unselected[i].col = i % 4;
            unselected[i].row = Math.floor(i / 4);
            unselected[i].selected = false;
        }

        function x_pos (d) {
            var center_x, angle, rotate, x_mod;
            if (d.selected) {
                center_x = width / 2;
                angle = (d.startAngle + d.endAngle) / 2;
                rotate = - Math.PI / 2;
                x_mod = 1.2 * outerRadius * Math.cos(rotate + angle);
            }
            else {
                x_mod = 20 + d.col * 40 - width / 2;
            }
            return x_mod;
        }

        function y_pos (d) {
            var center_y, angle, rotate, y_mod;
            if (d.selected) {
                center_y = height / 2;
                angle = (d.startAngle + d.endAngle) / 2;
                rotate = - Math.PI / 2;
                y_mod = 1.2 * outerRadius * Math.sin(rotate + angle);
            }
            else {
                y_mod = 20 + d.row * 40 - height / 2;
            }
            return y_mod;
        }

        svg.selectAll(".mugshots")
            //.data(groups)
            .data(groups.concat(unselected))
            .enter()
            .append("svg:circle")
            .attr("cx", x_pos)
            .attr("cy", y_pos)
            .attr("r", 15)
            .attr("stroke", "black")
            .attr("stroke-width", 2)
            .attr("fill", function (d) {
                //return "url(#avatar" + d.index + ")";
                //return "url(#avatar-" + hackers[d.mainIndex].login + ")";
                return "url(#avatar-" + d.login + ")";
            });

    }

    layout_avatars(chord.groups());

}
