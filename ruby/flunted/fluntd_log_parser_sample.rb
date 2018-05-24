# 
# fluentd td-agentのログパーサ
#

require 'fluent/parser'
module Fluent
  class TextParser
    #パーサープラグインの名前
    class MtLogParser < Parser
      # このプラグインをパーサプラグインとして登録する confではこの名前を取得
      Plugin.register_parser('mylog', self)

      def initialize
        super

      end

      def configure(conf={})
        super
        # 設定ファイルによるものはここで
      end

      def parse(text)
        #apache log format
        # "%{%Y-%m-%d_%H:%M:%S}t\t%h\t%U\t%q"
        # 1.\tでパース

        arr_tsv = text.split("\t")

        output = {}
        output['atime'] = arr_tsv[0]
        output['host']  = arr_tsv[1]
        output['path']  = arr_tsv[2]
        output['query'] = arr_tsv[3]
        output['ua']    = arr_tsv[4]

        # query &date=111&data=....&data2...をスプリット
        query = arr_tsv[3]
        arr_query2 = {}
        if query  then
          query.slice!(0) #先頭?削除

          arr_query = query.split('|')
          arr_query.each do |row|
             arr_row = row.split('=', 2) #全体を2個に分割する。最初の一つで分割。
             key = arr_row[0]
             val = arr_row[1]
             arr_query2[key]  = val
          end
        end

        #target_key query中のこのデータだけ取得する
        require 'uri'
        target_key = ['ltime', 'lurl', 'lref', 'ltype', 'lval1', 'lval2','ltitle','mlid', 'sf_id', 'pre_url', 'pre_title' ]
        target_key.each do |row|

            #keyが無い場合はnil
            #if( row == 'ltitle' && arr_query2.key?('ltitle')) then
            #    output[row] = URI.unescape(arr_query2[row])
            #else
            #    output[row] = arr_query2[row]
            #end
            if(arr_query2.key?(row) && !arr_query2[row].nil?) then
                arr_query2[row] = URI.unescape(arr_query2[row]); #全部エスケープかける
            end
            output[row] = arr_query2[row]
        end

        yield Engine.now, output
      end

    end
  end
end


