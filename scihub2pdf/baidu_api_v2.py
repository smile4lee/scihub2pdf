# -*- coding:utf-8 -*-
import json
import time

import pandas as pd
import requests
import traceback
import glob
import os

# change these parameters if needed
# provide your own access_token and url here
# access_token = ""
access_token = ""
base_url = "https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify"
charset = "UTF-8"

# input and output dir path, must exist on disk
in_dir_path = 'D:\\tmp\\dir'
out_dir_path = 'D:\\tmp\\dir-out'


# sleep time between two invocations, unit: second
# change it if needed
sleep = 0.5


class BaiduExamples(object):
    def __init__(self):
        self.charset = charset
        self.access_token = access_token

        # build url
        self.build_url(base_url)

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
        self.word_analysis_url = base_url + "?charset=" + self.charset + "&access_token=" + self.access_token

    # do analysis
    # default: retry 3 times if failed, with interval of 3 seconds
    def word_analysis(self, text, retries=3, interval=3):
        datas = json.dumps({
            "text": text
        })

        code = -1
        current = 0
        res = None
        while (code != 200 and current < retries):
            res = requests.post(self.word_analysis_url, data=datas)
            code = res.status_code
            current += 1
            if code != 200:
                print("error, status_code is not 200, retries: %s/%s, interval: %s" % (current, retries, interval))
                time.sleep(interval)

        if code != 200:
            print("error, status_code is not 200, something wrong with the post method, "
                  "res.status_code: %s, res.text: %s, res.content: %s" % (res.status_code, res.text, res.content))
            request = res.request
            print("error, request.url: %s" % request.url)

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
def read_excel(in_filepath, out_dir):
    # pd.set_option('display.float_format', lambda x: '%.2f' % x)
    df = pd.read_excel(in_filepath)
    df_li = df.values.tolist()
    # rows and columns
    row_count = len(df_li)
    column_count = len(df_li[0])
    print("row_count: %s, column_count: %s" % (row_count, column_count))

    # build analysis_url
    be = BaiduExamples()
    be.build_url(base_url)

    for x in range(row_count):
        # store_id and text in column No.0 and column No.1, respectively
        store_id = df_li[x][0]
        text = df_li[x][1].strip()
        current = x + 1
        print("%s/%s, store_id: %s" % (current, row_count, store_id))
        # do analysis
        res_text = None
        try:
            res_text = be.word_analysis(text)
            # append results into lists
            be.append_list(store_id, res_text)
        except Exception as e:
            print("error, %s/%s, store_id: %s, text: %s, res_text: %s" % (current, row_count, store_id, text, res_text))
            traceback.print_exc()
        # sleep seconds to wait for next api invocation
        time.sleep(sleep)

    # build pandas dataframe from all results lists
    be.build_dataframe()

    # save to xlsx and csv file
    out_path = out_dir_path + "\\" + get_filename_without_extension(in_filepath) + "-result.xlsx"
    out_path_csv = out_dir_path + "\\" + get_filename_without_extension(in_filepath) + "-result.csv"
    be.save_df_to_excel(out_path)
    be.save_df_to_csv(out_path_csv)


def list_files(dir, extension='\\*.xlsx'):
    files = glob.glob(dir + extension)
    return files


def get_filename_without_extension(path):
    basename = os.path.basename(path)
    return os.path.splitext(basename)[0]


if __name__ == "__main__":
    # read_excel(in_path)
    files = list_files(in_dir_path)
    total = len(files)
    current = 0
    for f in files:
        current += 1
        print("%s/%s, file: %s" % (current, total, f))
        read_excel(f, out_dir_path)
