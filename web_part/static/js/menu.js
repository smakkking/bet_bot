var stop_bot = false
var last_data = {}
var WAIT_TIME = 60
function update_bet() {
    if (!stop_bot) {
        $.getJSON(
            "/account/renew", 
        function(data){
            console.log(data)
            for (let key in data) {
                if (!last_data[key] || (String(last_data[key]) != String(data[key]))) {
                    // this happens if data[key] is new
                    last_data[key] = data[key];
                    data[key] = JSON.stringify(data[key]);
                } else {
                    data[key] = 'old';
                } 
            }  
            try_bet(data);    
            setTimeout('update_bet()', WAIT_TIME * 1000);
        })
    }
};
function try_bet(data) {
    $('#lastdatafield').empty();
    $.getJSON("/account/bet",
        data, function(success_bet) {
        console.log('Congr');
        for (let key in success_bet) {
            $('#lastdatafield').append(
                '<p><b>' + key + '</b> : ' + success_bet[key] +'</p>'
            );
        }
    })
}; 
function create_bot() {
    stop_bot = false;
    new_iteration = true;
    if ($.cookie('sub_status') == 'False') {
        location.href = "/account/subscribe";
    } else {
        $.ajaxSetup({cache : false});
        update_bet();
    }
};