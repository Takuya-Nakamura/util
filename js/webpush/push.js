/**
* nodejs
* webpushの送信処理
*
/

'use strict';
/**
 * 送信処理
 */
const send_message = function(push, user, message){

    return new Promise( (resolve, reject) => {

        //subscription
        const data = {
            'endpoint': user.endpoint,
            'userAuth': user.auth,
            'userPublicKey': user.publick_key
        };

        const pushSubscription = {
            endpoint: data.endpoint,
            keys: {
                auth: data.userAuth,
                p256dh: data.userPublicKey
            }
        }

        //option
        const options = {
            TTL: 86400, //単位 秒 1日分86400  最大値などの規定は無いらしい
            vapidDetails: {
              subject: "タイトル",
              // 先ほど生成したVAPIDの鍵情報をセットする
              publicKey: "",
              privateKey: "",
            }
        }

        var json_msg = JSON.stringify(message);
        //send
        push.sendNotification(pushSubscription, json_msg, options)
            .then(function(result) {
                //success
                console.log("send_message success :"+ user.id + ":" + message.title);
                resolve();
            })
            .catch(function(err) {
                //err
                console.log("send_message failed :"+ user.id);

                /* failedの場合は該当レコードに削除フラグを立てる */
                update_users_delete_flag(user)
                    .then(function(){
                        console.log("update_users_delete_flag success")
                        reject(); //send_message err
                    })
                    .catch(function(){
                        console.log("update_users_delete_flag failed")
                        reject(); //send_message err
                    })
            });

    }); //promise


} //function


/**
 * 送信対象記事を取得
 */
const get_articles = function(){
    return new Promise( (resolve, reject) => {
        //main
        const sql = "\
            SELECT * FROM \
            ( \
              SELECT * \
              FROM  webpush_articles  \
              WHERE send = 0  /*未送信*/ \
              AND article_published >  now() - interval 1 day  /*公開が一定時間内*/ \
              ORDER BY  article_published DESC \
            ) sq1  \
            LIMIT 5;\
        ";

        var res = [];
        con.query(sql, (err, rows, fields) =>{
            //err
            if(err) reject(err);

            //success
            resolve(rows);
        });

    }) //promise

}//function


/**
 * 送信対象サブスクリプション(users)を取得
 */
const get_users = function(){
    return new Promise( (resolve, reject) => {

        //main
        const sql = "SELECT * FROM webpush_users where delete_flag = 0;";

        var res = [];
        con.query(sql, (err, rows, fields) =>{
            //err
            if(err) reject(err);
            //success
            resolve(rows);
        });

    }) //promise

}//function


/**
 * 送信済み記事にフラグを立てる
 *
 */
const update_send_status = function(entry_id){
    return new Promise( (resolve, reject) => {
        //main
        const sql = "UPDATE webpush_articles SET send = 1 where entry_id = ?;";
        var res = [];
        con.query(sql, [entry_id], (err, rows, fields) =>{
            if(err) reject(err);
            resolve(rows);
        });
    }) //promise

}//function


/**
 *送信失敗ユーザーにフラグをたてて、送信対象から除外する
 *
 */
const update_users_delete_flag = function(users){
    return new Promise( (resolve, reject) => {
        //main
        const sql = "UPDATE webpush_users SET delete_flag = 1, deleted = ?  WHERE id = ?;";
        var deleted = str_now();
        var res = [];

        //
        con.query(sql, [deleted, users.id], (err, rows, fields) =>{
            if(err) reject(err);
            resolve(rows);
        });


    }) //promise
}//function


const str_now = function(){
    var dt = new Date();
    return  dt.toFormat("YYYY-MM-DD HH:24MI:SS");

}

/**************/
/**** main ****/
/**************/

//初期設定
console.log("start push");
require('date-utils');
const push = require('web-push');
const GCM_API_KEY = ''; 
push.setGCMAPIKey(GCM_API_KEY);

//db接続
const mysql = require('mysql');
const con = mysql.createConnection({
    host : '127.0.0.1',
    user : '',
    password : '',
    port : 3306,
    database: ''
});
con.connect();

//送信対象の取得
const async = require('async');
get_articles()
    .then(function(articles){
        if(articles.length == 0){
            console.log("no news articles");
            process.exit(0);

        }else{
            //loop1
            async.eachSeries( articles, function(article, callback1){

                /*メッセージ作成*/
                var message = {
                    title: article.entry_title,
                    body: article.entry_url,
                    icon: "画像",
                    link: article.entry_url + "?wp",
                };

                /* 送信 */
                get_users()
                    .then(function(users){
                        if(users.length == 0){
                            console.log("no users");
                            process.exit(0);
                        }else{
                            // loop2
                            async.eachSeries(users, function(user, callback2){
                                 //送信実行
                                 send_message(push, user, message)
                                     .then( function(){
                                         callback2();
                                     })
                                     .catch(function(){
                                         callback2();
                                     })

                            }, function(err){ //loop2 callback = loop2終了時に実行
                                //送信済みとして更新
                                update_send_status(article.entry_id)
                                    .then(function(){
                                        callback1();
                                    })
                            });
                        }//if
                    });


            }, function(err){ //loop1 callback = loop1終了時に実行
                con.end();
                console.log("end push");
            }); //async each


        }//if article length
    })

