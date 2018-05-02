from flask import Flask, render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from models import db, Vendor, Person, Review, Category
import psycopg2
import psycopg2.extras
from psycopg2.extensions import AsIs

app = Flask(__name__)

POSTGRES = {
    'user': 'postgres',
    'pw': 'root',
    'db': 'taipei_places',
    'host': 'localhost',
    'port': '5432'
}

#initialize connection/cursor to database
try:
    conn = psycopg2.connect("dbname='taipei_places' user='postgres' host='localhost' password='root'")
except:
    print("Cannot connect to database.")

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
db.init_app(app)

#Secret key for Flask sessions
app.secret_key = 'tAiPeI'

@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.route("/")
def main():
    #return render_template('result.html', data=session['users'])
    # if the user is logged in, have all the posts available to the user display
    if (session.get('logged_in') == True):
        cursor = conn.cursor()
        username = session['username']
        cursor.close()

        initiate()

        # get all the users
        userQuery = 'SELECT username, name FROM person'
        userData = getData(userQuery)

        return render_template("index.html", userData=userData)
    return render_template('index.html')

@app.route('/search/processing', methods=['GET', 'POST'])
def searchProcessed():
    if (not session.get('logged_in')):
        return redirect(url_for('main'))

    #search by category, district, or both --> return all vendors related
    search_item = False
    if (request.form['search_item']):
        search_item = request.form['search_item']
    selected_dist = request.form.get('dist_dropdown')

    # get all the likes
    likesQuery = 'SELECT * FROM likes'
    likesData = getData(likesQuery)

    # get all the likes for the post each time
    allLikes = {}
    for restaurant in likesData:
        if restaurant['vID'] not in allLikes.keys():
            allLikes[restaurant['vID']] = {}
            allLikes[restaurant['vID']]['users'] = []
        allLikes[restaurant['vID']]['users'].append(restaurant['username'])
   
    #Search both district and category
    if (selected_dist != "None" and search_item):
        present = False
        #check if category exists, else produce error
        catQuery = """SELECT "cName" FROM category WHERE "cName" LIKE """+"'%"+search_item+"%'"
        categories = getData(catQuery)
        
        #check if category query is blank, if not then present
        if len(categories) > 0:
            present = True

        if (present): #retrieve restaurants
            resultQuery = """SELECT * FROM vendor NATURAL JOIN has WHERE "cName" LIKE """+"'%"+search_item+"%' AND district = """+"'"+selected_dist+"'"
            resultData = getData(resultQuery)
            #TODO: Add reviews to each restaurant/vendor
            return render_template('searchres.html', resultData=resultData, likesData=likesData, userLikesData=allLikes)
            
        if (present == False):
            error = "Category does not exist."
            return render_template('index.html', error=error)
    #Search by category only
    elif (search_item and selected_dist == "None"): 
        present = False
        #check if category exists, else produce error
        catQuery = """SELECT "cName" FROM category WHERE "cName" LIKE """+"'%"+search_item+"%'"
        categories = getData(catQuery)
        
        #check if category query is blank, if not then present
        if len(categories) > 0:
            present = True

        if (present): #retrieve restaurants
            searchQuery = """SELECT * FROM vendor NATURAL JOIN has WHERE "cName" LIKE """+"'%"+search_item+"%'"
            searchData = getData(searchQuery)
            #TODO: Add reviews to each restaurant/vendor
            return render_template('searchres.html', resultData=searchData, likesData=likesData, userLikesData=allLikes)
            
        if (present == False):
            error = "Category does not exist."
            return render_template('index.html', error=error)
    #Search by district only
    elif (selected_dist != "None" and search_item == False):
        distQuery = """SELECT * FROM vendor WHERE district = """+"'"+selected_dist+"'"
        distData = getData(distQuery)
        return render_template('searchres.html', resultData=distData, likesData=likesData, userLikesData=allLikes)
    #If nothing, no results 
    elif (selected_dist == "None" and search_item == False):
        error = "Please enter a keyword or district."
        return render_template('index.html', error=error)
    return render_template('searchres.html')

@app.route("/restaurants")
def restaurants():
    # if the user is logged in, have all the restaurants available to the user display
    if (session.get('logged_in') == True):
        username = session['username']
        initiate()

        # get all the users
        userQuery = 'SELECT username, name FROM person'
        userData = getData(userQuery)

        # get all the restaurants
        vendorQuery = 'SELECT * FROM vendor'
        vendorData = getData(vendorQuery)

        # get reviews from restaurants
        reviewQuery = 'SELECT * FROM review'
        reviewData = getData(reviewQuery)
        reviews = storeReviews(reviewData)

        # get all the likes
        likesQuery = 'SELECT * FROM likes'
        likesData = getData(likesQuery)

        # get all the likes for the post each time
        allLikes = {}
        for restaurant in likesData:
            if restaurant['vID'] not in allLikes.keys():
                allLikes[restaurant['vID']] = {}
                allLikes[restaurant['vID']]['users'] = []
            allLikes[restaurant['vID']]['users'].append(restaurant['username'])

        return render_template("restaurants.html", userData=userData, vendorData=vendorData, reviewData=reviewData, likesData=likesData, userLikesData=allLikes)
    return render_template('restaurants.html')

def storeReviews(data):
    session['reviews'] = {}
    for info in data:
        if info['vID'] not in session['reviews'].keys():
            session['reviews'][info['vID']] = []
        session['reviews'][info['vID']].append({'author': info['author'],
                                            'description': info['description'],
                                            'rating': info['rating']})
    return;

@app.route('/likes')
def likes():
    if (not session.get('logged_in')):
        return redirect(url_for('main'))

    # get all the likes
    likesQuery = 'SELECT * FROM likes'
    likesData = getData(likesQuery)

    # get all the likes for the post each time
    allLikes = {}
    for restaurant in likesData:
        if restaurant['vID'] not in allLikes.keys():
            allLikes[restaurant['vID']] = {}
            allLikes[restaurant['vID']]['users'] = []
        allLikes[restaurant['vID']]['users'].append(restaurant['username'])

    likeVendorQuery = """SELECT * FROM vendor NATURAL JOIN likes"""
    likeVendorData = getData(likeVendorQuery)
    
    return render_template('likes.html', likesData=likesData, userLikesData=allLikes, likeVendorData=likeVendorData)

#likes a restaurant via INSERT into likes table, and then redirect to likes page
@app.route('/like-restaurant/<vendor_vid>')
def likeRestaurant(vendor_vid):
    if (not session.get('logged_in')):
        return redirect(url_for('main'))
    
    cursor = conn.cursor()
    likeQuery = """INSERT INTO likes ("username", "vID") VALUES ('"""+session['username']+"""', '"""+vendor_vid+"""')"""
    cursor.execute(likeQuery)
    conn.commit()
    cursor.close()

    return redirect(url_for('likes'))

@app.route('/unlike-restaurant/<vendor_vid>')
def unlikeRestaurant(vendor_vid):
    if (not session.get('logged_in')):
        return redirect(url_for('main'))

    cursor = conn.cursor()
    dislikeQuery = """DELETE FROM likes WHERE "username" = '"""+session['username']+"""' AND "vID"="""+"'"+vendor_vid+"'"
    cursor.execute(dislikeQuery)
    conn.commit()
    cursor.close()

    return redirect(url_for('likes'))

@app.route('/login')
def login():
    return render_template('login.html')

#Authenticates logins
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    username = request.form['username']
    password = request.form['password']

    cursor = conn.cursor()
    query = 'SELECT * FROM person WHERE username = %s and password = %s'
    cursor.execute(query, (username, password))
    #stores results in var
    data = cursor.fetchone()
    cursor.close()

    if (data):
        session['logged_in'] = True
        session['username'] = username
        return redirect(url_for('main', username=session['username']))
    else:
        error = "Invalid login or username/password"
        return render_template('login.html', error=error)

def initiate():
    # get all the users
    userQuery = 'SELECT username, name, gender, age FROM person'
    userData = getData(userQuery)
    storeUsers(userData)

def getData(query):
    cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor) #allows dictionary for user sessions
    cursor.execute(query)
    data = cursor.fetchall()
    conn.commit()
    cursor.close()
    return(data)

def storeUsers(data):
    # store users in a session users dictionary
    # which can be used to access users' fullname.
    session['users'] = {}
    for user in data:
        session['users'][user['username']] = {}
        session['users'][user['username']]['name'] = user['name']
    return;

@app.route('/register')
def register():
    userdata = initiate()
    #return render_template("result.html", data=userdata)
    return render_template('register.html')

@app.route('/register/processing', methods=['GET', 'POST'])
def registerProcessing():
    username = request.form['username']
    if username in session['users'].keys():
        errormsg = "Username already taken."
        return render_template('register.html', error = errormsg)
    if len(username) < 4:
        errormsg = "Username is too short. Must be more than 3 characters."
        return render_template('register.html', error = errormsg)
    elif len(username) > 50:
        errormsg = "Username and/or other fields are too long. 50 characters max."
        return render_template('register.html', error = errormsg)
    password = request.form['password']
    if len(password) < 4:
        errormsg = "Password is too short (needs to be greater than 3 characters)."
        return render_template('register.html', error = errormsg)
    elif len(password) > 50:
        errormsg = "Password is too long. 50 characters max."
        return render_template('register.html', error = errormsg)
    retype = request.form['retype']
    if retype != password:
        errormsg = "Passwords do not match."
        return render_template('register.html', error = errormsg)

    #TO DO: PERFORM CHECKS
    name = request.form['fullname']
    age = request.form['age']
    gender = request.form['gender']
    cursor = conn.cursor()
    query = 'INSERT INTO person (username, password, name, age, gender) VALUES (%s, %s, %s, %s, %s)'
    cursor.execute(query, (username, password, name, age, gender))
    conn.commit()
    cursor.close()

    session['logged_in'] = True
    session['username'] = username
    session['users'][username] = {}
    session['users'][username]['name'] = name
    
    return redirect(url_for('main', username = session['username']))

@app.route('/logout')
def logout():
    session.pop('logged_in', False)
    session.pop('username', None)
    return redirect(url_for('main'))

if __name__ == '__main__':
    app.run()
