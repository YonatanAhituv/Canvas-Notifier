console.log('hi there');
function validURL(inputURL) {
    console.log(inputURL)
    try {
        var url = new URL(inputURL);
    } catch (_) {
        return false;  
    }
    console.log("passed catch")
    console.log(url.protocol)
    if (url.protocol == "") {
        return false;
    }
    return true;
}

window.onload = function () {
    var url = document.getElementById("url");
    console.log(url.value);
    url.addEventListener("keyup", function (e) {
        console.log("Key up!")
        urlValue = "";
        urlHref = "";
        helperText = "<i>Enter your url first for help!</i>";
        if (validURL(this.value)) {
            console.log("url is valid")
            urlValue = "1. Go to your profile settings on Canvas: " + url.value + "/profile/settings";
            urlHref = url.value + "/profile/settings";
            helperText = "2. Scroll down to 'Approved Integrations'<br>3. Click on New Access Token<br>4. Enter a purpose in the text box<br>5. Enter an expiration date if you'd like<br>6. Press generate token!<br>7. Copy the token in bold at the top and paste it below!"
        }
        var helperUrl = document.getElementById("helperURL");
        console.log(helperUrl)
        helperUrl.innerHTML = urlValue;
        helperUrl.href = urlHref;
        var helper = document.getElementById("helper");
        console.log(helper)
        helper.innerHTML = helperText;
    }, false);
};