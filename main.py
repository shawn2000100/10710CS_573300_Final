# -*- coding: UTF-8 -*-
from sys import argv
from Crawler import PttCrawler

# 原作者提共的，命令列模式開啟方式。 可自行參考修改
# def main():
#     crawler = PttCrawler()
#     mode = 'all' # 爬所有類型推文
#
#     if len(argv) == 3:
#         mode = argv[2]
#         result = crawler.parse_article(argv[1], mode)
#         crawler.output("result", result)
#     elif len(argv) == 5:
#         mode = argv[4]
#         crawler.crawl(board=argv[1], start=int(argv[2]), end=int(argv[3]), mode=argv[4])
#     else:
#         print("使用方式有兩種：")
#         print("1) python %s 欲爬取的url" % argv[0])
#         print("2) python %s 欲爬取的版面 從哪一頁開始爬 爬到哪一頁為止" % argv[0])

def main():
    crawler = PttCrawler()
    # 八卦版主頁面網址 https://www.ptt.cc/bbs/Gossiping/index.html
    # 進入看板主頁後，可以按上一頁，看一下目前 index(頁數) 然後決定爬蟲範圍。
    crawler.crawl(board="Gossiping", mode='all', start=39535, end=39540)

if __name__=="__main__":
    main()