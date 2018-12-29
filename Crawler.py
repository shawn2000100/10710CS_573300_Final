# -*- coding: UTF-8 -*-
import json
import requests
import time
from bs4 import BeautifulSoup
from bs4.element import NavigableString


class PttCrawler:
    root = "https://www.ptt.cc/bbs/" # ptt 根目錄，看板爬蟲時用到
    main = "https://www.ptt.cc"      # 搭配代碼，可存取某一篇特定文章
    gossip_data = {
        "from": "bbs/Gossiping/index.html",
        "yes": "yes"
    }
    def __init__(self):
        self.session = requests.session()
        requests.packages.urllib3.disable_warnings()
        self.session.post("https://www.ptt.cc/ask/over18",
                          verify=False,
                          data=self.gossip_data)

    def articles(self, page):
    # 文章內容的生成器
    # page 代表頁面網址 (從某一頁點進去後的網址)
    # 要爬文章及推文內容須從 page 網址來爬
        res = self.session.get(page, verify=False)
        soup = BeautifulSoup(res.text, "lxml")

        for article in soup.select(".r-ent"):
            try:
                yield self.main + article.select(".title")[0].select("a")[0].get("href")
            except:
                pass  # (本文已被刪除)

    def pages(self, board, index_range):
        # 頁面網址的生成器
        # 這邊是為了一頁一頁的爬某版的全部文章
        # board: 看板名稱
        # index_range: 文章頁數範圍
         target_page = self.root + board + "/index"
         if range is None:
            yield target_page + ".html"
         else:
            for index in index_range:
                yield target_page + str(index) + ".html"

    def parse_article(self, url, mode):
        # 解析爬取的文章 (從頁面點進去後的特定文章網址)
        # url: 欲爬取的PTT頁面網址
        # mode: 欲爬取的推文模式，通常全部都爬。 全部(all)、推文(up)、噓文(down)、純回文(normal)
        # Returns: article (爬取文章後資料的dict)

        # 處理mode標誌
        if mode == 'all':
            mode = 'all'
        elif mode == 'up':
            mode = u'推'
        elif mode == 'down':
            mode = u'噓'
        elif mode == 'normal':
            mode = '→'
        else:
            raise ValueError("mode變數錯誤", mode)

        raw = self.session.get(url, verify=False)
        soup = BeautifulSoup(raw.text, "lxml")
        try:
            # 取得文章作者, 標題, 日期... 這邊需自行檢查文章原始碼來決定怎麼寫爬蟲語法
            article = {}
            article["Author"] = soup.select(".article-meta-value")[0].contents[0].split(" ")[0]
            article["Title"] = soup.select(".article-meta-value")[2].contents[0]
            article["Date"] = soup.select(".article-meta-value")[3].contents[0]
            # 取得內文，目前還沒辦法爬取文章中的圖片網址
            content = ""
            for tag in soup.select("#main-content")[0]:
                if type(tag) is NavigableString and tag != '\n':
                    content += tag
                    break # 出於某些不明原因，這邊要Break... Contents才不會出現奇怪的字串
            article["Content"] = content
            article["Link"] = url # 為了之後回傳dict，以便輸出JSON檔的時候能夠順便記下文章網址 (不然爬出來的內文格式太亂了...)

            # 這邊開始處理下面的回文，紀錄推文數據，最後會Output在JSON檔最後面
            upvote = 0
            downvote = 0
            novote = 0
            response_list = []
            for response_struct in soup.select(".push"):
                # 跳脫「檔案過大！部分文章無法顯示」的 push class
                if "warning-box" not in response_struct['class']:
                    response_dic = {}
                    # 根據不同的mode去採集response
                    if mode == 'all':
                        response_dic["Vote"] = response_struct.select(".push-tag")[0].contents[0][0]
                        response_dic["User"] = response_struct.select(".push-userid")[0].contents[0]
                        response_dic["Content"] = response_struct.select(".push-content")[0].contents[0][1:]
                        response_list.append(response_dic)

                        if response_dic["Vote"] == "推":
                            upvote += 1
                        elif response_dic["Vote"] == "噓":
                            downvote += 1
                        else:
                            novote += 1
                    else:
                        response_dic["Vote"] = response_struct.select(".push-tag")[0].contents[0][0]
                        response_dic["User"] = response_struct.select(".push-userid")[0].contents[0]
                        response_dic["Content"] = response_struct.select(".push-content")[0].contents[0][1:]

                        if response_dic["Vote"] == mode:
                            response_list.append(response_dic)
                            if mode == "推":
                                upvote += 1
                            elif mode == "噓":
                                downvote += 1
                            else:
                                novote += 1

            article["Responses"] = response_list
            article["UpVote"] = upvote
            article["DownVote"] = downvote
            article["NoVote"] = novote
        except Exception as e:
            print(e)
            print(u"在分析 %s 時出現錯誤" % url)

        return article

    def output(self, filename, data):
    #爬取完的資料寫到json文件
    #Args:
        #filename: json檔的文件路徑
        #data: 爬取完的資料
        try:
            with open(filename + ".json", 'wb+') as op:
                op.write(json.dumps(data, indent=4, ensure_ascii=False).encode('utf-8'))
                print('爬取完成~', filename + '.json', '輸出成功！')
        except Exception as err:
            print(filename + '.json', '輸出失敗 :(')
            print('error message:', err)

    def crawl(self, board, mode, start, end):
        sleep_time = 0.01
        # 爬取資料主要接口
        # board: 欲爬取的看版名稱
        # mode: 欲爬取回文的模式。全部(all)、推文(up)、噓文(down)、純回文(normal)
        # start: 從哪一頁開始爬取
        # end: 爬取到哪一頁停止
        # sleep_time: sleep間隔時間
        crawl_range = range(start, end+1)
        for page in self.pages(board, crawl_range):
            res = []
            for article in self.articles(page):
                res.append(self.parse_article(article, mode))
                time.sleep(sleep_time)

            print("已經完成 %s 頁面第 %d 頁的爬取" % (board, start))
            self.output(board + str(start), res)
            start += 1


if __name__ == '__main__':
    main()