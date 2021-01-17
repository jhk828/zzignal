import pandas as pd
import urllib.request
import requests, json
from bs4 import BeautifulSoup
import re


def gettrainlist(sido):
    url = 'http://www.worktogether.or.kr/eduInfo/trainInfo/eduTrainInfoList.do'
    response = requests.get(url)
    bs = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')
    target = bs.select('.board_list')[0]
    trlist = target.findAll(lambda tag: tag.name == 'tr')

    jobdf = pd.DataFrame({'훈련명': [], '등록기관': []})
    for i in range(1, len(trlist)):
        ex = trlist[i]
        title = ex.findAll(lambda tag: tag.name == 'a')[0].text
        title = re.sub('\n|\t|\r|\xa0', '', title).strip()
        title = re.sub('<', '[', title)
        title = re.sub('>', ']', title)
        add = title.split('[')[1].split(']')[0]
        where = ex.findAll(lambda tag: tag.name.startswith('td'))[3].text
        location = where.split(' ')[0]
        if where.endswith('..'):
            location = location + ' ' + add
        #         print(location)
        if sido in location:
            templist = [title, location]
            jobdf = jobdf.append(pd.Series(templist, index=jobdf.columns), ignore_index=True)
    return jobdf


################# 훈련정보


# post 형식 가져오는 함수
def getPostForm(sido):
    data = {
        'joReqstNo': '',
        'mberSn': '',
        're': '1',
        'joKndCmmnCodeSe': 'C',
        'regdateOrder': 'A',
        'searchFlag': '',
        'chUseZe': 'D',
        'sido': sido,
        'workPararBassAdresCn': '',
        'pageSize': '20',
        'pageIndex': '1'
    }

    url = 'https://jobable.seoul.go.kr/jobable/job_offer_info/JobOfferInfo.do?method=selectJobOfferInfoList1'

    response = requests.post(url, data=data)
    #     res_data = response.json()

    return response

def getjoblist(sido):
    response = getPostForm(sido)

    bs = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')
    target = bs.select('.table_wrap')[0]
    trlist = target.findAll(lambda tag: tag.name=='tr')

    jobdf = pd.DataFrame({'기업명':[], '구인제목':[], '급여':[], '희망경력':[], '근무지역':[], '등록일':[], '마감일':[]})
    for i in range(1, len(trlist)):
        tdlist = trlist[i].findAll(lambda tag: tag.name.startswith('td'))
        templist = []
        for td in tdlist:
            txt = re.sub('\n|\t|\r', '', td.text).strip()
            templist.append(txt)
        jobdf = jobdf.append(pd.Series(templist, index=jobdf.columns), ignore_index=True)

    return jobdf
### 일자리정보
