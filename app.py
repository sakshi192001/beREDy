from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import re
import pickle
from flask_mysqldb import MySQL
import MySQLdb.cursors
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
import os 
from datetime import date
# from werkzeug.utils import secure_filename
import pandas as pd
# from bs4 import BeautifulSoup
# from selenium import webdriver 
from datetime import datetime
import time
import datetime
from flask import Flask, render_template, request, jsonify
import nltk
import datetime
from nltk.stem.lancaster import LancasterStemmer

stemmer = LancasterStemmer()
seat_count = 50

import numpy as np
import tflearn
import tensorflow as tf
import random
import json
import pickle

with open("intents.json", encoding="utf8") as file:
	data = json.load(file)
with open("data.pickle","rb") as f:
	words, labels, training, output = pickle.load(f)

def bag_of_words(s, words):
	
	bag = [0 for _ in range(len(words))]
	
	s_words = nltk.word_tokenize(s)
	s_words = [stemmer.stem(word.lower()) for word in s_words]

	for se in s_words:
		for i,w in enumerate(words):
			if w == se:
				bag[i] = 1

	return np.array(bag)

tf.compat.v1.reset_default_graph()

net = tflearn.input_data(shape = [None, len(training[0])])
net = tflearn.fully_connected(net,8)
net = tflearn.fully_connected(net,8)
net = tflearn.fully_connected(net,len(output[0]), activation = "softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)
model.load("saved_model/my_model")

app = Flask(__name__)
  

#database connection details 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'hackjnu'

mysql = MySQL(app)
app.secret_key = 'key12'

# @app.route("/", methods=['GET', 'POST'])
# def index():
#     return render_template('index.html')

@app.route("/", methods=['GET', 'POST'])
def Register():
    msg = ''
    if request.method == 'POST' and 'FullName' in request.form and 'email' in request.form and 'Contact' in request.form and 'Password' in request.form and 'Gender' in request.form and 'Age' in request.form:
        # Create variables for easy access
        
        FullName = request.form['FullName']
        email = request.form['email']
        Contact = request.form['Contact']
        Password = request.form['Password']
        Gender = request.form['Gender']
        Age = request.form['Age']
                
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s AND Password=%s', [email, Password])
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'            
    
        # elif not re.match(r'[A-Za-z0-9]+', Username):
        #     msg = 'Username must contain only characters and numbers!'
            
        elif not email or not Password:
            msg = 'Please fill out the form!'
            
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO users VALUES(%s,%s,%s,%s,%s,%s)', [FullName,email,Contact, Password, Gender, Age])
            mysql.connection.commit()
            msg = 'Successfully registered! Please Log-In'
            
            return redirect(url_for('Login'))
            
    elif request.method != 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    return render_template("Register.html", msg=msg)

@app.route("/Login", methods=['GET', 'POST'])
def Login():
    msg=''
    if request.method == 'POST' and 'email' in request.form and 'Password' in request.form:
        
        email = request.form['email']
        Password = request.form['Password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email=%s AND Password=%s',[email, Password])
        user = cursor.fetchone()    
        
        # If account exists in accounts table in out database
        if user==None:
            msg = 'Incorrect Username or Password'
            print('if')
            # return redirect(url_for('login',msg=msg)) 
        else:
            print('else')
            session['loggedin'] = True
            session['email'] = user['email']
            session['FullName'] = user['FullName']
            return redirect(url_for('home'))

    
    return render_template('Login.html', msg=msg)   

@app.route("/home", methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route("/Products", methods=['GET', 'POST'])
def Products():
    return render_template('Products.html')

@app.route("/Product2", methods=['GET', 'POST'])
def Product2():
    return render_template('Product2.html')

@app.route("/Product3", methods=['GET', 'POST'])
def Product3():
    return render_template('Product3.html')

@app.route("/ShareExp", methods=['GET', 'POST'])
def ShareExp():    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM experiences')
    exp = cursor.fetchall() 
    if request.method=='POST':
        title=request.form['title']
        text=request.form['text']
        print(title,text)
        cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor1.execute('INSERT INTO experiences VALUES(%s,%s)',[title, text])
        mysql.connection.commit()

    return render_template('ShareExp.html',exp=exp)


@app.route("/Diagnosis", methods=['GET', 'POST'])
def Diagnosis():
    pr=''
    
    if request.method == 'POST':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT cyc_len, Age FROM users WHERE email=%s',[session['email']])
        details = cursor.fetchall() 

        bmi = request.form['bmi']
        pulse = request.form['pulse']
        rr = request.form['rr']
        heamo = request.form['heamo']
        
        preg = request.form['preg']
        abort = request.form['abort']
        waist = request.form['waist']
        weight = request.form['weight']
        growth = request.form['growth']
        loss = request.form['loss']
        skin = request.form['skin']
        pimples = request.form['pimples']
        reg_ex = request.form['reg_ex']
        sys = request.form['sys']
        dia = request.form['dia']
        
        model = pickle.load(open('model.pkl','rb'))    
        print(model)
        pred = model.predict([[details[0]['Age'], bmi, pulse, rr, heamo, details[0]['cyc_len'], preg, abort, waist, weight, growth, skin, loss, pimples, reg_ex, sys, dia ]])    
        print(pred)
        if pred[0]==0:
            pr = 'No'
        elif pred[0]==1:
            pr = 'Yes'
        session['var'] = pr
        return redirect(url_for('Diagnosis1'))
    return render_template('Diagnosis.html')

@app.route("/Diagnosis1", methods=['GET', 'POST'])
def Diagnosis1():
    var = session.get('var', None)
    print(type(var))
    print('aaaaaaaaaaaaaaaaaaaaa')
    if var=='Yes':
        op = 1
    else:
        op = 0
    return render_template('Diagnosis1.html', op=op)

@app.route("/Blogs", methods=['GET', 'POST'])
def Blogs():
    # obj_name='stages-of-menstrual-cycle'
    # PATH = "C:\Program Files (x86)\chromedriver.exe"
    # driver = webdriver.Chrome(PATH)
    # base = "https://www.healthline.com/health/womens-health/"
    # # input1 = "how+to+reuse+"
    # # input2 = obj_name
    # final_url = base+obj_name
    # driver.get(final_url)

    # data = driver.find_elements_by_xpath('//*[@id="video-title"]')
    # links = []
    # for i in data:
    #             links.append(i.get_attribute('href'))
    
    # glink1 = "how+to+reuse+"
    # glink2 = obj_name
    # query = glink1+glink2
    # glinks=[]
    # for page in range(1):
    #     url = "http://www.google.com/search?q=" + str(query) + "&start=" 
    #     driver.get(url)
    #     soup = BeautifulSoup(driver.page_source, 'html.parser')
    #     # soup = BeautifulSoup(r.text, 'html.parser')

    #     search = soup.find_all('div', class_="yuRUbf")
    #     for h in search:
    #         glinks.append(h.a.get('href'))
            


    # google_links =[glinks[0],glinks[1],glinks[2]]
    # youtube_inks = [links[0],links[1],links[2]]
    
    # LIST=[obj_name,imp,google_links,youtube_inks]
    return render_template('Blogs.html')

# @app.route("/CycleTracker", methods=['GET', 'POST'])
# def CycleTracker():    
    
#     return render_template('CycleTracker.html')



@app.route("/Calendar", methods=['GET', 'POST'])
def Calendar():   
    date = ''
    events = []
    dt_obj = ''

    if request.method == "POST":
        date = request.form['date']           
        print(date)
        string = str(date)

        dt = datetime.datetime.strptime(date, '%Y-%m-%d')
        print(dt)
        date1 = ("{0}-{1}-{2}".format(dt.day, dt.month, dt.year))

        string1 = time.mktime(datetime.datetime.strptime(date1,
                                                    "%d-%m-%Y").timetuple())

        next = string1 + 28*86400        
        dt_obj = datetime.datetime.fromtimestamp(next).strftime('%d-%m-%Y')

        print(type(dt_obj))
        dt_obj1 = dt_obj.split('-')
        print(dt_obj1)
        dt_obj2 = dt_obj1[2]+'-' + dt_obj1[1]+'-' + dt_obj1[0]
        print(dt_obj2)
        events = [{
    'todo':'Periods',
    'date': dt_obj2
    }]       

    return render_template('Calendar.html', events=events)


@app.route('/get')
def get_bot_response():
	global seat_count
	message = request.args.get('msg')
	if message:
		message = message.lower()
		results = model.predict([bag_of_words(message,words)])[0]
		result_index = np.argmax(results)
		tag = labels[result_index]
		if results[result_index] > 0.5:
			if tag == "book_table":
				seat_count -= 1
				response = "Your table has been booked successfully. Remaining tables: " + str(seat_count)
				
			elif tag == "available_tables":
				response = "There are " + str(seat_count) + " tables available at the moment."
				
			elif tag == "menu":
				day = datetime.datetime.now()
				day = day.strftime("%A")
				if day == "Monday":
					response = "Chef recommends: Steamed Tofu with Schezwan Peppercorn, Eggplant with Hot Garlic Sauce, Chicken & Chives, Schezwan Style, Diced Chicken with Dry Red Chilli, Schezwan Pepper"

				elif day == "Tuesday":
					response = "Chef recommends: Asparagus Fresh Shitake & King Oyster Mushroom, Stir Fried Chilli Lotus Stem, Crispy Fried Chicken with Dry Red Pepper, Osmanthus Honey, Hunan Style Chicken"

				elif day == "Wednesday":
					response = "Chef recommends: Baby Pokchoi Fresh Shitake Shimeji Straw & Button Mushroom, Mock Meat in Hot Sweet Bean Sauce, Diced Chicken with Bell Peppers & Onions in Hot Garlic Sauce, Chicken in Chilli Black Bean & Soy Sauce"

				elif day == "Thursday":
					response = "Chef recommends: Eggplant & Tofu with Chilli Oyster Sauce, Corn, Asparagus Shitake & Snow Peas in Hot Bean Sauce, Diced Chicken Plum Honey Chilli Sauce, Clay Pot Chicken with Dried Bean Curd Sheet"

				elif day == "Friday":
					response = "Chef recommends: Kailan in Ginger Wine Sauce, Tofu with Fresh Shitake & Shimeji, Supreme Soy Sauce, Diced Chicken in Black Pepper Sauce, Sliced Chicken in Spicy Mala Sauce"

				elif day == "Saturday":
					response = "Chef recommends: Kung Pao Potato, Okra in Hot Bean Sauce, Chicken in Chilli Black Bean & Soy Sauce, Hunan Style Chicken"

				elif day == "Sunday":
					response = "Chef recommends: Stir Fried Bean Sprouts & Tofu with Chives, Vegetable Thou Sou, Diced Chicken Plum Honey Chilli Sauce, Diced Chicken in Black Pepper Sauce"
			else:
				for tg in data['intents']:
					if tg['tag'] == tag:
						responses = tg['responses']
				response = random.choice(responses)
		else:
			response = "I didn't quite get that, please try again."
		return str(response)
	return render_template('index.html')



if __name__ =="__main__":
    app.run(debug=True)

