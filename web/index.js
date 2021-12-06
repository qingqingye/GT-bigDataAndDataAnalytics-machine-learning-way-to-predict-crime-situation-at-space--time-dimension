
let map, leftUp, rightBottom, gridSize, hour, time, currentTime, infoWindow;
let heatmapData, heatmapDataByTime, heatmapByHour, heatmapDataByRegion, dataByRegion, heatmap;

const zoomScale = {
    20 : 1128.497220,
    19 : 2256.994440,
    18 : 4513.988880,
    17 : 9027.977761,
    16 : 18055.955520,
    15 : 36111.911040,
    14 : 72223.822090,
    13 : 144447.644200,
    12 : 288895.288400,
    11 : 577790.576700,
    10 : 1155581.153000,
    9  : 2311162.307000,
    8  : 4622324.614000,
    7  : 9244649.227000,
    6  : 18489298.450000,
    5  : 36978596.910000,
    4  : 73957193.820000,
    3  : 147914387.600000,
    2  : 295828775.300000,
    1  : 591657550.500000
}

function initMap() {
    var dataTime = d3.range(0, 23).map(function(d) { // 155 months
        return new Date(2021 + d/12, d%12, 1);
    });

    var time = new Date(2009, 0, 1);
    var barTime = new Date(2021, 0, 1);
    var hour = "";
    // var currentTime = new Date(2009, 11, 1);
    // console.log(time);
    // console.log(time.getYear());

    // slider bottom
    var sliderTime = d3
        .sliderBottom()
        .min(new Date(2021, 0, 1))
        .max(new Date(2022, 11, 1))
        .step(1000 * 60 * 60 * 24)
        .width(800)
        .ticks(12)
        .tickFormat(d3.timeFormat('%Y-%m-%d'))
        .tickValues(dataTime)
        .default(barTime)
        .on('onchange', show);

    function show(){
        // d3.selectAll(".legend").remove();
        infoWindow.close();
        
        time = sliderTime.value();
        time.setFullYear(time.getFullYear()-12);
        if (time.toISOString().slice(0, 10) in heatmapData) {
            heatmapData[time.toISOString().slice(0, 10)].forEach(function(d){
                if (Array.isArray(d.location)) {
                    d.location = new google.maps.LatLng(d.location[0], d.location[1]);
                    d.weight *= 100;
                    d.maxIntensity = 10000;
                }
            });
            heatmap.setData(heatmapData[time.toISOString().slice(0, 10)]);
            heatmap.setOptions({radius: 3.5 * 2 ** (3-map.getZoom()) });
            // heatmap.setOptions({radius: 1.5 * 2 ** (map.getZoom()-22) });
            // console.log(time.toISOString().slice(0, 10));
            // console.log(heatmapData[time.toISOString().slice(0, 10)].length);
        } else {
            heatmap.setData([]);
            // console.log("no data");
        }
    }

    var gTime = d3
        .select('div#slider-year')
        .append('svg')
        .attr('width', 1000)
        .attr('height', 80)
        .append('g')
        .attr('transform', 'translate(40,20)');
    gTime.call(sliderTime);

    var tip = d3.tip()
        .attr("id", "tooltip")
		.attr("class", "d3-tip")
		.offset([0, 0])

    var hourSelect = ["Select the hour period:"];
    for (let hr = 0; hr < 24; hr++) {
        let hr1 = hr.toString().padStart(2, "0") + ":";
        let hr2 = (hr+1).toString().padStart(2, "0") + ":";
        hourSelect.push(hr1 + "00 - " + hr1 + "30");
        hourSelect.push(hr1 + "30 - " + hr2 + "00");
    }

    d3.select("#hourSelect")
        .selectAll('option')
        .data(hourSelect)
        .enter()
        .append("option")
        .attr("value", function (d) { return d; }) // corresponding value returned by the button
        .text(function (d) { return d; }) // text showed in the menu

    d3.select("#hourSelect").on("change", function(d){
        infoWindow.close();

        hour = this.value;
        if (hour.length == 13) {
            console.log(heatmapDataByTime[time.toISOString().slice(0, 10)].length);
            var minute1 = parseInt(hour.slice(3,5));
            var minute2 = parseInt(hour.slice(11,13));
            if (minute2 == 0) minute2 = 59;
            heatmapByHour = [];
            for (i=0; i<heatmapDataByTime[time.toISOString().slice(0, 10)].length; i++) {
                if (heatmapDataByTime[time.toISOString().slice(0, 10)][i].getHours() == parseInt(hour.slice(0,2))) {
                    var minute = heatmapDataByTime[time.toISOString().slice(0, 10)][i].getMinutes();
                    if (minute >= minute1 && minute <= minute2) {
                        heatmapByHour.push(heatmapData[time.toISOString().slice(0, 10)][i]);
                    }
                }
            }
            // heatmap.setData(heatmapByHour);
            // heatmap.setOptions({radius: 10});

            console.log(heatmapByHour.length);
        }
    })

    const gatech = { lat: 33.7756, lng: -84.3963 };
    const leftUp = { lat: 33.885846, lng: -84.550489 };
    const rightBottom = { lat: 33.6009, lng: -84.284975 };
    const gridSize = [0.0031696245663468403, 0.0030172045454545005]; // lat and long

    infoWindow = new google.maps.InfoWindow({});

    var heatmapData = {};
    var heatmapDataByTime = {};
    var heatmapByHour = [];
    var heatmapDataByRegion = {};
    var dataByRegion = {};

    // Initialize and add the map
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 13,
        center: gatech,
        mapTypeId: "terrain",
    });
    const marker = new google.maps.Marker({
        position: gatech,
        map: map,
    });

    map.data.loadGeoJson(
        "./json/City_of_Atlanta_Neighborhood_Statistical_Areas.json"
    );

    map.addListener("zoom_changed", () => {
        heatmap.setOptions({radius: 1.5 * 2 ** (3-map.getZoom()) });
    });

    // define(function (require) {
    //     PolygonLookup = require('polygon-lookup');
    // });
    // const PolygonLookup = require('polygon-lookup');

    map.data.setStyle(function(feature) {
        // var lookup = new PolygonLookup(feature);
        // var poly = lookup.search(33.7756, -84.3963);
        // console.log(poly);
        // console.log(d3.geoContains(feature, { lat: 33.7756, lng: -84.3963 }));
        // var ascii = feature.getProperty('ascii');
        // var color = ascii > 91 ? 'red' : 'blue';
        return {
            fillColor: 'none',
            strokeColor: 'grey',
            strokeWeight: 1
        };
    });

    map.data.addListener('mouseover', function(event) {
        map.data.revertStyle();
        map.data.overrideStyle(event.feature, {strokeWeight: 3});
    });

    map.data.addListener('mouseout', function(event) {
        map.data.revertStyle();
    });

    map.addListener("click", (mapsMouseEvent) => {
        var mouseLatLng = mapsMouseEvent.latLng;
        
        var index = Math.floor(Math.abs(leftUp.lat - mouseLatLng.toJSON().lat)/gridSize[0]) * 88 + Math.floor(Math.abs(leftUp.lng - mouseLatLng.toJSON().lng)/gridSize[1]);
        infoWindow.close();
        contentString = show_string(time, hour, mouseLatLng, null, index, dataByRegion, heatmapDataByRegion, heatmapByHour);
        infoWindow = new google.maps.InfoWindow({
            content: contentString,
            position: mouseLatLng,
        });
        infoWindow.open(map);
    });

    map.data.addListener("click", (mapsMouseEvent) => {
        // map.setZoom(8);
        // map.setCenter(marker.getPosition());
        // console.log(mapsMouseEvent.latLng.toString());
        var mouseLatLng = mapsMouseEvent.latLng;

        // const resultColor = google.maps.geometry.poly.containsLocation(
        //     mapsMouseEvent.latLng,
        //     bermudaTriangle
        // ) ? "blue" : "red";        
        var index = Math.floor(Math.abs(leftUp.lat - mouseLatLng.toJSON().lat)/gridSize[0]) * 88 + Math.floor(Math.abs(leftUp.lng - mouseLatLng.toJSON().lng)/gridSize[1]);
        contentString = show_string(time, hour, mouseLatLng, mapsMouseEvent.feature.h, index, dataByRegion, heatmapDataByRegion, heatmapByHour);

        infoWindow.close();
        infoWindow = new google.maps.InfoWindow({
            content: contentString,
            position: mouseLatLng,
        });
        infoWindow.open(map);
        
    });

    //// Read and parse by Papa
    // const fs = require('fs');
    // console.log(document.getElementById("file-input"));
    // const file = fs.createReadStream('refined_data.csv');
    // Papa.parse("https://raw.githubusercontent.com/KratosST/kratosst.github.io/main/refined_data.csv", {
    //     download: true,
    //     complete: function(results) {
    //         array = results.data; 
    //         array.forEach(function(d, i){
    //             if (i > 0) {
    //                 var date = (new Date(d[0] * 1000)).toISOString().slice(0, 10);
    //                 const latLng = new google.maps.LatLng(d[1], d[2]);

    //                 // TODO: draw color by region
    //                 if ((date in heatmapData) == false) {
    //                     heatmapData[date] = [{location: latLng, weight: 0.1}];
    //                     heatmapDataByTime[date] = [new Date(d[0] * 1000)];
    //                 } else {
    //                     heatmapData[date].push({location: latLng, weight: 0.1});
    //                     heatmapDataByTime[date].push(new Date(d[0] * 1000));
    //                 }
    //             }
    //         });

    //         heatmap = new google.maps.visualization.HeatmapLayer({
    //             data: heatmapData[time.toISOString().slice(0, 10)],
    //             dissipating: false,
    //             map: map,
    //             radius: 2 * 10 ** (map.getZoom()-15),
    //         });
    //     }
    // })

    d3.json("./refined.json").then(function(data) {
        dataByRegion = data["dataByRegion"];
    });
    d3.json("./sample.json").then(function(data) {
        heatmapData = data["heatmapData"];
        heatmapDataByTime = data["heatmapDataByTime"];
        heatmapDataByRegion = data["heatmapDataByRegion"];

        heatmapData[time.toISOString().slice(0, 10)].forEach(function(d){
            d.location = new google.maps.LatLng(d.location[0], d.location[1]);
            d.weight *= 100;
            d.maxIntensity = 10000;
        });
        heatmap = new google.maps.visualization.HeatmapLayer({
            data: heatmapData[time.toISOString().slice(0, 10)],
            dissipating: false,
            map: map,
            // radius: 3 * 10 ** (map.getZoom()-16),
            radius: 3.5 * 2 ** (3-map.getZoom()),
        }) 
    });

    // get_heatmap(time, leftUp, gridSize, heatmapData, heatmapDataByTime, dataByRegion);
    // get_stkde_map(time, leftUp, gridSize, heatmapData, heatmapDataByTime, heatmapDataByRegion);

    // Create a <script> tag and set the USGS URL as the source.
    // const script = document.createElement("script");
    // script.src =
    //     "https://developers.google.com/maps/documentation/javascript/examples/json/earthquake_GeoJSONP.js";
    // document.getElementsByTagName("head")[0].appendChild(script);

}

function get_heatmap(time, leftUp, gridSize, heatmapData, heatmapDataByTime, dataByRegion) {
    Promise.all([
        d3.csv("./refined_data.csv")
    ]).then (function(array) {
        results = array[0];
        results.forEach(function(d){
            var date = (new Date(d["timestamp"] * 1000)).toISOString().slice(0, 10);
            // const latLng = new google.maps.LatLng(d["lat"], d["long"]);

            var index = Math.floor(Math.abs(leftUp.lat - d["lat"])/gridSize[0]) * 88 + Math.floor(Math.abs(leftUp.lng - d["long"])/gridSize[1]); 

            // TODO: draw color by region
            // if ((date in heatmapData) == false) {
            //     heatmapData[date] = [{location: latLng, weight: 0.1}];
            //     heatmapDataByTime[date] = [new Date(d["timestamp"] * 1000)];
            // } else {
            //     heatmapData[date].push({location: latLng, weight: 0.1});
            //     heatmapDataByTime[date].push(new Date(d["timestamp"] * 1000));
            // }

            if (index in dataByRegion) {
                dataByRegion[index].push(date);
            } else {
                dataByRegion[index] = [date];
            }

        });

        console.log(dataByRegion);

        // heatmap = new google.maps.visualization.HeatmapLayer({
        //     data: heatmapData[time.toISOString().slice(0, 10)],
        //     dissipating: false,
        //     map: map,
        //     radius: 2 * 10 ** (map.getZoom()-15),
        // });
    });
}

function get_stkde_map(time, leftUp, gridSize, heatmapData, heatmapDataByTime, heatmapDataByRegion) {
    //// Read and parse by d3
    Promise.all([
        d3.csv("./filtered_data(1).csv")
    ]).then (function(array) {
        results = array[0];
        results.forEach(function(d){
            var ts = d["from_time"]/2+d["to_time"]/2;
            var date = (new Date(ts * 1000)).toISOString().slice(0, 10);
            const latLng = new google.maps.LatLng(d["from_lat"]/2+d["to_lat"]/2, d["from_lon"]/2+d["to_lon"]/2);

            var index = Math.floor(Math.abs(leftUp.lat - latLng.toJSON().lat)/gridSize[0]) * 88 + Math.floor(Math.abs(leftUp.lng - latLng.toJSON().lng)/gridSize[1]);

            // console.log(latLng);

            // TODO: draw color by region
            if ((date in heatmapData) == false) {
                heatmapData[date] = [{location: latLng, weight: d["possibility"]*1}];
                heatmapDataByTime[date] = [new Date(ts * 1000)];
            } else {
                heatmapData[date].push({location: latLng, weight: d["possibility"]*1});
                heatmapDataByTime[date].push(new Date(ts * 1000));
            }

            if (index in heatmapDataByRegion) {
                if (date in heatmapDataByRegion[index]) heatmapDataByRegion[index][date].push(d["possibility"]);
                else heatmapDataByRegion[index][date] = [d["possibility"]];
            } else {
                heatmapDataByRegion[index] = {};
                heatmapDataByRegion[index][date] = [d["possibility"]];
            }

        });

        heatmap = new google.maps.visualization.HeatmapLayer({
            data: heatmapData[time.toISOString().slice(0, 10)],
            dissipating: false,
            map: map,
            radius: 2 * 10 ** (map.getZoom()-15),
        });

        console.log(heatmapDataByRegion);

    });
}

function show_string(time, hour, mouseLatLng, feature = null, index, dataByRegion, heatmapDataByRegion, heatmapByHour) {
    var currentTime = new Date(2009, 11, 1);
    var date = time.toISOString().slice(0, 10);
    showDate = parseInt(date.slice(0,4))+12 + date.slice(4, date.length);
    var latLng = mouseLatLng.toJSON();
    var history = 0, current = 0, location = "outside Atlanta", neighborhood = "N/A", prediction = 0.0, risk = "Safe", hourRange = "whole day";
    const risk_level = {0.0 : ["safe", "#008450"], 0.5 : ["medium", "#EFB700"], 
        1.0 : ["cafeful", "#EFB700"], 2.0: ["stay inside", "#B81D13"], 5.0: ["dangerous", "#B81D13"]};
    
    if (feature != null) {
        location = feature.NPU + ", " + feature.STATISTICA;
        neighborhood = feature.NEIGHBORHO;
    } else {
        index = "N/A";
    }
    if (index in dataByRegion) {
        history = dataByRegion[index].length;
        current = dataByRegion[index].filter(x => x==date).length;
    }
    if (hour.length == 13) {
        hourRange = hour;
        // console.log(heatmapByHour);
        if (current > 0) current = heatmapByHour.length;
    }
    if (index in heatmapDataByRegion && date in heatmapDataByRegion[index]) {
        prediction = heatmapDataByRegion[index][date].reduce((a, b) => parseFloat(a) + parseFloat(b)) / heatmapDataByRegion[index][date].length;
        prediction = (prediction * 100).toFixed(2);
    }
    for (l in risk_level) {
        if (prediction >= l) risk = risk_level[l];
    }
    var contentString =
        '<div id="bodyContent">' +
        '<p>Location: ' + latLng.lat + ', ' + latLng.lng + '</b></p>' +
        '<p>Region: ' + location + '</p>' +
        '<p><b>Neighborhood: ' + neighborhood + '</b></p>' +
        "<p><b>Date: " + showDate + "</b></p>" +
        "<p><b>Hour Range: " + hourRange + "</b></p>" +
        "<p><b>Grid Index: </b>" + index + "</p>" + 
        "<p><b>History Records: </b>" + history + "</p>";
    if (time < currentTime) {
        contentString += ("<p><b>Records at " + showDate + ": </b>" + current + "</p>");
        contentString += ("<p><b>Density Analysis at " + showDate + ": </b>" + prediction + "%</p>");
    } else {
        contentString += "<p><b>Predicted Probability at " + showDate + ": </b>" + prediction + "%</p>";
    }
    contentString += "<p><b>Risk Level at " + showDate + ": </b>" + "<b><span style=color:" + risk[1] + ">" + risk[0] + "</span></b>" + "</p>";
    contentString += "</div>";

    return contentString;
}
