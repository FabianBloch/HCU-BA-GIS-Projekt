const map = L.map('map').setView([53.5403, 10.005], 13);

L.control.scale({imperial: false, metric: true}).addTo(map);

// Basemaps

const OSM = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

const Webatlas = L.tileLayer.wms('https://sg.geodatenzentrum.de/wms_webatlasde.light?', {
    layers: "webatlasde.light",
    attribution: "&copy; GeoBasis-DE / <a href='http://www.bkg.bund.de'>BKG</a>"
});

const Ortho = L.tileLayer.wms('https://geodienste.hamburg.de/HH_WMS_DOP?', {
    layers: "HH_WMS_DOP_2021",
    attribution: "&copy; <a href='https://geoportal-hamburg.de/'>LGV</a>"
});

const GeoBasisHH = L.tileLayer.wms('https://geodienste.hamburg.de/HH_WMS_Geobasiskarten?', {
    layers: "WMS_Geobasiskarten_Hamburg_N",
    attribution: "&copy; <a href='https://geoportal-hamburg.de/'>LGV</a>"
});

const baseMaps = {
    "OpenSteet Map": OSM,
    "Webatlas DE": Webatlas,
    "GeoBasisKarten HH": GeoBasisHH,
    "Orthophotos HH": Ortho
}

// OverlayMaps

const overlayMaps = {};

// OpenSeaMap
const OpenSeaMap = L.tileLayer('https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
});

// HVV-Linien
const hvv_colors = {
    "U1": "#0381F0",
    "U2": "#FF010E",
    "U3": "#FFE300",
    "S1": "#01CD2E",
    "S21": "#E90D4B",
    "S3": "#721F86",
    "A1": "#E8921D"
};

const load_hvvlinien = async (url) => {
    const response = await fetch(url);
    const geojson_obj = await response.json();
    const linien = L.geoJson(geojson_obj, {
        style: (feature) => {
            return {
                color: hvv_colors[feature.properties.ART+feature.properties.NR],
                weight: 3.5
            };
        },
        onEachFeature: (feature, layer) => {
            layer.bindPopup(feature.properties.ART+feature.properties.NR)
        }
    });
    return linien;
}

async function load_hvvstationen(url) {
    const response = await fetch(url);
    const geojson_obj = await response.json();
    const stationen = L.geoJson(geojson_obj, {
        pointToLayer: (feature, latlng) => {
            return L.marker(latlng, {
                icon: L.icon({
                    iconUrl: 'images/' + feature.properties.ART + '.svg',
                    iconSize: [15, 15], // 20, 20
                    iconAnchor: [7.5, 7.5], // 10, 10
                    popupAnchor: [0, -10] // 0, -10
                })
            })
        },
        onEachFeature: (feature, layer) => {
            layer.bindPopup(`<b>${feature.properties.HALTESTELLE}</b><br>
            ${feature.properties.ART}${feature.properties.NR}`);
        }
    })
    return stationen;
}

// IIFE (Immediately Invoked Function Express)
// = selbst ausführende Funktion
(async () => {
    const overlayMaps = {
        'OpenSeaMap': OpenSeaMap,
        'HVV-Linien': await load_hvvlinien('data/hvvlinien.geojson'),
        'HVV-Stationen': await load_hvvstationen('data/hvvstationen.geojson')
    };
    L.control.layers(baseMaps, overlayMaps).addTo(map);
})();


// Icons
const uniIcon = L.icon({
    iconUrl: 'images/uni.svg',
    iconSize: [25, 25],
    iconAnchor: [12, 12],
    popupAnchor: [0, -10]
});

L.marker([53.5403, 10.005], {icon: uniIcon}).addTo(map)
    .bindPopup('<a href="https://www.hcu-hamburg.de/" target="_blank">HafenCity Universität Hamburg</a>');
    //.openPopup();

