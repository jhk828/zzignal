import feedparser



urls = (#뉴스 고르시면 됩니다 필요한거

    "http://fs.jtbc.joins.com/RSS/newsflash.xml",               #속보	
    'http://fs.jtbc.joins.com/RSS/politics.xml',              #정치
    'http://fs.jtbc.joins.com/RSS/economy.xml',               #경제
    'http://fs.jtbc.joins.com/RSS/society.xml',               #사회
    'http://fs.jtbc.joins.com/RSS/international.xml',          #국제
    'http://fs.jtbc.joins.com/RSS/culture.xml',               #문화
    # 'http://fs.jtbc.joins.com/RSS/entertainment.xml',         #연예	
    # 'http://fs.jtbc.joins.com/RSS/sports.xml',                #스포츠	
    # 'http://fs.jtbc.joins.com/RSS/fullvideo.xml',             #풀영상	
    # 'http://fs.jtbc.joins.com/RSS/newsrank.xml',              #뉴스랭킹	
    # 'http://fs.jtbc.joins.com/RSS/newsroom.xml',              #뉴스룸	
    # 'http://fs.jtbc.joins.com/RSS/morningand.xml',            #아침뉴스
    # 'http://fs.jtbc.joins.com/RSS/newson.xml',                #뉴스ON	
    # 'http://fs.jtbc.joins.com/RSS/politicaldesk.xml',         #정치부회의
    None,	

)



def crawl_rss (url) :
    if url == None:
        return None
    else:
        rss_dic = []

        print(rss_dic,"parsing...")
        parse_rss = feedparser.parse(url)

        for p in parse_rss.entries :
            rss_dic.append({'title':p.title, 'link':p.link})

        print(url,"parsing complete")
        print(rss_dic[0])
        return rss_dic
    


if __name__ == "__main__" :

    for url in urls:

        crawl_rss(url)