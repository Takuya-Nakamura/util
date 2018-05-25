/**
 *
 *概要
 *  会員情報がwebpush送信対象テーブルに登録されているかチェック。
 *  未ログインの状態でwebnpush登録した場合、会員情報が登録されないので
 *  ログイン状態でのアクセス時に再取得処理を行う。
 *
 */


/**** functions ****/

/**
 * serviceWorkerからSubscriptionを取得する
 */
async function getsubscription() {
  var reg =  await navigator.serviceWorker.ready;
  var sub = await reg.pushManager.getSubscription();

  return sub;
}

var get_cookie_by_name_for_push = function(name){
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


/****  main  ****/
window.addEventListener('load', async () => {

    var cn = "wp_id_flag";
    var wp_id_flag = get_cookie_by_name(cn);
    var id = get_cookie_by_name('id');

    if (typeof js_class == 'undefined') {
        js_class = "";
    };

    if(wp_id_flag != 1){ //会員情報登録フラグが無い場合 =

        if(  sfid  ){ //会員情報登録済みflagなし かつ  ログイン状態

            //webpush許可設定状態を確認する
            navigator.serviceWorker.register('/serviceworker.js', {scope: "/"});
            var sub = await getsubscription();
            if(!sub){  !subで判定しないと上手くいかない...
                //webpush未許可
            }else{
                //webupush 許可かつ
                //会員情報データ未登録
                var endpoint = sub.endpoint;
                var auth = sub.getKey('auth') ? btoa(String.fromCharCode.apply(null, new Uint8Array(sub.getKey('auth')))) : '';
                var publick_key = sub.getKey('p256dh') ? btoa(String.fromCharCode.apply(null, new Uint8Array(sub.getKey('p256dh')))) : '';
                $.ajax({
                    type:'POST',
                    url: '/webpush/regist.php',
                    data:{
                        "endpoint": endpoint,
                        "auth": auth,
                        "publick_key": publick_key,
                        "id": id,  
                        "class" : js_class, 
                        "type": "update",
                    },
                    dataType:'text'
                }).then(
                    function(res){
                        //success
                        console.log(res);
                        //if(res =='success'){
                        if(res.match(/success$/)){
                            console.log("ajax update suceess");
                            //sfid設定済み cookie set
                            set_cookie(cn, 1);

                        }else{
                          // error
                          console.log("ajax update error");
                        }

                    },
                    function (err){
                        //err
                        console.log("ajax update error");

                    }
                );

            }//if sub
        }else{

        }//if sfid

    }else{
        console.log("ok");

    }// if wpflag

});



