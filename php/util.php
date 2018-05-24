<?php

/** 
 * 
 * 再利用しそうな処理の雛形を入れていくクラス
 * [ルール]
 * クラス名はパスカルケース
 * 変数名と関数名はスネークケース
 */
class Util{


    /**
     * コンストラクタ
     */
    public function __construct(){

    }

//db関連

    /**
     * mysqlへの接続を返す 
     */
    static function db_connect(){
       $user = "";
       $pass = "";
       $host = "";
       $db_name   = "";
       $con =   PDO("mysql:host=${host};dbname=${db_name}", $user, $pass); 
       //$this->db = $con;
       //return $con;
  
    }

    /**
     * queryでsql実行
     *
     */ 
    public function select_by_query(){
         $sql = "SELECT * FROM table ";
         $res = $this->db->query($sql);
         if($res){
             return $res->fetchAll(PDO::FETCH_ASSOC);//連想配列で結果取得
         }else{
             var_dump($res->errorInfo()); //エラー出力
             return false;
         }

    }   

    /**
     * prepared statemanetでsql実行
     * placeholderを?と順番で設定
     */ 
    public function select_by_prepare(){
        $sql = "SELECT * FROM table WHERE id = ?";
        $st = $this->db->prepare($sql);
        $res = $st->execute(["id"]);

        if($res){
            return $st->fetchAll(PDO::FETCH_ASSOC);
        }else{
            var_dump($st->errorInfo());
            return false;
        }
    }   

    /**
     * prepared statemanetでsql実行2 
     * placeholderを連想配列のキー名で設定
     */ 
    public function select_by_prepare2(){
        $sql   = "SELECT * FROM table WHERE id = :id";
        $st    = $this->db->prepare($sql);
        $param = [
            ':id' =>  'id'
        ];
        $res = $st->execute($param);

        if($res){
            return $st->fetchAll(PDO::FETCH_ASSOC);
        }else{
            var_dump($st->errorInfo());
            return false;
        }
    }   

    /**
     * テーブルに既に該当dataが登録されているか確認
     * @param 検索条件
     * @return boolean 
     *       存在する場合はtrue 存在しない場合false
     */
    public function check_exists($var){
        $sql = "
            SELECT count(*) as count
            FROM table 
            WHERE id = ? 
            LIMIT 1
        ";
        $st = $this->db->prepare($sql);
        $res = $this->db->execute([$var]);
        
        if($res){
            $res = $res->fetch(PDO::FETCH_ASSOC);
            return  $res['count'] > 0 ?  true  : false;
        }else{
            return false;
        }

    }

//日付け関連
    /**
    * 現在日付け取得関連
    * 
    */
    public function get_date(){
      //**** 1.タイムスタンプの取得 ****//
        //当日
        time();

        //今日から相対的に計算
        strtotime("-1 day"); //昨日
        strtotime("-1 month"); // 一月前

        //文字列から取得
        strtotime("2018-3-1"); //指定日
        strtotime("2018-3-1 -1 month") //指定日からさらに計算       


      //**** 2.日付け文字列の取得 ****//
        //当日
        var_dump (date("Y-m-d H:i:s"));//第2引数 default time()

        
        //今日から相対的に計算
        date("Y-m-d H:i:s",  strtotime("-1 day")) ; //昨日
        date("Y-m-d", strtotime("-1 month") ); // 一月前

        //文字列から取得
        date ("Y-m-d", strtotime("2018-3-1") ); //指定日
        date ("Y-m-d", strtotime("2018-3-1 -1 month")) //指定日からさらに計算       

        //月基準の日付け文字列
        $month       = date("Y-m", $datetime); //yyyy-mmまで
        $month_begin = date("Y-m-01 00:00:00", $datetime); //月初
        $month_end   = date("Y-m-t 23:59:59", $datetime);  //月末

    }

    /**
     * yyyy-mm-dd形式をチェック
     *
     */
    public function check_date_format($date){
        return $date === date("Y-m-d", strtotime($date));
    }


    /**
     * 指定範囲の日付け一覧取得
     * @param 開始日付け、終了日付け
     * @retrun  array 日付け配列
     */
    public function get_date_range($begin, $end){

        /*  開始終了を日付け計算して取得 計算する例)
        $begin = date('Y-m-d', strtotime('now -30 day')); //30日前
        $end = date('Y-m-d', strtotime("now"));//当日
        */

        //引数から計算
        $diff = (strtotime($end) - strtotime($begin)) / ( 60 * 60 * 24);
        for($i = 0; $i <= $diff; $i++) {
            $period[] = date('Y-m-d', strtotime($begin . '+' . $i . 'days'));
        }
        return $period;
    }



//log関連
    /**
     * ファイルにログメッセージの出力例
     * ファイルは当日日付けの入ったファイル想定
     */
    public function print_log($msg){

        //ログファイルは生成済みのイメージ
        /* 
         *   //ログファイル名設定例 
         *   $prefix = "error"; 
         *   $date   = date("Ymd_His");
         *   $this->log_file_name = "${prefix}_${date}.log";
         *   $this->log_file_path = $log_dir.$this->log_file_name;
        */
 
        //整形
        $now     = date("Y-m-d H:i:s");
        $out_msg = "${now} : $msg \n";
        //出力
        file_put_contents($this->log_file_path, $out_msg, FILE_APPEND);//file
        echo $out_msg; //標準出力

    }

   /**
   * とにかくメッセージをログのフォーマットにするだけ
   * ここは日付けを加えているだけ
   * 使うときは関数名は短くしておいたほうが楽
   */
   public function get_log_message($msg){
        $date = date("Y-m-d_H:i:s");
        return "$date $msg";
    }



//メール送信関連
    /**
     * タイトルと本文を引数に日本語含むメール送信
     *
     */
    public function send_mail($title, $body){

        mb_language("Japanese");
        mb_internal_encoding("UTF-8");
        $to      = 'sample@example.jp ';
        $subject = $title;
        $message = $body;
        $headers = 'From: nakamura@test.jp' . "\r\n";
        mb_send_mail($to, $subject, $message, $headers);

    }


    /**
    *  textメールの送信
    *  @param
    *  @return boolean
    */
    public function send_mail_text($mail_data){
         //usleep(100000);  

         $to    = "aaa@bbb" ;
         $bcc   = "foge@huga";
         $cc    = "";
         $from  = "Name <no-reply@hogehoge>";
         $title = "";
         $body  = "";

         //header作成
         $header="From: $from";
         $header.="\n";
         $header.="Cc: $cc";
         $header.="\n";
         $header.="Bcc: $bcc";

         //送信
         mb_internal_encoding("UTF-8");
         return mb_send_mail($to, $title, $body, $header);
    }

    /**
    * htmlメールの送信
    * pear Mailの利用
    * https://www.phpbook.jp/pear/pear_mail/
    * 
    */
    private function send_mail_html($mail_data){
        require_once(__DIR__."/html_mail.class.php");
        $htmlmail = new html_mail();
        $to = [
            'address_1',
            'address_2',
        ];
        $cc  = [];
        $bcc = [];
        $from    = "Name<no-reply@hogehoge>";
        $subject = $mail_data['subject'];
     
        $body    = mb_convert_encoding($mail_data['body'], "ISO-2022-JP", "UTF-8" ); //utf-8から ISO...に変換
        return $htmlmail->main($to, $from, $subject, $body , $cc, $bcc);

    }






      


}
