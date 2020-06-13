document.addEventListener('DOMContentLoaded', () => {

    document.querySelector('#form').onsubmit = () => {

        // Initialize new request
        const request = new XMLHttpRequest();
        const name = document.querySelector('#name').value;
        request.open('POST', '/register', false);

        // Add data to send with request
        const data = new FormData();
        data.append('name', name);

        const options = Intl.DateTimeFormat().resolvedOptions()
        data.append("locale", options.locale);
        data.append("timezone", options.timeZone);

        const d = new Date();
        data.append("timezone-offset", - d.getTimezoneOffset() * 60);

        // Send request
        request.send(data);
        return true;
    };

});