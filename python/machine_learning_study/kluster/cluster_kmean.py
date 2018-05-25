# coding:utf-8
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.cluster import MiniBatchKMeans
from pprint import pprint 

class ClusteKmean:

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

        # KMeans インスタンスを生成しクラスタリングする
        # パラメータはデータの量や特性に応じて適切なものを与えるようにする
  
        """ http://qiita.com/ynakayama/items/8bc9f3c7639f7251858a
        km = MiniBatchKMeans(
            n_clusters=self.num_clusters,
            init='k-means++', batch_size=1000,
            n_init=10, max_no_improvement=10,
            verbose=True
            )
        km.fit(X)
        labels = km.labels_
 
        # 属するクラスタとその距離を計算する
        transformed = km.transform(X)
        dists = np.zeros(labels.shape)
        for i in range(len(labels)):
            dists[i] = transformed[i, labels[i]]

        clusters = []
        for i in range(self.num_clusters):
            cluster = []
            ii = np.where(labels==i)[0]
            dd = dists[ii]
            di = np.vstack([dd,ii]).transpose().tolist()
            di.sort()
            for d, j in di:
                cluster.append(texts[int(j)])
            clusters.append(cluster)

        # 生成したクラスタを返す
        for doc, cls in zip(arr_texts, clusters):
            print cls, doc
        """   
        #クラスタリングパターン2 k-means
        #http://ailaby.com/tfidf/

        clusters = KMeans(n_clusters=4, random_state=0).fit_predict(X)
        for doc, cls in zip(arr_texts, clusters):
            print '%s,%s' %(cls, doc)


    def _read_from_file(self):
        f = open("./sample.data");
        data = f.read()
        return data        

# start
obj = ClusterKmean()
obj.main()

