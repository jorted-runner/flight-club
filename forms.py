from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField, FloatField, EmailField, PasswordField, IntegerField
from wtforms.validators import DataRequired, URL, Length

class AddDests(FlaskForm):
    city_name = StringField("Destination City", validators=[DataRequired()])
    country = StringField("Destination Country", validators=[DataRequired()])
    fly_from = StringField("Orgin City", validators=[DataRequired()])
    max_price = FloatField("Max Price", validators=[DataRequired()])
    min_nights_in_dest = IntegerField("Minimum Nights in Destination", validators=[DataRequired()]) 
    max_nights_in_dest = IntegerField("Maximum Nights in Destination", validators=[DataRequired()]) 
    max_stopovers = FloatField("Maximum Number of Layovers")
    max_stopover_len = FloatField("Maximum Length of Layovers")
    submit = SubmitField("Submit")

class NewUser(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired()])
    email = EmailField("Email Address", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min= 8)])
    submit = SubmitField("Register")
    
class UserLogin(FlaskForm):
    email = EmailField("Email Address", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")