import math
from sys import stdout
import logging
from flask import Flask, render_template, jsonify,redirect
import requests
from flask_socketio import SocketIO, emit
import cv2, base64
import numpy as np
import mediapipe as mp
import datetime
import feedparser
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import configparser
import json
import sys
import os.path
import os
import flask
from auth2 import auth
from predict import *
import paho.mqtt.client as mqtt
from models import db
from models import Fcuser
from flask_wtf.csrf import CSRFProtect
from forms import RegisterForm, LoginForm
from flask import session
import potal

frame_num = 50
input_frame_num = 0

CLIENT_SECRETS_FILE = "client_secret.json"

SCOPES = ['https://www.googleapis.com/auth/calendar']
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'

libdir = os.path.dirname(__file__)
sys.path.append(os.path.split(libdir)[0])
apiKey = '솔라피API KEY'
apiSecret = '솔라피API KEY'

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.2, min_tracking_confidence=0.5)

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(stdout))
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True
socketio = SocketIO(app)
app.secret_key = '0000'

prediction_global = 999
prediction_flag = 123124

icon_lookup = {
    'clear-day': "assets/Sun.png",  # clear sky day
    'wind': "assets/Wind.png",   #wind
    'cloudy': "assets/Cloud.png",  # cloudy day
    'partly-cloudy-day': "assets/PartlySunny.png",  # partly cloudy day
    'rain': "assets/Rain.png",  # rain day
    'snow': "assets/Snow.png",  # snow day
    'snow-thin': "assets/Snow.png",  # sleet day
    'fog': "assets/Haze.png",  # fog day
    'clear-night': "assets/Moon.png",  # clear sky night
    'partly-cloudy-night': "assets/PartlyMoon.png",  # scattered clouds night
    'thunderstorm': "assets/Storm.png",  # thunderstorm
    'tornado': "assets/Tornado.png",    # tornado
    'hail': "assets/Hail.png"  # hail
}

def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	#client.subscribe("$SYS/#")
	client.subscribe("hand") #구독 "nodemcu"

def on_message(client, userdata, msg):
	print(msg.topic+" "+str(msg.payload)) #토픽과 메세지를 출력한다.


client = mqtt.Client() #client 오브젝트 생성
client.on_connect = on_connect #콜백설정
client.on_message = on_message #콜백설정

client.connect("ip주소", 1883, 60) #라즈베리파이3 MQTT 브로커에 연결

def get_weather():

    # Get json from dark skys api
    APIKEY = 'Dark Sky API KEY'
    LAT, LON =37.512828, 127.052707
    URL = 'https://api.darksky.net/forecast/{}/{},{}'.format(APIKEY, LAT, LON)
    r = requests.get(URL)
    json = r.json()

    temperatureHigh = json['daily']['data'][0]['temperatureHigh']
    temperatureLow = json['daily']['data'][0]['temperatureLow']
    week_summary = json['daily']['summary']
    # Get current and hourly data
    currently = json['currently']
    hourly = json['hourly']
    # print(hourly['data'])
    # Fetch important information for display
    title = currently['summary']
    icon = icon_lookup[currently['icon']]
    temperature = int(round((currently['temperature']-32)*5/9))
    desc = hourly['summary'].rstrip('.')

    week = {0: "월요일", 1: "화요일", 2: "수요일", 3: "목요일", 4: "금요일", 5: "토요일", 6: "일요일"}

    time = [0,0,0,0,0,0]
    time_hightemp = [0,0,0,0,0,0]
    time_lowtemp = [0,0,0,0,0,0]
    time_icon = [0,0,0,0,0,0]
    for i in range(6):
        time[i] = week[datetime.datetime.fromtimestamp(json['daily']['data'][i+1]['time']).weekday()]
        # time[i]="월요일"
        time_hightemp[i] = int(round((json['daily']['data'][i+1]['temperatureHigh']-32)*5/9))
        time_lowtemp[i] = int(round((json['daily']['data'][i+1]['temperatureLow']-32)*5/9))
        time_icon[i] = json['daily']['data'][i+1]['icon']
    global prediction_global
    prediction_global = 999
    global prediction_flag
    prediction_flag = 1

    return {'title': title, 'icon': icon, 'temperature': temperature, 'desc': desc, 'temperatureHigh': temperatureHigh,
            'temperatureLow': temperatureLow, 'week_summary': week_summary,
            'time0': time[0], 'time0_hightemp': time_hightemp[0], 'time0_lowtemp': time_lowtemp[0], 'time0_icon': time_icon[0],
            'time1': time[1], 'time1_hightemp': time_hightemp[1], 'time1_lowtemp': time_lowtemp[1], 'time1_icon': time_icon[1],
            'time2': time[2], 'time2_hightemp': time_hightemp[2], 'time2_lowtemp': time_lowtemp[2], 'time2_icon': time_icon[2],
            'time3': time[3], 'time3_hightemp': time_hightemp[3], 'time3_lowtemp': time_lowtemp[3], 'time3_icon': time_icon[3],
            'time4': time[4], 'time4_hightemp': time_hightemp[4], 'time4_lowtemp': time_lowtemp[4], 'time4_icon': time_icon[4],
            'time5': time[5], 'time5_hightemp': time_hightemp[5], 'time5_lowtemp': time_lowtemp[5], 'time5_icon': time_icon[5]}


## 라즈베리파이 카메라가 실시간으로 사용자 탐색 후 추적
## 추적을 완료하면 손동작의 좌표를 통해 예측을 시작한다.
@socketio.on('input image', namespace='/test')
def test_message(input):
    global input_frame_num
    flag = False
    camera = cv2.VideoCapture("http://ip주소:port번호/?action=stream")
    #camera = cv2.VideoCapture(0)
    #camera.isOpened()

    success, image = camera.read()
    keypoints = []
    image = cv2.cvtColor(cv2.flip(image, 0), cv2.COLOR_BGR2RGB)
    keypoint = 0
    a = 0

    image.flags.writeable = False
    results = hands.process(image)

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    ########################################
    idx = 0
    if results.multi_hand_landmarks:
        arow = []
        tokey = 0
        # multi_hand_landmarks
        for hand_landmarks in results.multi_hand_landmarks:
            #                 print(hand_landmarks)
            idx += 1
            keypoint += hand_landmarks.landmark[9].x

            for data_point in hand_landmarks.landmark:
                nset = [data_point.x, data_point.y]
                arow += nset
            mp_drawing.draw_landmarks(
                image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        keypoint = keypoint * 100 / idx
        client.publish("hand", keypoint)
        handed = len(results.multi_handedness)
        #             print(results.multi_handedness)
        if handed == 1:
            hd = results.multi_handedness[0].classification[0].label.split('\r')[0]
            if hd == 'Left':
                arow = arow + [0, 0] * 21
            else:
                arow = [0, 0] * 21 + arow

        keypoints += arow
        input_frame_num += 1

        # print(input_frame_num)

        if input_frame_num >= frame_num:
            global prediction_global
            prediction = pred_word(keypoints)
            print('prediction result = ', prediction)
            keypoints = []
            input_frame_num = 0
            print(type(prediction))

            prediction_global = prediction
        # print(prediction_global)

    image = cv2.imencode('.jpg', image)[1].tobytes()
    image = base64.b64encode(image).decode('utf-8')
    image = f"data:image/jpeg;base64,{image}"
    emit('out-image-event', {'image_data': image}, namespace='/test')
    print(input_frame_num)
    #camera.enqueue_input(base64_to_pil_image(input))


@socketio.on('connect', namespace='/test')
def test_connect():
    app.logger.info("client connected")


@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/index2')
def index2():
    return render_template('index2.html')

@app.route("/result", methods=['POST'])
def result():
    global prediction_global
    global prediction_flag
    return jsonify({'result': prediction_global, 'flag': prediction_flag})

@app.route('/start')
def start():
    global prediction_global
    prediction_global = 999
    global prediction_flag
    prediction_flag = 0
    return render_template('start.html')

@app.route('/weather')
def weather():
    return render_template('weather.html')

@app.route("/update_weather", methods=['POST'])
def update_weather():
    currentWeather = get_weather()
    return jsonify({'result' : 'success', 'currentWeather': currentWeather})

@app.route('/news')
def news():
    urls = (
        "http://fs.jtbc.joins.com/RSS/newsflash.xml"  # 속보
    )
    rss_dic = []
    news_dic = []
    parse_rss = feedparser.parse(urls)
    for p in parse_rss.entries:
        rss_dic.append({'title': p.title, 'link': p.link})
    for i in range(5):
        news_dic.append(rss_dic[i])
    global prediction_global
    prediction_global = 999
    global prediction_flag
    prediction_flag = 1

    return render_template('news.html', news=news_dic)

################### 캘린더 시작 ##############################
@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

@app.route('/data')
def return_date():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    calendar_id = 'primary'  # 사용할 캘린더 ID
    today = datetime.date.today().isoformat()
    time_min = today + 'T00:00:00+09:00'  # 일정을 조회할 최소 날짜
    time_max = '2020-12-31' + 'T23:59:59+09:00'  # 일정을 조회할 최대 날짜
    max_results = 30  # 일정을 조회할 최대 개수
    is_single_events = True  # 반복 일정의 여부
    orderby = 'startTime'  # 일정 정렬

    # 오늘 일정 가져오기
    events_result = service.events().list(calendarId = calendar_id,
                                        timeMin = time_min,
                                        timeMax = time_max,
                                        maxResults = max_results,
                                        singleEvents = is_single_events,
                                        orderBy = orderby).execute()
    flask.session['credentials'] = credentials_to_dict(credentials)

    # print(service)
    # print(events_result)
    events_result = events_result['items']
    # events = {}
    events = []
    for i in events_result:
        print(i)
        print(i["summary"], i["updated"][:10])
        events.append({'start': i['start']['date'], 'title': i['summary']})
    print(events)

    # start_date = request.args.get('start', '')
    # end_date = request.args.get('end', '')
    return flask.jsonify(events)


@app.route('/authorize')
def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES
    )

    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    flask.session['state'] = state

    return flask.redirect(authorization_url)


@app.route('/ouath2callback')
def oauth2callback():
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state
    )
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.redirect(flask.url_for('calendar'))


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}
###################### 캘린더 끝 ######################################


def send_message():
    data = {
        'message': {
            'to': '119',  # 119라던가 보낼번호
            'from': '01000000000',  # "인증받은 번호만 됩니다"
            'text': '서울시 xx구 입니다'
                    '위급한 상황이에요 도와주세요'  # 여기에 주소랑 입력하면 될거같습니다
        }
    }
    res = requests.post('https://api.solapi.com/messages/v4/' + 'send', headers=auth.get_headers(apiKey, apiSecret),
                        json=data)

    print(json.dumps(json.loads(res.text), indent=2, ensure_ascii=False))
    print(res)
    return res


@app.route('/report')
def report():
    result = ""
    if(send_message().status_code==200):
    #if result == "":
        result = "신고하였습니다."
    else:
        result = "신고에 실패하였습니다"
    global prediction_global
    prediction_global = 999
    global prediction_flag
    prediction_flag = 1
    return render_template('report.html', x=result)

@app.route('/register', methods=['GET', 'POST'])  # 겟, 포스트 메소드 둘다 사용
def register():  # get 요청 단순히 페이지 표시 post요청 회원가입-등록을 눌렀을때 정보 가져오는것
    form = RegisterForm()
    if form.validate_on_submit():  # POST검사의 유효성검사가 정상적으로 되었는지 확인할 수 있다. 입력 안한것들이 있는지 확인됨.
        # 비밀번호 = 비밀번호 확인 -> EqulaTo

        fcuser = Fcuser()  # models.py에 있는 Fcuser
        fcuser.userid = form.data.get('userid')
        fcuser.username = form.data.get('username')
        fcuser.password = form.data.get('password')
        fcuser.age = form.data.get('age')
        fcuser.gender = form.data.get('gender')
        fcuser.address = form.data.get('address')

        print(fcuser.userid, fcuser.password)  # 회원가입 요청시 콘솔창에 ID만 출력 (확인용, 딱히 필요없음)
        db.session.add(fcuser)  # id, name 변수에 넣은 회원정보 DB에 저장
        db.session.commit()  # 커밋

        return redirect('/')

    return render_template('register.html', form=form)

@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # 로그인 폼 생성
    if form.validate_on_submit():  # 유효성 검사
        session['userid'] = form.data.get('userid')  # form에서 가져온 userid를 session에 저장

        return redirect('/select')  # 로그인에 성공하면 홈화면으로 redirect

    return render_template('login.html', form=form)


@app.route('/select')
def select():
    return render_template('select.html')

@app.route('/logout',methods=['GET'])
def logout():
    session.pop('userid',None)
    return redirect('/')

@app.route('/joblist')
def get_joblist():
    company_name = potal.getjoblist('서울').to_dict('index')
    print(company_name)
    return render_template('joblist.html',company_name=company_name)

@app.route('/trainlist')
def get_trainlist():
    trainlist = potal.gettrainlist('서울').to_dict('index')
    return render_template('trainlist.html',trainlist=trainlist)


if __name__ == '__main__':
    basedir = os.path.abspath(os.path.dirname(__file__))  # db파일을 절대경로로 생성
    dbfile = os.path.join(basedir, 'db.sqlite')  # db파일을 절대경로로 생성

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
    # sqlite를 사용함. (만약 mysql을 사용한다면, id password 등... 더 필요한게많다.)
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    # 사용자 요청의 끝마다 커밋(데이터베이스에 저장,수정,삭제등의 동작을 쌓아놨던 것들의 실행명령)을 한다.
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # 수정사항에 대한 track을 하지 않는다. True로 한다면 warning 메시지유발
    app.config['SECRET_KEY'] = 'wcsfeufhwiquehfdx'

    csrf = CSRFProtect()
    csrf.init_app(app)

    db.init_app(app)
    db.app = app
    db.create_all()  # db 생성

    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    socketio.run(app, host='0.0.0.0')
