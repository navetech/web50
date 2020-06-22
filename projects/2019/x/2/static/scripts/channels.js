document.addEventListener('DOMContentLoaded', () => {

    let items_count = document.querySelectorAll(".channel-item").length;

    const template_item = Handlebars.compile(document.querySelector('#channel').innerHTML);
    const template_item_none = Handlebars.compile(document.querySelector('#channel-none').innerHTML);

    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // When a channel is created, add channel
    socket.on('announce create channel', channel => {

        let same_user = false;
        if (channel.creator.id === session_user_id) {
            same_user = true;
        }

        const context = {
            channel: channel,
            same_user: same_user
        }

        const content = template_item(context);
        const old_content = document.querySelector('#channels').innerHTML
        document.querySelector('#channels').innerHTML = content + old_content;
        items_count++;

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

                    const content = template_item_none();
                    const old_content = document.querySelector('#channels').innerHTML;
                    document.querySelector('#channels').innerHTML = content + old_content;
            
                    const id_elem_add = `#channel-null`;
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