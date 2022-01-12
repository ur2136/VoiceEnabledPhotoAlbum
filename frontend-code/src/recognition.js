// using built-in speech recognition
var recognition = new webkitSpeechRecognition(); //That is the object that will manage our whole recognition process. 
recognition.continuous = true;   // Suitable for dictation. 
recognition.interimResults = true;  //If we want to start receiving results even if they are not final.
// Define some more additional parameters for the recognition:
recognition.lang = "en-US"; 
recognition.maxAlternatives = 1; //Since from our experience, the highest result is really the best...


recognition.onresult = function(event) {
    if (event.results.length > 0) {
        console.log(event.results[0][0].transcript);
        var voiceQuery = event.results[0][0].transcript;
        document.getElementById("field_search").value = voiceQuery;

        // searchVoice(voiceQuery);
        // this now holds the necessary text for the query 
    //   console.log(q.value);
    //   q.form.submit();
    }
};


// recognition.onresult = function(event) { //the event holds the results
// //Yay – we have results! Let’s check if they are defined and if final or not:
//     if (typeof(event.results) === 'undefined') { //Something is wrong…
//         recognition.stop();
//         return;
//     }

//     for (var i = event.resultIndex; i < event.results.length; ++i) {      
//         if (event.results[i].isFinal) { //Final results
//             console.log("final results: " + event.results[i][0].transcript);   //Of course – here is the place to do useful things with the results.
//         } else {   //i.e. interim...
//             console.log("interim results: " + event.results[i][0].transcript);  //You can use these results to give the user near real time experience.
//         } 
//     } //end for loop
// }; 

function searchVoice(voiceQuery)
{
    var apigClient = apigClientFactory.newClient({
        apiKey: "h5pv2bM96C443KTAdFJoaGURiM2SYbi6IASgpqgf"
    });
    var body = {};
    var params = {q: voiceQuery};
    document.getElementById("field_search").value = voiceQuery;

    var addParams = {
        headers: {
            'Content-Type':"application/json"
        }
    };
    apigClient.searchGet(params, body, addParams).then(function(res) {
        if (res.data.length == 0)
        {
            document.getElementById("display-text").innerHTML="NoImagesFound!";
        }
        // console.log(res);
        res.data.results.forEach(function(obj){
            // obj = {"labels": [...], "url": "..."}
            var img = new Image();
            console.log('obj');
            console.log(obj);
            img.src = obj["url"];
            // img.src = "http://s3.amazonaws.com/ur2136-jk4534-b2/"+obj;
            img.setAttribute("class", "album-img");
            document.getElementById("display-text").innerHTML="ImagesFound!";
            document.getElementById("album").appendChild(img);
        });
     }).catch(function(result){
        console.log("result here");
        console.log(result);
     });
}
