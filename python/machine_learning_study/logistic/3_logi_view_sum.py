#### import ####
import sys
sys.path.append("../")
import App

from  pprint import pprint  as pp

import time
import json

class LogiViewSum:
    """ 予測結果を表示するためのクラス """
    #entry_id
    #a_type
    #seido
    #sql_common_cond

    def __init__(self):
        #db接続の取得
        app = App.AppClass()
        self.db = app.db_con()
        self.start_time = time.time()


    def main(self):
        pp ("start")
        # get_result_data 

        arr_seido = ['0.8', '0.9', '0.95']
        arr_entry_atype = self.get_entry_atype_list()
        pp(arr_entry_atype) 


        for r in arr_entry_atype :
            for seido in arr_seido :
                self.entry_id = r['entry_id']
                self.a_type   = r['a_type']
                self.seido    = seido

                # exe
                self.get_summary();

    #end main



    ########################
    ### 対象データの取得 ###
    ########################
    def get_entry_atype_list(self):
        sql = """SELECT entry_id, a_type 
              FROM analyze_predict_1 
              GROUP BY entry_id, a_type
              """
        cur = self.db.cursor()  #カーソル宣言
        cur.execute(sql)  #実行
        row = cur.fetchall() 
        return row

    #def

    ######################
    ### 集計結果の保存 ###
    ######################
    def get_summary (self):
        """
            entry_idと分析タイプ毎に各数値を取得する 
            filterとして予測モデルの精度を加える
            seido でフィルターをかける
        """

        #インスタンス変数の設定
        #self.entry_id = '509696'
        #self.a_type   = 'all_logistic'
        #self.seido    = '0.95'

        ## 共通SQLwhere部
        self.sql_common_cond = """ 
            a_type = '{a_type}'
            AND entry_id = '{entry_id}'
            AND seido >= {seido}
        """.format(a_type=self.a_type, 
                   entry_id=self.entry_id, 
                   seido=self.seido)
        """ 数値取得 """
        data= {}
        data['entry_id'] = self.entry_id
        data['a_type']   = self.a_type
        data['seido']    = self.seido

        #予測者数
        data['target_count'] = self.get_target_count()

        #開封と予測
        data['open_predict_count'] = self.get_open_predict_count()

        #開封と予測してマッチ
        #open_predict_match_count
        data['open_match_count'] = self.get_open_match_count()

        #開封一致率
        data['open_match_rate'] = data['open_match_count'] / data['open_predict_count']

        #未開封と予測
        #not_open_predict_count
        data['not_open_predict_count'] = self.get_not_open_predict_count()

        #未開封と予測してマッチ
        #not_open_predict_match_count
        data['not_open_match_count'] = self.get_not_open_match_count()

        #未開封一致率
        data['not_open_match_rate'] = data['not_open_match_count'] / data['not_open_predict_count']


        """ save """
        self.save(data)
        pp (data) 

    #end
 
    """ 予測対象全体 """
    def get_target_count(self) :
        sql = """ SELECT count(*) as count 
                  FROM analyze_predict_1 
                  WHERE  {cond}
              """.format(cond = self.sql_common_cond)
        res =  self.query_fetch_one(sql)
        return res['count']

    #end

    """ 開封予測 """
    def get_open_predict_count(self) :
        sql = """ SELECT count(*) as count 
                  FROM analyze_predict_1 
                  WHERE  {cond} AND predict_label = 1
              """.format(cond = self.sql_common_cond)
        res =  self.query_fetch_one(sql)
        return res['count']

    #end

    """ 開封予測 で結果とマッチ"""
    def get_open_match_count(self) :
        sql = """ SELECT count(*) as count 
                  FROM analyze_predict_1 
                  WHERE  {cond} 
                      AND predict_label = 1 
                      AND result_match = 1
              """.format(cond = self.sql_common_cond)
        res =  self.query_fetch_one(sql)
        return res['count']

    #end


    """ 未開封予測 """
    def get_not_open_predict_count(self) :
        sql = """ SELECT count(*) as count 
                  FROM analyze_predict_1 
                  WHERE  {cond} 
                      AND predict_label = 0
              """.format(cond = self.sql_common_cond)

        res =  self.query_fetch_one(sql)
        return res['count']

    #end


    """ 未開封予測で結果とマッチ """
    def get_not_open_match_count(self) :
        sql = """ SELECT count(*) as count 
                  FROM analyze_predict_1 
                  WHERE  {cond} 
                      AND predict_label = 0
                      AND result_match = 1
              """.format(cond = self.sql_common_cond)

        res =  self.query_fetch_one(sql)
        return res['count']

    #end

    """ 結果の保存 """
    def save(self, data):
        sql = """
            REPLACE  INTO analyze_match_1
            VALUES
            (
              %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
                
        """
        param = [
            data['entry_id'],
            data['a_type'],
            data['seido'],
            data['target_count'],
            data['open_predict_count'],
            data['open_match_count'],
            data['open_match_rate'],
            data['not_open_predict_count'],
            data['not_open_match_count'],
            data['not_open_match_rate'],
        ]

        cur = self.db.cursor()  #カーソル宣言
        res = cur.execute(sql, param)  #実行
        self.db.commit()
        pp(res)

    """ util  """
    def query_fetch_one(self, sql, param=[]):
        cur = self.db.cursor()  #カーソル宣言
        cur.execute(sql, param)  #実行
        row = cur.fetchone() 
        return row
    #def

#class    

obj = LogiViewSum()
obj.main()

