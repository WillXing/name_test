# -- coding: UTF-8 -- 
import MySQLdb as mdb
import scrapy
import time
from scrapy.shell import inspect_response


class NameTest(scrapy.Spider):
  name="test_name"
  DB_NAME = "spider"
  test_name = {'qm': 'zhqm', 
                'xs': '黄刘',
                'xm': '若源',
                'xb': '1',
                'nn': '2017',
                'ny': '6',
                'nr': '9',
                'ns': '9',
                'nf': '32',
                'gn': '0',
                'nx': '公历',
                'cs': '',
                'harea': '510108',
                'zty': '1'}
  word_list = []

  first_word_index = 0
  second_word_index = 0

  def start_requests(self):
    self.conn = mdb.connect("localhost", "root", "")
    self.conn.select_db(self.DB_NAME)
    cursor = self.conn.cursor()
    cursor.execute("truncate table name_test")
    cursor.execute("select a.word as total from (select substr(name, 4, 1) as word, count(*) as sum from name group by word union select substr(name, 3, 1) as word, count(*) as sum from name group by word) as a group by a.word")
    self.word_list = cursor.fetchall()
    cursor.close()

    self.test_name["xm"] = self.word_list[self.first_word_index][0] + self.word_list[self.second_word_index][0]

    return [scrapy.FormRequest("https://qiming.yw11.com/newqiming/qm/cm/", 
      formdata=self.test_name,
      callback=self.check_score)]
  def check_score(self, response):
    # inspect_response(response, self)
    name = self.test_name["xm"]
    total = response.css(".namet1 tr:nth-child(2) td:nth-child(1) .num::text").extract()[0]
    yin = response.css(".namet1 tr:nth-child(2) td:nth-child(2) .co1::text").extract()[0]
    bazi = response.css(".namet1 tr:nth-child(3) td .co1.bd::text").extract()[0]
    shenxiao = response.css(".namet1 tr:nth-child(4) td .co1.bd::text").extract()[0]
    wuge = response.css(".namet1 tr:nth-child(5) td .co1.bd::text").extract()[0]
    zhouyi = response.css(".namet1 tr:nth-child(6) td .co1.bd::text").extract()[0]

    # print self.test_name["xm"]
    # inspect_response(response, self)

    self.conn.select_db(self.DB_NAME)
    cursor = self.conn.cursor()
    cursor.execute("INSERT INTO name_test values(%s,%s,%s,%s,%s,%s,%s)", (name.decode("utf-8"), total, yin, bazi, shenxiao, wuge, zhouyi))
    cursor.close()

    self.second_word_index = self.second_word_index + 1

    if self.second_word_index >= len(self.word_list):
      self.first_word_index = self.first_word_index + 1
      self.second_word_index = 0

    if self.first_word_index >= len(self.word_list):
      return

    self.conn.commit()
    time.sleep(10)
    self.test_name["xm"] = self.word_list[self.first_word_index][0] + self.word_list[self.second_word_index][0]
    yield scrapy.FormRequest("https://qiming.yw11.com/newqiming/qm/cm/", 
      formdata=self.test_name,
      callback=self.check_score)