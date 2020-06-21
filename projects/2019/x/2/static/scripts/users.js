document.addEventListener('DOMContentLoaded', () => {

/*
    console.log("user")
    console.log(navigator.userLanguage);
    console.log("system")
    console.log(navigator.systemLanguage);
    console.log("browser")
    console.log(navigator.browserLanguage);
    console.log("language")
    console.log(navigator.language);
    console.log("languages")
    console.log(navigator.languages);

    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    console.log("timezone");
    console.log(timezone);
*/
/*
    const currentTime = moment().tz(timezone).format();
    console.log("currentTime");
    console.log(currentTime);
*/

/*
    var d = new Date();
    var tz = d.toString().split("GMT")[1].split(" (")[0]; // timezone, i.e. -0700
    console.log("offset");
    console.log(tz);
    var tz = d.toString().split("GMT")[1]; // timezone, i.e. -0700 (Pacific Daylight Time)
    console.log("name");
    console.log(tz);

    var d = new Date().toString();
    var gmtRe = /GMT([\-\+]?\d{4})/; // Look for GMT, + or - (optionally), and 4 characters of digits (\d)
    var tz = gmtRe.exec(d)[1]; // timezone, i.e. -0700
    console.log("Re offset");
    console.log(tz);
*/

/*
    var tzRe = /\(([\w\s]+)\)/; // Look for "(", any words (\w) or spaces (\s), and ")"
    var tz = tzRe.exec(d)[1]; // timezone, i.e. "Pacific Daylight Time"
    var tzRe = /\(([\w\s]+)\)/; // Look for "(", any words (\w) or spaces (\s), and ")"
    var d = new Date().toString();
    var tz = tzRe.exec(d)[1]; // timezone, i.e. "Pacific Daylight Time"
    console.log("Re name");
    console.log(tz);
*/

/*
    var d = new Date();
    var tz= d.getTimezoneOffset();
    console.log("timezoneoffset");
    console.log(tz);
*/

/*
    console.log(Intl.getCanonicalLocales('EN-US')); // ["en-US"]
    console.log(Intl.getCanonicalLocales(['EN-US', 'Fr'])); // ["en-US", "fr"]
    console.log(Intl.getCanonicalLocales([]))
*/

const datetime = Intl.DateTimeFormat()
console.log("datetime");
console.log(datetime);
const options = datetime.resolvedOptions()
console.log("options");
console.log(options);
const timezone = options.timeZone;
console.log("timezone");
console.log(timezone);

    var template = Handlebars.compile(document.querySelector('#usuario').innerHTML);
    console.log(template);

    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // When a user is registered, add user
    socket.on('announce register', user => {

        let same_user = false;
        if (user.id === session_user_id) {
            same_user = true;
        }

        /*
        const d = new Date(user.timestamp);
        console.log(d)
        user.timestamp = d.toString();
*/



        const context = {
            user: user,
            same_user: same_user
        }

        console.log(template);
        const content = template(context);
        const old_content = document.querySelector('#users').innerHTML
        document.querySelector('#users').innerHTML = content + old_content;

        const id = `#user${user.id}`
        const element = document.querySelector(id)

        element.addEventListener('animationend', () =>  {
            element.style.animationPlayState = 'paused';
            let clo = element.getAttribute("class");
            let cln = clo.replace("item-show", "item-hide");
            element.setAttribute("class", cln);
        });

        element.style.animationPlayState = 'running';
    });


    // When a user is unregistered, remove user
    socket.on('announce unregister', user => {

        const id = `#user${user.id}`;
        const element = document.querySelector(id);

        element.addEventListener('animationend', () =>  {
            element.remove();
        });

        element.style.animationPlayState = 'running';
    }); 
});