from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FloatField, IntegerField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class CarbonFootprintForm(FlaskForm):

    body_type = StringField('Body Type', validators=[DataRequired()])
    sex = StringField('Sex', validators=[DataRequired()])
    diet = StringField('Diet', validators=[DataRequired()])
    shower = IntegerField('How Often Shower (days)', validators=[DataRequired()])
    heating_energy_source = StringField('Heating Energy Source', validators=[DataRequired()])
    transport = StringField('Transport', validators=[DataRequired()])
    vehicle_type = StringField('Vehicle Type', validators=[DataRequired()])
    social_activity = SelectField(
        'Social Activity',
        choices=[('often', 'Often'), ('sometimes', 'Sometimes'), ('rarely', 'Rarely'), ('never', 'Never')],
        validators=[DataRequired()]
    )
    grocery_bill = FloatField('Monthly Grocery Bill', validators=[DataRequired()])
    air_travel = SelectField(
        'Frequency of Traveling by Air',
        choices=[('very frequently', 'Very Frequently'), ('frequently', 'Frequently'), ('rarely', 'Rarely'), ('never', 'Never')],
        validators=[DataRequired()]
    )
    vehicle_distance = FloatField('Vehicle Monthly Distance (Km)', validators=[DataRequired()])
    waste_bag_size = SelectField(
        'Waste Bag Size',
        choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large'), ('extra large', 'Extra Large')],
        validators=[DataRequired()]
    )
    waste_bag_count = FloatField('Waste Bag Weekly Count', validators=[DataRequired()])
    tv_pc_hours = FloatField('How Long TV/PC Daily (hours)', validators=[DataRequired()])
    new_clothes = FloatField('How Many New Clothes Monthly', validators=[DataRequired()])
    internet_hours = FloatField('How Long Internet Daily (hours)', validators=[DataRequired()])
    energy_efficiency = SelectField(
        'Energy Efficiency',
        choices=[('No', 'No'), ('Sometimes', 'Sometimes'), ('Yes', 'Yes')],
        validators=[DataRequired()]
    )
    submit = SubmitField('Predict')
