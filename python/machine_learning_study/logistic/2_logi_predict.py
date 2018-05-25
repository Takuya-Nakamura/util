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
import json

class LogiPredict:
    """ ロジスティック回帰 ユーザー毎、記事毎に開封予測データを作成 """

    def __init__(self):
        #db接続の取得
        app = App.AppClass()
        self.db = app.db_con()


    def main(self, a_type):

        pp ("start")
        self.a_type = a_type
        pp(self.a_type)

        if 'shinryoka' in a_type :
            self.flag_table = 'page_shinryoka_hz'      
        elif 'all' in a_type :
            self.flag_table = 'page_all_tag_hz'

        elif 'cat' in a_type :
            self.flag_table = 'page_cat_hz'

        elif 'shikkan' in a_type :
            self.flag_table = 'page_shikkan_hz'

        elif 'sonota' in a_type :
            self.flag_table = 'page_sonota_hz'
        else :
            pp('a_type error')
            exit()

        # main 
        pp(self.flag_table) 
     
        user_list = self.get_user_list();
        if len(user_list ) == 0 :
            pp('error : this a_type has no user')
            exit()
 
        #page_list = self.get_page_list();
        #page_list manu
        page_list = [
            {'entry_id' : '509696'},
            {'entry_id' : '510065'},
            {'entry_id' : '509871'},
            {'entry_id' : '509767'},
            {'entry_id' : '508862'},
        ]

        for p in page_list :
            pp(p)

            for u in user_list :
                self.run_predict(u['member'], p['entry_id'] )


        pp("end")

    #end main

    def run_predict(self, id, entry_id):


        #ユーザー毎モデルを取得
        analyze_result = self.get_analyze_result(id, self.a_type) 

        if analyze_result is None :
            return 0

        if len(analyze_result) == 0 :
            return 0

        if analyze_result['model'] == "" :
            return 0

        model_dict = self.convert_model_json_dict(analyze_result['model'])
        if len(model_dict) == 0 :
            return 0

        seido = analyze_result['seido'] 


        #対象ページの 診療科情報を取得する
        #entry_id = "509696"
        page_shinryoka_flag = self.get_page_flag(entry_id)
        if len(page_shinryoka_flag) == 0:
            return 0

        predict_val = self.predict_val(model_dict, page_shinryoka_flag)
        if predict_val > 0.5 :
            predict_label = 1
        else :
            predict_label = 0

        self.save_result(id, entry_id, self.a_type, seido,  predict_val, predict_label) 


    #end main


    def predict_val(self, model_dict, page_shinryoka_flag) :
        """ 予測値の計算 """
        """ 0.5以上の場合は開封と予測 """

        ret_val = 0
        for key, val in model_dict.items() :
            ret_val += float(val) + float(page_shinryoka_flag[key])

        return ret_val
    #end predict_open_val



    def convert_model_json_dict(self, model_json):
        dict_tmp = json.loads(model_json)
        arr_ret = {}
        for(item, val) in zip(dict_tmp['0'].values(), dict_tmp['1'].values()):
           arr_ret.update({item : val})
        return arr_ret
    #end convert_model_json_dict


          
    def get_analyze_result(self, id, a_type) :
        """ shinryoka_logisticでの分析結果を取得 """
        sql = "SELECT * FROM analyze_result_1 WHERE id = %s AND type = %s limit 1"
     
        cur= self.db.cursor()  #カーソル宣言
        cur.execute(sql, [id, a_type])  #実行
        rows = cur.fetchone() #全部フェッチ
        return rows


    def get_page_flag(self, entry_id) :
        """ ページのフラグを取得する """
        sql = """
            SELECT * FROM {flag_table} where entry_id = %s limit 1 
        """.format(flag_table=self.flag_table)
     
        cur= self.db.cursor()  #カーソル宣言
        cur.execute(sql, [entry_id])  #実行
        rows = cur.fetchone() #全部フェッチ
        return rows
 
    #end get_page_shinryoka 


    def save_result(self, id, entry_id, a_type, seido, predict_val, predict_label ) :
        """ 1件づつデータを保存 """
        sql = """INSERT IGNORE INTO analyze_predict_1 
                 (id, entry_id, a_type, seido, predict_val, predict_label)
                 VALUES
                 (%s, %s, %s, %s, %s, %s )
              """
        
        cur= self.db.cursor()  #カーソル宣言
        res = cur.execute(sql, [id, entry_id, a_type, seido, predict_val, predict_label])  #実行
        self.db.commit() #commit必須..?
    #end save_result





    """ list  """
    def get_user_list(self) :
        """ 対象ユーザーリストの取得 """
        # seido = 1は除外 (過学習)
        #sample user tableから
        #sql = "SELECT member FROM analyze_sample_users "

        sql = """ 
                 SELECT id as member 
                 FROM analyze_result_1
                 WHERE type = '{a_type}'
                 AND  0.8 < seido  AND seido < 1
              """.format(a_type = self.a_type)

        cur= self.db.cursor()  #カーソル宣言
        cur.execute(sql)  #実行
        rows = cur.fetchall() #全部フェッチ
        return rows
        
    #end get_user_list

 

    def get_page_list(self) :
        """ 対象ユーザーリストの取得 """
        #sample user tableから
        #sql = "SELECT member FROM analyze_sample_users "
        sql = """ SELECT entry_id from pages 
                  ORDER BY entry_id desc
              """
 
        cur= self.db.cursor()  #カーソル宣言
        cur.execute(sql)  #実行
        rows = cur.fetchall() #全部フェッチ
        return rows
        
    #end get_user_list
#class    


args = sys.argv
if  len(args) == 1:
   pp("missing argument error")
   sys.exit()

a_type = args[1]
obj = LogiPredict()
obj.main(a_type)

