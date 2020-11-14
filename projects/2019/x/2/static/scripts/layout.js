let session_user_id;

const socket = connectToServer();

let room = null;
let page = null;
let idCommunicator = null;



function convertToLocaleString(timestamp) {
    const locales = window.navigator.language;
    const options = {dateStyle: 'full', timeStyle: 'full'};

    const d = new Date(timestamp);
    return d.toLocaleString(locales, options);
}


function connectToServer() {
    // Connect to websocket
    const url = location.protocol + '//' + document.domain + ':' + location.port;
    const url2 = window.location;
    s = io.connect(url);
    return s;
}


function joinRoom(page_, idCommunicator_) {
    if (!page_) {
        return;
    }

    let room_;
    if (idCommunicator_) {
        room_ = `${page_} ${idCommunicator_}`;
    }
    else {
        room_ = `${page_}`;
    }
    const data = {'room': room_};
    socket.emit('join', data);
}


socket.on('connect', () => {
    room = null;
});


socket.on('joined', data => {
    room = data['room'];
});
