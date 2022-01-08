import requests,time,json
from bs4 import BeautifulSoup
from datetime import datetime
from flask import Flask, jsonify, make_response, redirect, render_template, url_for, send_from_directory, request
import urllib3,os

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'DEFAULT@SECLEVEL=1'

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
	

app = Flask(__name__,static_url_path="")
app.config['JSON_AS_ASCII'] = False

@app.route('/')
def home():
    return render_template("home.html")
@app.route('/movie/<id>')
def movie(id):
    data=get_movie_details(id)
    return render_template("movie.html",data=data,id=id)
    
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
	
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(debug=True,host='0.0.0.0', port=port)



