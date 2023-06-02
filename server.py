from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_apscheduler import APScheduler

from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from data_manager import DataManager
from flight_search import FlightSearch
from flight_data import FlightData
from notification_manager import NotificationManager

from forms import AddDests, NewUser, UserLogin

import os
from dotenv import load_dotenv


def configure():
    load_dotenv()

configure()

db = SQLAlchemy()
app = Flask(__name__)
schedular = APScheduler()
app.config['SECRET_KEY'] = os.environ.get("appSecretKey")
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///destinations.db").replace("postgres://", "postgresql://", 1) 

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

class Users(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    name = db.Column(db.String(250), unique=False, nullable=False)
    password = db.Column(db.String(250), unique=False, nullable=False)
    destinations = relationship("Destinations", back_populates="user")

class Destinations(db.Model):
    __tablename__ = "destinations"
    id = db.Column(db.Integer, primary_key=True)
    dest_city = db.Column(db.String(250))
    fly_from = db.Column(db.String(250))
    fly_from_iata = db.Column(db.String(250))
    dest_country = db.Column(db.String(250))
    dest_iata_code = db.Column(db.String(250))
    max_price = db.Column(db.Float)
    min_nights = db.Column(db.Integer)
    max_nights = db.Column(db.Integer)
    max_stopovers = db.Column(db.Integer)
    max_leng_stopovers = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = relationship("Users", back_populates="destinations")

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

data_manager = DataManager()
flight_search = FlightSearch()
notifications = NotificationManager()

@app.route("/")
def home():
    return render_template('index.html')

def send_daily_alerts():
    with app.app_context():
        users = Users.query.all()
        for user in users:
            user_destinations = user.destinations
            for destination in user_destinations:
                cheap_flights, PRICE = flight_search.search_cheap_flights(destination)
                find_cheapest = FlightData()
                lowest = find_cheapest.get_lowest_price(cheap_flights, PRICE)
                if len(lowest) == 0:
                    pass
                else:
                    cheapest_url = lowest["deep_link"]
                    email = user.email
                    departure, return_date = find_cheapest.get_dates_of_flights(lowest)
                    notifications.send_email(lowest, departure, return_date, cheapest_url, email)


@app.route('/register', methods=["GET", "POST"])
def register():
    new_user = NewUser()
    if new_user.validate_on_submit():
        if Users.query.filter_by(email=new_user.email.data).first():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('register'))
        new_user_name = request.form.get('name')
        new_user_email = request.form.get('email')
        new_user_password = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=8)
        new_user = Users(email = new_user_email, password = new_user_password, name = new_user_name)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home"))
    else:
        return render_template("register.html", form = new_user, current_user=current_user)
    
@app.route('/login', methods=["GET", "POST"])
def login():
    login_form = UserLogin()
    if login_form.validate_on_submit():
        if not Users.query.filter_by(email=login_form.email.data).first():
            flash("No user associated with that email, try registering!")
            return redirect(url_for('login'))
        email = request.form.get("email")
        user = Users.query.filter_by(email = email).first()
        if user:
            password = request.form.get('password')
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('user_dests'))
            else:
                flash("Incorrect Password, try again!")
                return render_template("login.html", form = login_form)
    else:
        return render_template("login.html", form = login_form, current_user=current_user)

@app.route("/destinations", methods=["GET", "POST"])
@login_required
def user_dests():
    user = Users.query.get(current_user.id)
    user_destinations = user.destinations
    return render_template('user_dests.html', destinations = user_destinations, current_user=current_user)

@app.route("/add-dest", methods=["GET", "POST"])
@login_required
def add_dest():
    new_dest = AddDests()    
    if new_dest.validate_on_submit():
        dest = Destinations(dest_city = new_dest.city_name.data, fly_from = new_dest.fly_from.data, fly_from_iata = flight_search.get_iata_codes(new_dest.fly_from.data), dest_country = new_dest.country.data, dest_iata_code = flight_search.get_iata_codes(new_dest.city_name.data),
                            max_price = new_dest.max_price.data, user_id=current_user.id,
                            min_nights = new_dest.min_nights_in_dest.data, max_nights = new_dest.max_nights_in_dest.data,
                            max_stopovers = new_dest.max_stopovers.data, max_leng_stopovers = new_dest.max_stopover_len.data)
        db.session.add(dest)
        db.session.commit()
        return redirect(url_for("user_dests"))
    return render_template ("add_cities.html", dest_form = new_dest, is_edit = False, current_user=current_user)

@app.route("/edit-dest/<dest_id>", methods=["GET", "POST"])
@login_required
def edit_dest(dest_id):
    destination = Destinations.query.get(dest_id)
    edit_dest_form = AddDests(city_name=destination.dest_city, country=destination.dest_country, fly_from = destination.fly_from, max_price=destination.max_price, min_nights_in_dest = destination.min_nights,
                              max_nights_in_dest = destination.max_nights, max_stopovers = destination.max_stopovers, max_stopover_len = destination.max_leng_stopovers)
    if edit_dest_form.validate_on_submit():
        destination.dest_city = edit_dest_form.city_name.data
        destination.fly_from = edit_dest_form.fly_from.data
        destination.fly_from_iata = flight_search.get_iata_codes(edit_dest_form.fly_from.data)
        destination.dest_country = edit_dest_form.country.data
        destination.dest_iata_code = flight_search.get_iata_codes(edit_dest_form.city_name.data)
        destination.max_price = edit_dest_form.max_price.data
        destination.min_nights = edit_dest_form.min_nights_in_dest.data
        destination.max_nights = edit_dest_form.max_nights_in_dest.data
        destination.max_stopovers = edit_dest_form.max_stopovers.data
        destination.max_leng_stopovers = edit_dest_form.max_stopover_len.data
        db.session.commit()
        return redirect(url_for("user_dests"))
    return render_template ("add_cities.html", dest_form = edit_dest_form, is_edit = True, current_user=current_user)

@app.route("/get-deals")
@login_required
def get_deals():
    user = Users.query.get(current_user.id)
    user_destinations = user.destinations
    for destination in user_destinations:
        cheap_flights, PRICE = flight_search.search_cheap_flights(destination)
        find_cheapest = FlightData()
        lowest = find_cheapest.get_lowest_price(cheap_flights, PRICE)
        if len(lowest) == 0:
            pass
        else:
            cheapest_url = lowest["deep_link"]
            email = current_user.email
            departure, return_date = find_cheapest.get_dates_of_flights(lowest)
            notifications.send_email(lowest, departure, return_date, cheapest_url, email)
    return redirect(url_for('user_dests'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/delete/<index>")
@login_required
def delete_post(index):
    dest_to_delete = Destinations.query.filter_by(id=index).first()
    db.session.delete(dest_to_delete)
    db.session.commit()
    return redirect(url_for('user_dests')) 

if __name__ == "__main__":
    schedular.add_job(id = 'Scheduled task', func= send_daily_alerts, trigger = 'cron', month= '*', day= '*', hour = '4')
    schedular.start()
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)