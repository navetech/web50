let session_user_id;

const socket = connectToServer();

let room = null;
let roomJoin = null;
let page = null;
let idCommunicator = null;



function convertToLocaleString(timestamp) {
    const locales = window.navigator.language;
    const options = {dateStyle: 'full', timeStyle: 'full'};

    const d = new Date(timestamp);
    return d.toLocaleString(locales, options);
}


function connectToServer() {
    let s = localStorage.getItem('socket');
    console.log(localStorage.getItem('socket'));

    if (!s || s.disconnected) {
        // Connect to websocket
//        const url = location.protocol + '//' + document.domain + ':' + location.port;
        console.log(url);
        const url2 = window.location;
        console.log(url2);
        s = io.connect(url);

        localStorage.setItem('socket', s);
        console.log(localStorage.getItem('socket'));
    }
    return s;
}


function getRoom() {
    return localStorage.getItem('room');
}


function setRoom(room_) {
    room = room_;
    localStorage.setItem('room', room);
}


function changeRoom(page, idCommunicator) {
    room = getRoom()
    if (room) {
        leaveRoom(room);
    }
    else {
        roomJoin = joinRoom(page, idCommunicator);
    }
}


function leaveRoom(room_) {
    if (room_) {
        const data = {'room': room_};
        socket.emit('leave', data);
    }
}


function joinRoom(page_, idCommunicator_) {
    if (!page_) {
        return null;
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
    return room_;
}


socket.on('connect', () => {
    setRoom(null);
});


socket.on('left', () => {
    setRoom(null);
    roomJoin = joinRoom(page, idCommunicator);
});


socket.on('joined', () => {
    setRoom(roomJoin);
});
