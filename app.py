import requests,time,json
from bs4 import BeautifulSoup
from datetime import datetime
from flask import Flask, jsonify, make_response, redirect, render_template, url_for, send_from_directory, request
import urllib3,os

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'DEFAULT@SECLEVEL=1'



def cformat(string):
    findL=False
    findR=False
    for c in range(len(string)):
        if string[c] =="(": 
            findL=True
        if string[c] ==")" and findL: 
            findR=True
        if findL and findR:
            return (string[c+1:],string[1:c])
    return (string,"")
            

def getMovies(area,theater):
    theater=json.loads(theater)
    movies=[] #主列表
    movie_set=[]
    if theater['國賓'] ==True:
        try:
            ######國賓################################
            r = requests.get("https://www.ambassador.com.tw/home") #國賓首頁
            soup = BeautifulSoup(r.text,features="html.parser")
            soup = soup.find('ul',id='moveList') #找到電影選擇框

            allsels=soup.find_all('li') #在電影選擇框底下找到所有選項
            for item in allsels:
                movie_set.append(item.text)
                data={
                    'id':len(movies)+1,
                    'MovieName':(item.text,""),
                    'DisplayName':item.text,
                    'theater':'國賓',
                    'data':{
                        'MID':item['data-id']   #國賓的電影id
                    }
                }
                movies.append(data) #把每筆資料一一新增至主列表
            ##########################################
        except:
            pass
    if theater['威秀'] ==True:
        try:
            ######威秀################################
            r = requests.get(F"https://www.vscinemas.com.tw/vsweb/api/GetLstDicFilm/?area={area}").json() #威秀 api
            for item in r:
                movie_set.append(cformat(item["strText"])[0])
                data={
                    'id':len(movies)+1,
                    'MovieName':cformat(item["strText"]),
                    'DisplayName':item["strText"],
                    'theater':'威秀',
                    'data':{
                        'flim':item["strValue"] #威秀的電影id
                    }
                }
                movies.append(data) #把每筆資料一一新增至主列表
            ##########################################
        except:
            pass


    return movies,sorted(list(set(movie_set))) #回傳主列表


#################################################################################################################################################################################################


def getMoviesData_Ambassador(MID,peoples):
    showSessions=[]
    ##################
    date=datetime.now().strftime('%Y/%m/%d')
    url=F"https://www.ambassador.com.tw/home/MovieContent?MID={MID}&DT={date}" #EX MID=bb146545-71fd-4f60-8d15-c2241bb88c28 Date=2021/12/23
    r = requests.get(url)
    soup = BeautifulSoup(r.text,features="html.parser")
    soup = soup.find('ul',class_='menu scrollbar') #找到時間選擇框
    allsels=soup.find_all('li') #在時間選擇框底下找到所有時間選項

    time_list=[]
    for item in allsels:
        
        time_str=item.text.split(', ')[1] # '當日, 2021/12/22' ==> '2021/12/22'
        time_list.append(time_str)

    for date in time_list:
        url=F"https://www.ambassador.com.tw/home/MovieContent?MID={MID}&DT={date}" #EX MID=bb146545-71fd-4f60-8d15-c2241bb88c28 Date=2021/12/23
        r = requests.get(url)
        soup = BeautifulSoup(r.text,features="html.parser")
        theaterbox=soup.find('section',class_='theater-list')
        theater_list=theaterbox.find_all('div',class_='theater-box')
        for item in theater_list:
            displayname=item.find('p',class_='tag-seat').text
            theater=item.find('h3').find('a').text
            seat_list=item.find_all('li')
            for li in seat_list:
                data={
                    'date':date,
                    'time':li.find('h6').text,
                    'theater':theater,
                    'displayname':displayname,
                    'IsSeatEnough':True,
                }
                showSessions.append(data)
    return showSessions



def get_ranking():
	r = requests.get("https://www.ezding.com.tw/new_ezding/ranking_list/order_top?page=1&page_size=100000").json()
	if r['status']=='success':
		rankData=r['result']
		return rankData
	return "ERROR"

def get_movie_details(movie_id):
	r = requests.get(F"https://www.ezding.com.tw/new_ezding/movies/{movie_id}").json()
	if r['status']=='success':
		details=r['result']
		return details
	return "ERROR"

def get_cinema(id):
	r = requests.get(F"https://www.ezding.com.tw/new_ezding/orders/find_movie/{id}").json()
	if r['status']=='success':
		cinemaData=r['result']
		return cinemaData
	return "ERROR"
	
def get_movie_time(id,cinema_id):
	r = requests.get(F"https://www.ezding.com.tw/new_ezding/orders/find_movie_time?movie_id={id}&cinema_id={cinema_id}&page=1&page_size=10000").json()
	if r['status']=='success':
		timeData=r['result']
		return timeData
	return "ERROR"
def get_session(id):
	r = requests.get(F"https://www.ezding.com.tw/new_ezding/orders/find_movie_by_session?session_id={id}").json()
	if r['status']=='success':

		Data=r['result']
		return Data
	return "ERROR"

def rm_favorite(id):
    with open('fav.json', 'r') as jsonFile:
        j = json.load(jsonFile)
        jsonFile.close()

    for item in j['fav']:
        if item["session_id"]==id:
            j['fav'].remove(item)
    with open('fav.json', "w" , encoding="utf-8") as jsonFile:
        json.dump(j, jsonFile)
        jsonFile.close()
        return j['fav']
def add_to_favorite(data):
    with open('fav.json', 'r') as jsonFile:
        j = json.load(jsonFile)
        jsonFile.close()
    if data in j['fav']:
        return "err"
    with open('fav.json', "w" , encoding="utf-8") as jsonFile:
        j['fav'].append(data)
        json.dump(j, jsonFile)
        jsonFile.close()
        return j['fav']
def get_all_favorite():
    with open('fav.json', 'r') as jsonFile:
        j = json.load(jsonFile)
        jsonFile.close()
        return j['fav']


app = Flask(__name__,static_url_path="")
app.config['JSON_AS_ASCII'] = False

@app.route('/')
def home():
    return render_template("home.html")
@app.route('/movie/<id>')
def movie(id):
    data=get_movie_details(id)
    return render_template("movie.html",data=data,id=id)
@app.route('/favorite/')
def favorite():
    return render_template("fav.html")



@app.route('/api/getMovies', methods=['GET'])
def api_getMovies():
    movies=get_ranking()
    data={
        'status':'succ',
        'data':movies['list'],
    }
    return jsonify(data)
@app.route('/api/getMovieDetails/<id>', methods=['GET'])
def api_getMovieDetails(id):
    mv=get_movie_details(id)
    data={
        'status':'succ',
        'data':mv,
    }
    return jsonify(data)
@app.route('/api/getCinema/<id>', methods=['GET'])
def api_getCinema(id):
    data_=get_cinema(id)
    data={
        'status':'succ',
        'data':data_,
    }
    return jsonify(data)
@app.route('/api/getMovieTime/<id>/<cinema_id>', methods=['GET'])
def api_getMovieTime(id,cinema_id):
    data_=get_movie_time(id,cinema_id)
    data={
        'status':'succ',
        'data':data_,
    }
    return jsonify(data)

@app.route('/api/Fav', methods=["POST","GET"])
def api_Fav():
    data=json.loads(request.get_data())
    if data['type']=="add":
        fdata={
            'session_id':data['session_id'],
            'movie_id':data['movie_id'],
        }
        
        data_=add_to_favorite(fdata)
        data={
            'status':'succ',
            'data':data_,
        }
        return jsonify(data)
    elif data["type"]=="rm":
        id = data["id"]
        data_=rm_favorite(id)
        data={
            'status':'succ',
            'data':data_,
        }
        return jsonify(data)
    else:
        list=get_all_favorite()
        data_=[]
        for s in list:
            a={
                'session_id':s['session_id'],
                'session_data':get_session(s['session_id'])
            }

            data_.append(a)

        data={
            'status':'succ',
            'data':data_,
        }
        return jsonify(data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(debug=True,host='0.0.0.0', port=port)



