/**
 *
 *概要
 *  webpush通知許可のダイアログの表示と登録
 */


/**** functions ****/
/**
 * npm web-push パッケージ サイトを参考
 *    https://www.npmjs.com/package/web-push
 */
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/\-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

/**
 * serviceWorkerからSubscriptionを取得する
 */
async function getsubscription() {
  var reg =  await navigator.serviceWorker.ready;
  var sub = await reg.pushManager.getSubscription();
  return sub;
}

/**
 * Subscriptionを取得するためにサーバ側で生成された
 * WebPush送信のための公開鍵をAPI経由で取得する
 *
 * TODO:取得元を変更
 */
async function getPublicKey() {
  /*
  var res = await fetch('getpush', { //httpリクエスト
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' }
                  }).then((res) => res.json());
  */
  const publicKey="";
  return publicKey;
}

/**
 * サーバから取得した公開鍵を元に
 * ServiceWorkerからSubscriptionを取得する
 */
async function subscribe(option) {
  var reg = await navigator.serviceWorker.ready;
  var sub = await reg.pushManager.subscribe(option);
  return sub;
}

/**
 * サーバから公開鍵を取得し、
 * ServiceWorkerからSubscriptionを取得する
 */
async function initSubscribe() {
  var vapidPublicKey = await getPublicKey();
  let option = {
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(vapidPublicKey)
  }
  return await subscribe(option);
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

/**** main  ****/
/**
 * ページの読み込みが完了すれば、
 * WebPushを受け取るための準備を行う
 */
window.addEventListener('load', async () => {
    console.log("webpush run")
    navigator.serviceWorker.register('/serviceworker.js', {scope: "/"});

    /*重要:SCOPE=(sw登録許可を求められる範囲)の設定がないと、
     * serviceworker.jsのディレクトリパスがつかわれ、そこ以下じゃないと動かない...ハズ.
     * ->chromeの制約でファイル位置以上のスコープは設定できない。
     *
     * */
    //navigator.serviceWorker.register('serviceworker.js');
    var sub = await getsubscription();
    var id = get_cookie_by_name_for_push('id');

    if (typeof js_class == 'undefined') {
        js_class = "";
    };

    if (!sub) {
        console.log("create subscription");

        // サブスクリプションが無ければ..ブラウザに通知許可を要求する
        var permission = await Notification.requestPermission();

        if (permission === 'denied') {
            //return alert('ブラウザの通知設定をONにしてください');
            return false;

        } else {
            //初subscriptionの取得
            sub = await initSubscribe();

            // サーバー側では、重複登録の有無を確認して保存
            var endpoint = sub.endpoint;
            var auth = sub.getKey('auth') ? btoa(String.fromCharCode.apply(null, new Uint8Array(sub.getKey('auth')))) : '';
            var publick_key = sub.getKey('p256dh') ? btoa(String.fromCharCode.apply(null, new Uint8Array(sub.getKey('p256dh')))) : '';


            //serversideにデータ送信
            $.ajax({
                type:'POST',
                url: '/webpush/regist.php',
                data:{
                    "endpoint": endpoint,
                    "auth": auth,
                    "publick_key": publick_key,
                    "id": id,  //globalに定義
                    "class":js_class //globalに定義
                },
                dataType:'text'
            }).then(
                function(res){
                    //success
                    console.log(res);
                    new Notification('通知設定をしました');
                },
                function (err){
                    console.log("push regist error ajax");
                    sub.unsubscribe();//subscriptionの削除
                    alert("登録処理に失敗しました.");
                }
            );
        } //if permission
  }else{
      //alert("既に通知を許可頂いてます。");
  } //if sub

  console.log("webpush end");
});

