
var UPDATE_INTERVAL = 1;
const NAMESPACE_SVG = "http://www.w3.org/2000/svg";
const SENSOR_DESCRIPTION_URL = "sensor_description.json";
// to be defined in config/config.js
// const SENSOR_VALUES_URL = "..."

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
    var sensorValueNodes = {};

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
            sensorValueNode.setAttribute("font-family", "Arial");
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

function updateSensorValues() {
    getJSON(SENSOR_VALUES_URL, function (err, data) {
        if (err != null) {
            console.log("Something went wrong: " + err);
        } else {
            var sensorValues = data["data"];
            var timestamp = data["timestamp"];

            Object.keys(sensorValues).forEach(function (sensorId) {
				if (sensorValueTextNodes[sensorId] != undefined) {
					var sensorValue = sensorValues[sensorId];
          var newSensorValue;
					switch (typeof(sensorValue)) {
						case "number":
							// integer
							if(sensorValue % 1 === 0)
								newSensorValue = sensorValue.toString();
							// float
							else
								newSensorValue = sensorValue.toFixed(1).toString();
							break;
						case "boolean":
							if(sensorValue)
								newSensorValue = "True";
							else
								newSensorValue = "False";
                            break;
						default:
							newSensorValue = sensorValue.toString();
							break;
					}
                    var oldSensorValue = sensorValueTextNodes[sensorId].textContent;
                    sensorValueTextNodes[sensorId].textContent = newSensorValue;
				}
            });
            var datetime = new Date(timestamp * 1000);
            document.getElementById("last-update-time").textContent = datetime.toString("dd.MM.yyyy HH:mm:ss");
        }
        setTimeout(updateSensorValues, UPDATE_INTERVAL * 1000)
    });
}


// required by function updateSensorValues()
var sensorValueTextNodes = {};

window.onload = function () {

    getJSON(SENSOR_DESCRIPTION_URL,
        function (err, data) {
            if (err != null) {
                console.log("Something went wrong: " + err);
            } else {
                sensorValueTextNodes = initializeSensorValueNodes(data);
                updateSensorValues();
            }
        });
};
