#### import ####
import sys
sys.path.append("../")
import App

from  pprint import pprint  as pp

import numpy as np
import pandas as pd
from pandas import Series, DataFrame

import sklearn
#from sklearn.linear_model import LinearRegression
#from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn import metrics

import time

class Logi:
    """ ロジスティック回帰実行 """

    def __init__(self):
        #db接続の取得
        app = App.AppClass()
        self.db = app.db_con()


    def main(self, type):
        """ main """ 
        pp ("main start")
        res = self.set_var(type) #初期変数セット

        if res == 0 :
            pp("argument type error")#引数不正
            return 0

        pp("main get_user start")
        arr_user = self.get_user_list()

        for user in arr_user :
            self.main2(user['member'])

    #end main

    def set_var(self, type) :
        """ 分析対象によって変更する変数のセット """ 

        #self.a_type = "%s_logistic" % type
        self.a_type = type
        if  'shinryoka' in type :
            self.select_join_table = "page_shinryoka_hz"

        elif 'shikkan' in type:
            self.select_join_table = "page_shikkan_hz"

        elif 'sonota' in type :
            self.select_join_table = "page_sonota_hz"

        elif 'yakuzai' in type :
            self.select_join_table = "page_yakuzai_hz"

        elif 'cat' in type :
            self.select_join_table = "page_cat_hz"

        elif 'all' in type  :
            self.select_join_table = "page_all_tag_hz"

        else: 
            pp("a_type error")
            return 0

        #end if

        return 1
    #end set_var


    
    def main2(self, sfid):
    #def main(self, sfid=""):
        start_time = time.time()
        pp ("main2 get_data start")

        #dbからのデータの取得と加工
        input_data = self.get_input_data(sfid)
        if len(input_data) == 0 :
            return 0
  
        input_data = self.convert_input_data(input_data)
        self.time(start_time)


        # logistic回帰分析用データの作成
        # TODO:保存はX回実行しての中央値をとったほうが無難そう
        pp("main2 analyze start")
        mean_row_len = 0;
        max = 10
        count = 0
        while mean_row_len == 0 and count < max:
            arr_res = []
            for var in range(0, 11): #試行回数は奇数回
                arr_res.append( self.analyze(input_data) )
            mean_row = self.get_mean_row(arr_res, 'seido');
            mean_row_len = len(mean_row)
            count+=1
 
        self.time(start_time) 


        if len(mean_row) == 0 :
            pp("loop over")
        else :    
            self.save_result(sfid, self.a_type, mean_row['seido'], mean_row['model'] )
        # 結果の保存 analyze_result_1
        #self.save_result()
        pp('end')       
    #end main  


    def save_result(self, sfid, a_type, seido, mode_json ) :
        """ 1件づつデータを保存(upsert..??) """
        # insert igonore
        #sql = """INSERT IGNORE INTO analyze_result_1 
        #         VALUES
        #         (%s, %s, %s, %s )
        #      """

        #upsert
        sql = """REPLACE  INTO analyze_result_1 
                 VALUES
                 (%s, %s, %s, %s )
              """
        
        cur= self.db.cursor()  #カーソル宣言
        res = cur.execute(sql, [sfid, a_type, seido, mode_json])  #実行
        self.db.commit() #commit必須..?
    #end save_result



    def get_mean_row(self, arr_res, col) :
        """ 結果配列の指定項目の中央値行を取得する """ 
        #seidoの中央値行取得
        arr_target =[]
       
        for val in arr_res :
            arr_target.append(val[col])
 
        df_target = DataFrame(arr_target)
        df_target.columns  = ['A']
        med = df_target.median()
        med = med[0] #valueだけ取得

        #return  df_target[df_target.A == med] #中央値の行を取得(複数あり)
        #medianと一致する先頭の行を返却
        for val in arr_res : 
            if val[col] == med :
                return val
        return []
    #end def



    def analyze(self,  input_data):
        """ logistic regression """
        #### 1.データ準備
        input_df = pd.DataFrame(input_data)

        # 合計が0の列(col)を削除
        """
        sum_df = input_df.sum(axis=0) #項目毎
        dict_sum_df = dict(sum_df) #dictに変換
        for key, val in dict_sum_df.items() :
            if val == 0 :
                input_df.drop(key, axis=1)
        """

        #目的変数
        Y = input_df['open_sts']

        #説明変数
        X = input_df.drop('open_sts', axis=1 )

        """ test dataなし 回帰処理
        # LogisticRegressionクラスのインスタンスを作ります。
        log_model = LogisticRegression()
        # モデル作成
        log_model.fit(X,Y)
        # 精度確認
        res = log_model.score(X,Y)
        #coeff_df = DataFrame([X.columns, log_model.coef_[0]]).T
        #pp(coeff_df)
        """
        
        ####実行 (テストデータ含む)
        #TODO:全部0,全部1のユーザーデータは除外が必要
        try:
            X_train, X_test, Y_train, Y_test = train_test_split(X, Y)
            log_model = LogisticRegression()
            log_model.fit(X_train, Y_train)
            class_predict = log_model.predict(X_test) #testで予測


            #精度の取得 
            seido = (metrics.accuracy_score(Y_test,class_predict)) # 精度

            #係数データの取得
            coeff_df = DataFrame([X.columns, log_model.coef_[0]]).T
            coeff_json = coeff_df.to_json()
            arr_ret = {}
        except ValueError:
            pp('raise value error')
            seido = 0;
            coeff_json = "";

        return { 'seido': seido, 'model':coeff_json } 
 
    #end logistic


    """ db  """
    def get_user_list(self) :

        """ 対象ユーザーリストの取得 """
        #sample user tableから
        #sql = "SELECT member FROM analyze_sample_users "
         

        sql = "SELECT user FROM table"
 
        cur= self.db.cursor()  #カーソル宣言
        cur.execute(sql)  #実行
        rows = cur.fetchall() #全部フェッチ
        return rows
        
    #end get_user_list

 
    def get_input_data(self, id):
        # メールの開封情報など取得
        sql = """
           SELECT 
               *
           FROM mail_open op
           JOIN mail_sum sum
             ON  op.no = sum.no
           JOIN  {select_join_table}  ps
           WHERE 
               id = %s
        """.format( select_join_table=self.select_join_table )


        cur= self.db.cursor()  #カーソル宣言
        cur.execute(sql, [sfid])  #実行
        rows = cur.fetchall() #全部フェッチ
        return rows

    #end get_input_data

    #取得データの加工
    def convert_input_data(self, datas):
        arr_ret = []
  
        for data in datas :
            #不要項目の削除
            del data['entry_id']
            del data['no']
            del data['top_article_entry_id']
            data['open_sts'] = self.convert_open_sts(data['open_sts'])
            
            arr_ret.append(data)
        #end for datas
        return arr_ret

    #end convert_input_data 
 
    def convert_open_sts(self, open_sts):
        if open_sts == '開封済み' :
            return 1
        else :
            return 0
    #end convert_open_sts


    def time(self, start_time) :
        """ 入力時刻からの経過病数表示"""
        duration = time.time() - start_time
        print('%.3f sec' % (duration))
    #end time

#class    


#### run
args = sys.argv
if  len(args) == 1:
   pp("missing argument error")
   sys.exit()

type = args[1]
obj  = Logi()
obj.main(type)

