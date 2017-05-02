const NAMESPACE_SVG = "http://www.w3.org/2000/svg";
const SENSOR_DESCRIPTION_URL = "../../config/sensor_description.json";
// to be defined in config/config.js
//const SOCKET_URL = "http://localhost:5002/";


// required by function updateSensorValues()
var sensorValueTextNodes = {};

var svgElementId = "monitor-atrium";
var topicFilter = "prod.stcs.atrium.temperatures";

window.onload = function () {

    getJSON(SENSOR_DESCRIPTION_URL,
        function (err, data) {
            if (err != null) {
                console.log("Something went wrong: " + err);
            } else {
                sensorValueTextNodes = initializeSensorValueNodes(data);
            }
        });

    var socket = io(SOCKET_URL);
    socket.on('connect', function () {

        socket.on('sensor_values', function (message) {
            if (typeof(message) === "undefined")
                return;

            if ('error' in message) {
                console.log(message.error);
                return;
            }

            if (message["topic"] != topicFilter)
                return;

            if ('timestamp' in message && 'data' in message) {
                update(message['timestamp'], message['data']);
            }
        });

    });

};


var getJSON = function (url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open("get", url, true);
    xhr.responseType = "json";
    xhr.onload = function () {
        var status = xhr.status;
        if (status == 200) {
            callback(null, xhr.response);
        } else {
            callback(status);
        }
    };
    xhr.send();
};

var myNamespaceResolver = {
    lookupNamespaceURI: function (prefix) {
        switch (prefix) {
            // resolve "x" prefix
            case 'x':
                return NAMESPACE_SVG;
            default:
                return null;
        }
    }
};

function initializeSensorValueNodes(sensorValues) {

    if (typeof(sensorValues) !== "object")
        return;

    Object.keys(sensorValues).forEach(function (sensorId) {
        var sensorUnit = sensorValues[sensorId].unit;

        // due to unique id, only first iteration should exist
        var sensorIdNode = document.getElementById(svgElementId).contentDocument.evaluate(
            '//x:text[text() = "' + sensorId + '"]',
            document.getElementById(svgElementId).contentDocument,
            myNamespaceResolver,
            XPathResult.FIRST_ORDERED_NODE_TYPE,
            null
        ).singleNodeValue;

        if (sensorIdNode != null) {

            var sensorValueNode = document.createElementNS(NAMESPACE_SVG, "text");

            // <text class="y" transform="translate(163.55 22.33)">TSE_6</text>
            translate = sensorIdNode.transform.baseVal.getItem(0);
            if (translate.type != SVGTransform.SVG_TRANSFORM_TRANSLATE)
                return;

            var x = translate.matrix.e - 5;
            var y = translate.matrix.f;
            sensorValueNode.setAttribute("x", x.toString());
            sensorValueNode.setAttribute("y", y.toString());
            sensorValueNode.setAttribute("fill", "red");
      			sensorValueNode.setAttribute("text-anchor", "end");
      			sensorValueNode.setAttribute("font-size", "10px");
            sensorValueNode.setAttribute("fonts-family", "Arial");
            sensorValueNode.textContent = "";

            var sensorValue = document.createElementNS(NAMESPACE_SVG, "tspan");
            sensorValue.setAttribute("id", sensorId);
            sensorValue.appendChild(document.createTextNode(NaN));

            var sensorUnitNode = document.createElementNS(NAMESPACE_SVG, "tspan");
            sensorUnitNode.appendChild(document.createTextNode(" " + sensorUnit));

            sensorValueNode.appendChild(sensorValue);
            sensorValueNode.appendChild(sensorUnitNode);

            document.getElementById(svgElementId).contentDocument.childNodes[0].appendChild(sensorValueNode);

            sensorValueTextNodes[sensorId] = sensorValue;
        }
    });

    return sensorValueTextNodes;
}

var latest_timestamp = 0;
function update(timestamp, sensorValues) {

    if (typeof(sensorValues) !== "object" || typeof(timestamp) !== "number")
        return;

    var datetime = new Date(timestamp * 1000);

    if(latest_timestamp < datetime) {
        latest_timestamp = datetime;
        document.getElementById("last-update-time").textContent = datetime.toString("dd.MM.yyyy HH:mm:ss");
    }

    Object.keys(sensorValues).forEach(function (sensorId) {
        if (sensorValueTextNodes[sensorId] != undefined) {
            sensorValueTextNodes[sensorId].textContent = sensorValues[sensorId].toFixed(1).toString();
        }
    });
}
