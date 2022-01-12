function getBase64(file) {
    return new Promise((resolve, reject) => {
        const fileReader = new FileReader();
        fileReader.readAsDataURL(file);
        fileReader.onload = () => {
            let encodedImage = fileReader.result.toString().replace(/^data:(.*;base64,)?/, '');
            if ((encodedImage.length%4)>0) {
              encodedImage += '='.repeat(4 - (encodedImage.length % 4));
            }
            resolve(encodedImage);
        };
        fileReader.onerror = error => reject(error);
    })
}

function uploadPhoto()
{
    var file = document.getElementById("field_upload").files[0];
    const fileReader = new FileReader();
    var encodedImage = getBase64(file).then(
        data => {
            var apigClient = apigClientFactory.newClient({
              apiKey: "h5pv2bM96C443KTAdFJoaGURiM2SYbi6IASgpqgf"
            });
    var fileType = file.type + ";base64"
    var body = data;
    var params = {"item": file.name, "bucket": "ur2136-jk4534-b2", "Content-Type": file.type, "x-amz-meta-customLabels": document.getElementById("field_labels").value, "x-amz-acl": "public-read"};
    var addParams = {};
    apigClient.uploadBucketItemPut(params, body, addParams).then(function(res) {
        if(res.status == 200)
        {
         document.getElementById("display-text").innerHTML="Uploaded!";
        }
    })
});
}

function resetSearchbar() {
    document.getElementById("field_search").value = "";

}

function searchPhoto()
{
    document.getElementById("album").innerHTML = ''; 
    document.getElementById("display-text").innerHTML = ''; // added one line
     var apigClient = apigClientFactory.newClient({
        apiKey: "h5pv2bM96C443KTAdFJoaGURiM2SYbi6IASgpqgf"
     });
     var body = {};

     // what if I did this: 
    recognition.onresult = function(event) {
        if (event.results.length > 0) {
            console.log(event.results[0][0].transcript);
            var voiceQuery = event.results[0][0].transcript;
            document.getElementById("field_search").value = voiceQuery;
            // then params should capture voiceQuery in the following
        }
    };
     // ends here


     var params = {q: document.getElementById("field_search").value};
     // we would need to edit params to support voice search 
     // once we have the user's voice recognized, we fill it in field_search
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

