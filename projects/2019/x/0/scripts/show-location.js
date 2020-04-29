var lat = document.getElementById("show-latitude");
var long = document.getElementById("show-longitude");

function getLocation()
{
    if (navigator.geolocation)
    {
        navigator.geolocation.getCurrentPosition(showPosition);
    }
    else
    {
        x.innerHTML = "Geolocation is not supported by this browser.";
    }
}

function showPosition(position)
{
    lat.innerHTML = position.coords.latitude;
    long.innerHTML = position.coords.longitude;
}
