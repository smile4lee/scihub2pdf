# -*- coding:utf-8 -*-
import json
import time

import pandas as pd
import requests

# change these parameters if needed
access_token = "24.0f5824ebe6b53c8d75dc35aafc93aa7f.2592000.1599356676.282335-21649372"
word_analysis_url = "https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify?charset=UTF-8&access_token=24.0f5824ebe6b53c8d75dc35aafc93aa7f.2592000.1599356676.282335-21649372"

# input path
in_path = 'C:\\Users\\lihaijun\\Desktop\\tmp\\anli.xlsx'

# output filepath: xlsx and csv
out_path = 'C:\\Users\\lihaijun\\Desktop\\tmp\\anli_result.xlsx'
out_path_csv = 'C:\\Users\\lihaijun\\Desktop\\tmp\\anli_result.csv'

# sleep time between two invocations, unit: second
sleep = 3


class BaiduExamples(object):
    def __init__(self):
        self.charset = "UTF-8"
        self.access_token = "24.0f5824ebe6b53c8d75dc35aafc93aa7f.2592000.1599356676.282335-21649372"
        self.word_analysis_url = "https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify?charset=UTF-8&access_token=24.0f5824ebe6b53c8d75dc35aafc93aa7f.2592000.1599356676.282335-21649372"
        self.store_id_list = []
        self.log_id_list = []
        self.text_list = []
        self.pos_prob_list = []
        self.confi_list = []
        self.neg_prob_list = []
        self.senti_list = []
        self.df = None

    # build post request url with parameters
    def build_url(self, base_url):
        return base_url + "?charset=" + self.charset + "&access_token=" + self.access_token

    # do analysis
    def word_analysis(self, text):
        self.word_analysis_url = self.build_url(self.word_analysis_url)
        datas = json.dumps({
            "text": text
        })
        res = requests.post(self.word_analysis_url, data=datas)

        res_str = res.content.decode()
        return res_str

    # append those results parsed into lists
    def append_list(self, store_id, res_text):
        # parse json response
        data = json.loads(res_text)

        # parse parameters in json
        log_id = data['log_id']
        text = data['text']
        pos_prob = data['items'][0]['positive_prob']
        confi = data['items'][0]['confidence']
        neg_prob = data['items'][0]['negative_prob']
        senti = data['items'][0]['sentiment']

        # print("store_id: %s" % store_id)
        # print("text: %s" % text)
        # print("log_id: %s" % log_id)
        # print("pos_prob: %s" % pos_prob)
        # print("confi: %s" % confi)
        # print("neg_prob: %s" % neg_prob)
        # print("senti: %s" % senti)
        # print("--------------------------")

        # append into lists
        self.store_id_list.append(store_id)
        self.log_id_list.append(log_id)
        self.text_list.append(text)
        self.pos_prob_list.append(pos_prob)
        self.confi_list.append(confi)
        self.neg_prob_list.append(neg_prob)
        self.senti_list.append(senti)

    # build pandas dataframe from lists
    def build_dataframe(self):
        self.df = pd.DataFrame(
            {'store_id': self.store_id_list,
             'log_id': self.log_id_list,
             'text': self.text_list,
             'pos_prob': self.pos_prob_list,
             'confi': self.confi_list,
             'neg_prob': self.neg_prob_list,
             'senti': self.senti_list
             })

    def save_df_to_excel(self, out_path):
        self.df.to_excel(out_path, sheet_name='result')

    def save_df_to_csv(self, out_path, sep=','):
        self.df.to_csv(out_path, sep=',', encoding='utf-8')


# read input xlsx file
def read_excel(path):
    # pd.set_option('display.float_format', lambda x: '%.2f' % x)
    df = pd.read_excel(path)
    df_li = df.values.tolist()
    # rows and columns
    row_count = len(df_li)
    column_count = len(df_li[0])
    print("row_count: %s, column_count: %s" % (row_count, column_count))

    be = BaiduExamples()
    for x in range(row_count):
        # store_id and text in column No.0 and column No.1, respectively
        store_id = df_li[x][0]
        text = df_li[x][1]
        print("%s/%s, store_id: %s" % (x + 1, row_count, store_id))
        # do analysis
        res_text = be.word_analysis(text.strip())
        # append results into lists
        be.append_list(store_id, res_text)
        # sleep seconds to wait for next api invocation
        time.sleep(sleep)

    # build pandas dataframe from all results lists
    be.build_dataframe()

    # save to xlsx and csv file
    be.save_df_to_excel(out_path)
    be.save_df_to_csv(out_path_csv)


if __name__ == "__main__":
    read_excel(in_path)
