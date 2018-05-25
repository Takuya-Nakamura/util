# coding:utf-8
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.cluster import MiniBatchKMeans
from pprint import pprint 
#ward
from scipy.cluster.hierarchy import dendrogram,ward,leaves_list
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.pyplot import show
from Tkinter import *


class ClusterWard:

    max_df = 0.5
    max_features=3000
    num_clusters = 10

    def main(self):
        #print "main start"
        self.make_cluster()

    def make_cluster(self):

        # 処理対象の文字列によるリストを生成する
        texts = self._read_from_file()
        #print("texts are %(texts)s" %locals() )

        # TF-IDF ベクトルを生成する
        vectorizer = TfidfVectorizer(
            max_df=self.max_df,
            max_features=self.max_features,
            stop_words='english'
            #stop_words='japanese'
            )


        arr_texts = texts.split("\n")
        X = vectorizer.fit_transform(arr_texts)  #error
        #print("X values are %(X)s" %locals() )

        #クラスタリングパターン2 k-means
        #http://ailaby.com/tfidf/
        #clusters = KMeans(n_clusters=4, random_state=0).fit_predict(X)
        #for doc, cls in zip(arr_texts, clusters):
        #    print '%s,%s' %(cls, doc)

        # ward 
        # http://esu-ko.hatenablog.com/entry/2016/03/09/%E3%83%87%E3%83%BC%E3%82%BF%E3%82%B5%E3%82%A4%E3%82%A8%E3%83%B3%E3%82%B9%E3%82%92Python%E3%81%A7%E8%A9%A6%E3%81%99%283_%E3%82%AF%E3%83%A9%E3%82%B9%E3%82%BF%E3%83%AA%E3%83%B3%E3%82%B0%29
        # https://openbook4.me/users/1/sections/783
        a = [[1,1],[2,2],[3,2],[3,6]] 

        h_cls = ward(a)
        d = dendrogram(h_cls)
        pprint(d)
        show()       


    def _read_from_file(self):
        f = open("./sample.data");
        data = f.read()
        return data        

# start
obj = ClusterWard()
obj.main()

