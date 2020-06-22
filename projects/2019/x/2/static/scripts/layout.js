var session_user_id;

document.addEventListener('DOMContentLoaded', () => {

    // Initialize new request
    const request = new XMLHttpRequest();
    request.open('GET', '/session');

    // Callback function for when request completes
    request.onload = () => {

        // Extract JSON data from request
        session_user_id = JSON.parse(request.responseText);
    }

    // Send request
    request.send();
})
