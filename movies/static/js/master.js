var year = {{pk}};

var movieSocket = new WebSocket('ws://'+ window.location.host + '/ws/movies/' + year + '/');

movieSocket.onmessage = function(e) {
    var data = JSON.parse(e.data);
    var message = data['message'];
    document.querySelector('.inner-centered-list').value += (message) // + '\n');
};

movieSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};
