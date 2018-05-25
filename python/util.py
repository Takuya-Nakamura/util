#ファイル:全て小文字の短い名前
#クラス:パスカルケース
#メソッド、関数、変数:スネークケース
#定数:大文字のアンスコ区切り
#
# コメント
# 複数行は """ コメント """ ''' コメント '''
#
#
#
#



import MySQLdb as my
import MySQLdb.cursors
from  pprint import pprint  as pp
from  datetime import datetime

class Util:

    """ db関連 """
    # db接続の取得
    def db_connect(self):
        con = my.connect(
            user='',
            passwd='',
            host='',
            db='',
            charset="utf8",
            cursorclass=my.cursors.DictCursor
        )
        return con
    #end db_connect


    """ log関連 """
    # メッセージに現在時刻を付けて出力
    def log(self, msg)
        now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        pp("%s %s" %(now, msg))

  

    ## python  
