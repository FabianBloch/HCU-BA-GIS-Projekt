const map = L.map('map').setView([53.5403, 10.005], 15);

L.control.scale({imperial: false, matric: true}).addTo(map);

// Basemaps

const OSM = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

const DOP = L.tileLayer.wms('http://geodienste.hamburg.de/HH_WMS_DOP', {
	layers: "DOP",
    attribution: '&copy; <a href="https://geodienste.hamburg.de/HH_WMS_DOP">Test</a> contributors'
})

const Webatlas = L.tileLayer.wms('https://sg.geodatenzentrum.de/wms_webatlasde.light?', {
    layers: "webatlasde.light",
    attribution: "&copy; GeoBasis-De / <a href = 'http://www.bkg.bund.de'>BGK</a>"
});

const baseMaps = {
    "OpenStreetMap": OSM,
	"DOP": DOP,
    "Webatlas DE": Webatlas
};

// Overlaymaps

const overlayMaps = {};

// OpenSeaMap

const openSeaMap = L.tileLayer('https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png', {
    attribution: '???'
});

// HHV-Linien
const hvv_colors = {
    "U1": "#0381F0",
    "U2": "#FF010E",
    "U3": "#FFE300",
    "S1": "#01CD2E",
    "S21": "#E90D4B",
    "S3": "#721F86",
    "A1": "#E8921D"
};

const load_hvv_linien = async (url) => {
    const response = await fetch(url);
    const geojson_obj = await response.json();
    const linien = L.geoJson(geojson_obj, {
        style: (feature) => {
            return {
                color: hvv_colors[feature.properties.ART+feature.properties.NR],
                weight: 5
            };
        },
        onEachFeature: (feature, layer) => {
            layer.bindPopup(feature.properties.ART+feature.properties.NR);
        }
    });
    return linien;
};

async function load_hvvstation(url) {
    const response = await fetch(url);
    const geojson_obj = await response.json();
    const stationen = L.geoJson(geojson_obj, {
        pointToLayer: (feature, latlng) => { 
            return L.marker(latlng, {
                icon: L.icon({
                    iconUrl:'images/'+ feature.properties.ART + '.svg',
                    iconSize: [20,20],
                    iconAnchor: [10,10],
                    popupAnchor:[0, -10]
                })
            })
        },
        onEachFeature: (feature, layer) =>{
            layer.bindPopup(`<b>${feature.properties.HALTESTELLE}<b><br>${feature.properties.ART}${feature.properties.NR}`);

        }
    })
    return stationen;
}

// IIFE (Immediately Invoked function Expression)
// = Selbst ausführende Funktion
(async () => {
    const overlayMaps = {
        'OpenSeaMap': openSeaMap,
        'Hvv-Linien': await load_hvv_linien('data/hvvlinien.geojson'),
        'HVV-Stationen': await load_hvvstation('data/hvvstationen.geojson')
    };
    L.control.layers(baseMaps, overlayMaps).addTo(map);
})();

// Icons

const uniIcon = L.icon({
    iconUrl: 'images/uni.svg',
    iconSize: [50, 50],
    iconAnchor: [25,40],
    popupAnchor: [-3, -76]
})
L.marker([53.5403, 10.005], {icon: uniIcon}).addTo(map)
    .bindPopup('Hier ist die <br> HafenCity Universität <br> Hamburg');
    //.openPopup();