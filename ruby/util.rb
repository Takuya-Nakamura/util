#condig: utf-8

# 
# [memo]
# クラス名、モジュール名:キャメルケース
# ファイル名、ディレクトリ名:スネークケース
# メソッド名、変数名:スネークケース
#
require 'pp'

class Util

    @con;


# db関連
    # mysqlへの接続取得
    def connect
        require 'mysql'
        host    = ""
        user    = ""
        pass    = ""
        db_name = ""

        return  Mysql.new(host, user, pass, db_name)
    end

    #prepared statementでselect
    def select_by_prepare (id)
        sql = "SELECT * FROM table WHERE id = ?";
        stmt = @con.prepare(sql)
        result = stmt.execute([id]);

    end

    # sql単純実行
    def select_by_query()
        sql = "SELECT * FROM table ";
        res = @con.query(sql)

        arr_return = []
        res.each do |row|
            arr_return << row
        end

        return arr_return
    end


    # sql実行結果1件 
    def select_by_query()
        sql = "SELECT * FROM table LIMIT 1";
        if  @con.query(sql).fetch()  then
            return res.first
        else
           return "";
        end
    end



#http 関連
    # httpdでのファイル取得
    def get_file_by_http 
        require 'open-uri'
        require "openssl"

        # オレオレ証明書無視設定
        OpenSSL::SSL.module_eval { remove_const(:VERIFY_PEER) }
        OpenSSL::SSL.const_set(:VERIFY_PEER, OpenSSL::SSL::VERIFY_NONE)
        file = open('https://xxxxxxx.jp/yyyy.tsv').read

    end


# 日付関連
    # 基本的な日付け文字列の取り方
    def date1 

        #### 日時2
        require 'date'
        date_time = DateTime.now

        #当日
        puts date_time.strftime("%Y-%m-%d") # 2018-05-24
        puts date_time.strftime("%Y-%m-%d %H:%M:%S") # 2018-05-24 15:02:15

        #指定日から取得
        one_day =  DateTime.strptime('2018-10-11', '%Y-%m-%d');
        puts one_day.strftime("%Y-%m-%d")

        one_day =  DateTime.strptime('2018-10-11 23:59:59', '%Y-%m-%d %H:%M:%S');
        puts one_day.strftime("%Y-%m-%d %H:%M:%S")

        ##計算
        # N月
        one_day2 = one_day >> 1;  #月加算 減産は <<
        puts one_day2.strftime("%Y-%m-%d %H:%M:%S")

        # N日
        one_day3 = one_day + 1;
        puts one_day3.strftime("%Y-%m-%d %H:%M:%S")

        # N時間
        one_day4 = one_day + Rational(1,24);  #1時間 /24
        puts one_day4.strftime("%Y-%m-%d %H:%M:%S")

        # N分
        one_day5 = one_day + Rational(1,24*60);  #1時間/24*60 = 分
        puts one_day5.strftime("%Y-%m-%d %H:%M:%S")

        #### 日付のみ
        require 'date'
        date = Date.today
        puts date.strftime("%Y-%m-%d") # 2018-05-24
        puts date.strftime("%Y-%m-%d %H:%M:%S") # 2018-05-24 00:00:00
       
    end

    # 日付け関連2
    def date2
        #月末月初の取得 
        require 'date'
        day  = Date.parse("2018-02-05"); #特定日付けの場合
        #day = Date.today() #今日の場合

        #月初の取得
        begin_date = Date::new(day.year, day.month, 1) #月初

        #月末の取得
        end_date = (begin_date >> 1 ) -1 #1月進めて1日戻す

    end
    

    #  

end

