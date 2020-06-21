var session_user_id;

document.addEventListener('DOMContentLoaded', () => {

    // Initialize new request
    const request = new XMLHttpRequest();
    request.open('GET', '/session');

    // Callback function for when request completes
    request.onload = () => {

        // Extract JSON data from request
        session_user_id = JSON.parse(request.responseText);

//        console.log(window.location.href)
//        window.location.href = window.location.href;
//        console.log(window.location.href)
}

    // Send request
    request.send();
})
