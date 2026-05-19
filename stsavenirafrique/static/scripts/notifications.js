function prettyDate(time) {
    var date = new Date(time),
        diff = (((new Date()).getTime() - date.getTime()) / 1000),
        day_diff = Math.floor(diff / 86400);
    var year = date.getFullYear(),
        month = date.getMonth()+1,
        day = date.getDate();

    if (isNaN(day_diff) || day_diff < 0 || day_diff >= 31)
        return (
            year.toString()+'-'
            +((month<10) ? '0'+month.toString() : month.toString())+'-'
            +((day<10) ? '0'+day.toString() : day.toString())
        );

    var r =
    (
        (
            day_diff == 0 &&
            (
                (diff < 60 && "moins d'une minute")
                || (diff < 120 && "il y a 1 minute")
                || (diff < 3600 && "il y a " + Math.floor(diff / 60) + " minutes")
                || (diff < 7200 && "il y a 1 houre")
                || (diff < 86400 && "il y a " + Math.floor(diff / 3600) + " heures")
            )
        )
        || (day_diff == 1 && "hier")
        || (day_diff < 7 && "il y a " +day_diff + " jours")
        || (day_diff < 31 && "il y a " + Math.ceil(day_diff / 7) + " semaines")
    );
    return r;
}

function getNewNotifications(){
    $.getJSON('/notifications/api/unread_list/', function(data){
        if(data.unread_count > 0) {
            $('#notif_count').text(data.unread_count)
        }
        $.map(data.unread_list, (notification)=>{
            $.getJSON('/user/user_full_name/'+ parseInt(notification.actor_object_id), function(user){
                if (notification.description =='0'){
                    $(`<a class='notif-link' href='/liste-des-notifications'><li class="notification-box"><strong>${notification.actor}</strong><sub>(${user.full_name})</sub> ${notification.verb} <strong>${notification.action_object}</strong>${notification.target?` au <strong>${notification.target}</strong>`:''} <small class='text-warning'>${prettyDate(notification.timestamp)}</small></li></a>`).insertBefore(".notif-footer")
                }
                else if(notification.description=='1') {
                    $(`<a class='notif-link' href='/details-d-un-courrier/${notification.action_object_object_id}/1'><li class="notification-box"><strong>${notification.actor}</strong><sub>(${user.full_name})</sub> ${notification.verb} <strong>${notification.action_object}</strong>${notification.target?` au <strong>${notification.target}</strong>`:''} <small class='text-warning'>${prettyDate(notification.timestamp)}</small></li></a>`).insertBefore(".notif-footer")
                } else if(notification.description=='2') {
                    $(`<a class='notif-link' href='/details-d-un-courrier/${notification.action_object_object_id}/3'><li class="notification-box"><strong>${notification.actor}</strong><sub>(${user.full_name})</sub> ${notification.verb} <strong>${notification.action_object}</strong>${notification.target ? ` au <strong>${notification.target}</strong>` : ''} <small class='text-warning'>${prettyDate(notification.timestamp)}</small></li></a>`).insertBefore(".notif-footer")
                } 
                if(notification.description=='3'){
                    $(`<a class='notif-link' href='/details-d-un-courrier/${notification.action_object_object_id}/3'><li class="notification-box"><strong>${notification.actor}</strong><sub>(${user.full_name})</sub> ${notification.verb} <strong>${notification.action_object}</strong>${notification.target?` au <strong>${notification.target}</strong>`:''} <small class='text-warning'>${prettyDate(notification.timestamp)}</small></li></a>`).insertBefore(".notif-footer")
                }
                if(notification.description=='4'){
                    $(`<a class='notif-link' href='/details-d-un-courrier/${notification.action_object_object_id}/4'><li class="notification-box"><strong>${notification.actor}</strong><sub>(${user.full_name})</sub> ${notification.verb} <strong>${notification.action_object}</strong>${notification.target?` au <strong>${notification.target}</strong>`:''} <small class='text-warning'>${prettyDate(notification.timestamp)}</small></li></a>`).insertBefore(".notif-footer")
                }
            
            })
        })
    });
    
}

getNewNotifications()

setInterval(() =>{
    getNewNotifications()
}, 200000000)
