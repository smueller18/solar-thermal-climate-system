SCHEMA_REGISTRY_URL = "/schema-registry";

var schemas = {};
var topics = {};


$.get(SCHEMA_REGISTRY_URL + "/subjects", function (subjects) {

    if(subjects.length === 0) {

        printError("No schemas available.");
        $(".loading").remove();
        return;
    }

    var finishedRequests = 0;

    subjects.forEach(function (subject) {

        $.get(SCHEMA_REGISTRY_URL + "/subjects/" + subject + "/versions/latest", function (schema) {

            var identifier = "";

            if (schema.subject.endsWith("-key") || schema.subject.endsWith("_key")) {
                topic_name = schema.subject.slice(0, -4);
		if (schema.subject.endsWith("_key")) 
		    topic_name = schema.subject.slice(0, -4);
		
                if (typeof(topics[topic_name]) === "undefined")
                    topics[topic_name] = {};

                topics[topic_name].key = schema.schema;
            }

            else if (schema.subject.endsWith("-value")) {
                topic_name = schema.subject.slice(0, -6);
		if (schema.subject.endsWith("_value")) 
		    topic_name = schema.subject.slice(0, -6);
		
                if (typeof(topics[topic_name]) === "undefined")
                    topics[topic_name] = {};

                topics[topic_name].value = schema.schema;
            }

        }).done(function(){
            finishedRequests++;
            if(finishedRequests === subjects.length){
                printSchemas();
            }
        }).fail(function(data) {
            printError(data.status + " " + data.statusText);
            $(".loading").remove();
        });
    })
})
.fail(function(data) {
    printError(data.status + " " + data.statusText);
    $(".loading").remove();
});

function printError(errorMessage) {
    $("#content").append(
      $("<div>").html(
        $('#template-error').html()
          .replace("ERROR_MESSAGE", errorMessage)
      )
    );
}

function printSchemas(){

    Object.keys(topics).sort().forEach(function (topic) {

        topicId = topic.replace(/\./g, "_");
		try {
			$("#schemas").append($("<div>").addClass("card").css("margin", "10px 0").html(
			  $('#template-schema').html()
				.replace(/TOPICID/g, topicId)
				.replace(/TOPIC/g, topic)
				.replace(/KEY_SCHEMA/g, library.json.prettyPrint($.parseJSON(topics[topic].key), null, 4))
				.replace(/VALUE_SCHEMA/g, library.json.prettyPrint($.parseJSON(topics[topic].value), null, 4))
			));
		} catch(e) {
			console.log(e);
		}
        
    });

    $(".loading").remove();
}
