let items_count = 0;
let template_item;
let template_item_none;

document.addEventListener('DOMContentLoaded', () => {
    items_count = document.querySelectorAll(".channel-item").length;

    template_item = Handlebars.compile(document.querySelector('#channel').innerHTML);
    template_item_none = Handlebars.compile(document.querySelector('#channel-none').innerHTML);

    // Connect to websocket
    let socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    
    // Initialize new request
    const request = new XMLHttpRequest();
    request.open('GET', '/api/channels');

    // Callback function for when request completes
    request.onload = () => {
        // Extract JSON data from request
        const channels = JSON.parse(request.responseText);
        showChannels(channels);
    }
    // Send request
    request.send();


    // When a channel is created, add channel
    socket.on('announce create channel', channel => {
        const item_show_hide = 'item-show';
        addChannel(channel, item_show_hide);

        const id_elem_add = `#channel${channel.id}`;
        const elem_add = document.querySelector(id_elem_add);

        elem_add.addEventListener('animationend', () =>  {
            elem_add.style.animationPlayState = 'paused';
            let class_old = elem_add.getAttribute("class");
            let class_new = class_old.replace("item-show", "item-hide");
            elem_add.setAttribute("class", class_new);

            const id_elem_remove = `#channel-null`;
            const elem_remove = document.querySelector(id_elem_remove);
    
            if (elem_remove) {
                elem_remove.addEventListener('animationend', () =>  {
                    elem_remove.remove();
                });
                elem_remove.style.animationPlayState = 'running';
            }
        });
        elem_add.style.animationPlayState = 'running';
    });


    // When a channel is removed, remove channel
    socket.on('announce remove channel', channel => {
        const id_elem_remove = `#channel${channel.id}`;
        const elem_remove = document.querySelector(id_elem_remove);

        if (elem_remove) {
            elem_remove.addEventListener('animationend', () =>  {
                elem_remove.remove();

                items_count--;
                if ((items_count < 1) &&
                    (document.querySelector(`#channel-null`) == null)) {
                        const context = {
                            item_show_hide: 'item-show'
                        }
                        const content = template_item_none(context);
                        const old_content = document.querySelector('#channels').innerHTML;
                        document.querySelector('#channels').innerHTML = content + old_content;
                
                        const id_elem_add = '#channel-null';
                        const elem_add = document.querySelector(id_elem_add);
                
                        elem_add.addEventListener('animationend', () =>  {
                            elem_add.style.animationPlayState = 'paused';
                            let class_old = elem_add.getAttribute("class");
                            let class_new = class_old.replace("item-show", "item-hide");
                            elem_add.setAttribute("class", class_new);
                        });
                    elem_add.style.animationPlayState = 'running';
                }
            });
            elem_remove.style.animationPlayState = 'running';
        }
    });
});


function showChannels(channels) {
    items_count = 0;
    document.querySelector('#channels').innerHTML = '';

    const item_show_hide = 'item-hide';
    if (channels.length > 0) {
        channels.reverse().forEach(channel => {
            addChannel(channel, item_show_hide);
        });
    }
    else {
        const context = {
            item_show_hide: item_show_hide
        }
        const content = template_item_none(context);
        document.querySelector('#channels').innerHTML = content;
    }
}


function addChannel(channel, item_show_hide) {
    let same_user = false;
    if (channel.creator.id === session_user_id) {
        same_user = true;
    }

    const locales = window.navigator.language;
    const options = {dateStyle: 'full', timeStyle: 'full'};

    const d = new Date(channel.timestamp);
    channel.timestamp = d.toLocaleString(locales, options);

    const context = {
        channel: channel,
        item_show_hide: item_show_hide,
        same_user: same_user
    }

    const content = template_item(context);
    const old_content = document.querySelector('#channels').innerHTML
    document.querySelector('#channels').innerHTML = content + old_content;
    items_count++;
}
