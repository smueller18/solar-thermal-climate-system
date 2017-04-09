SCHEMA_REGISTRY_URL = "/schema-registry";

var schemas = {};
var topics = {};


$.get(SCHEMA_REGISTRY_URL + "/subjects", function (subjects) {

    var finishedRequests = 0;

    subjects.forEach(function (subject) {

        $.get(SCHEMA_REGISTRY_URL + "/subjects/" + subject + "/versions/latest", function (schema) {

            var identifier = "";

            if (schema.subject.endsWith("-key")) {
                topic_name = schema.subject.slice(0, -4);
                if (typeof(topics[topic_name]) === "undefined")
                    topics[topic_name] = {};

                topics[topic_name].key = schema.schema;
            }

            else if (schema.subject.endsWith("-value")) {
                topic_name = schema.subject.slice(0, -6);
                if (typeof(topics[topic_name]) === "undefined")
                    topics[topic_name] = {};

                topics[topic_name].value = schema.schema;
            }

        }).done(function(){
            finishedRequests++;
            if(finishedRequests === subjects.length){
                printHtml();
            }
        })
    })
});

function printHtml(){

    Object.keys(topics).sort().forEach(function (topic) {
        $("#content").append($("<h2>").text(topic));
        $("#content").append($("<h3>").text("Key"));
        $("#content").append($("<pre>").html(library.json.prettyPrint($.parseJSON(topics[topic].key), null, 4)));
        $("#content").append($("<h3>").text("Value"));
        $("#content").append($("<pre>").html(library.json.prettyPrint($.parseJSON(topics[topic].value), null, 4)));
    });
}
