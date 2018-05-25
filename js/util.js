    /* cookie */
    var get_cookie_by_name = function(name){
        var val = "";
        var cookies = document.cookie.split("; ");
        for (var i = 0; i < cookies.length; i++) {
            var arr_cookie = cookies[i].split("=");
            if (arr_cookie[0] == name) {
                var cookie_val = unescape(arr_cookie[1]);
                val = cookie_val;
            }
         }
        return val;
    }
    
    //通常のcookie
    var  set_cookie = function (name, value){
        var nowtime     = new Date().getTime();
        var clear_time  = new Date(nowtime + (60 * 60 * 1000 ));
        var expires     = clear_time.toGMTString();
        document.cookie = name + "=" + escape(value) + "; path=/; expires=" + expires;
    }
    //一時的なcookie
    var  set_cookie_temporary = function (name, value){
        document.cookie = name + "=" + escape(value) + "; path=/;";
    }


    // ga event 送信
    var send_ga_event = function(){
        ga('send', 'event',  'カテゴリ', 'アクション', ラベル, '0', {'nonInteraction' : 1});
    }

   //uuid生成
    function generateUuid() {
        var chars = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".split("");
        for (var i = 0, len = chars.length; i < len; i++) {
            switch (chars[i]) {
                case "x":
                    chars[i] = Math.floor(Math.random() * 16).toString(16);
                    break;
                case "y":
                    chars[i] = (Math.floor(Math.random() * 4) + 8).toString(16);
                    break;
            }
        }
        return chars.join("");
    }
    
