const NAMESPACE_SVG = "http://www.w3.org/2000/svg";
const SENSOR_DESCRIPTION_URL = "sensor_description.json";
// to be defined in config/config.js
//const SOCKET_URL = "http://localhost:5002/";


// required by function updateSensorValues()
var sensorValueTextNodes = {};

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

        document.getElementById('connection-status').className =
            document.getElementById('connection-status').className.replace("btn-danger", "btn-success");

        socket.on('sensor_values_cache', function (message) {

            if (typeof(message) === "undefined")
                return;

            if ('error' in message) {
                console.log(message.error);
                return;
            }

            if ('timestamp' in message && 'data' in message) {
                update(message['timestamp'], message['data']);
            }
        });

        socket.on('sensor_values', function (message) {
            if (typeof(message) === "undefined")
                return;

            if ('error' in message) {
                console.log(message.error);
                return;
            }

            if ('timestamp' in message && 'data' in message) {
                update(message['timestamp'], message['data']);
            }
        });

        socket.on('connected_clients', function (message) {
            if (typeof(message) === "number")
                document.getElementById("connected-clients").value = message;
        });
    });

    socket.on('disconnect', function () {
        document.getElementById('connection-status').className =
            document.getElementById('connection-status').className.replace("btn-success", "btn-danger");
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
        var sensorIdNode = document.getElementById("plant-visualization").contentDocument.evaluate(
            '//x:text[text() = "' + sensorId + '"]',
            document.getElementById("plant-visualization").contentDocument,
            myNamespaceResolver,
            XPathResult.FIRST_ORDERED_NODE_TYPE,
            null
        ).singleNodeValue;

        if (sensorIdNode != null) {

            bbox = sensorIdNode.getBBox();

            var sensorValueNode = document.createElementNS(NAMESPACE_SVG, "text");
            var x = sensorIdNode.getAttribute("x");
            var y = parseFloat(sensorIdNode.getAttribute("y")) + bbox.height + 2;
            sensorValueNode.setAttribute("x", x);
            sensorValueNode.setAttribute("y", y.toString());
            sensorValueNode.setAttribute("text-anchor", "left");
            sensorValueNode.setAttribute("fill", "red");
            sensorValueNode.setAttribute("fonts-family", "Arial");
            sensorValueNode.textContent = "";

            var sensorValue = document.createElementNS(NAMESPACE_SVG, "tspan");
            sensorValue.setAttribute("id", sensorId);
            sensorValue.appendChild(document.createTextNode(NaN));

            var sensorUnitNode = document.createElementNS(NAMESPACE_SVG, "tspan");
            sensorUnitNode.appendChild(document.createTextNode(" " + sensorUnit));

            sensorValueNode.appendChild(sensorValue);
            sensorValueNode.appendChild(sensorUnitNode);

            sensorIdNode.parentNode.appendChild(sensorValueNode);

            sensorValueTextNodes[sensorId] = sensorValue;
        }
    });

    return sensorValueTextNodes;
}

function update(timestamp, sensorValues) {

    if (typeof(sensorValues) !== "object" || typeof(timestamp) !== "number")
        return;

    var datetime = new Date(timestamp * 1000);
    var offset = new Date() - datetime;
    document.getElementById("last-update-time").value = datetime.toString("dd.MM.yyyy HH:mm:ss");
    document.getElementById("offset").value = offset;

    Object.keys(sensorValues).forEach(function (sensorId) {
        if (sensorValueTextNodes[sensorId] != undefined) {
            var sensorValue = sensorValues[sensorId];
            var newSensorValue;
            switch (typeof(sensorValue)) {
                case "number":
                    // integer
                    if (sensorValue % 1 === 0)
                        newSensorValue = sensorValue.toString();
                    // float
                    else
                        newSensorValue = sensorValue.toFixed(1).toString();
                    break;
                case "boolean":
                    if (sensorValue)
                        newSensorValue = "True";
                    else
                        newSensorValue = "False";
                    break;
                default:
                    newSensorValue = sensorValue.toString();
                    break;
            }
            sensorValueTextNodes[sensorId].textContent = newSensorValue;
        }
    });
}