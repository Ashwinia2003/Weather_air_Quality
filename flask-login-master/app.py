from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms import CarbonFootprintForm, RegistrationForm, LoginForm
from models import create_user, get_user_by_email
import joblib
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime

import plotly.graph_objs as go

# Flask setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# API Keys
openWeatherMapApiKey = '24a87e9b43cc8219e6e793befdf656eb'
aqiApiKey = '132f67be1b7c0decb2f2135bafb77d0f692bec9a'
newsApiKey = 'pub_60468740a09a1aa459841d5b63f2f66466852'


# Load trained model and preprocessors
MODEL_PATH = "model/carbon_footprint_model.pkl"
ENCODERS_PATH = "model/label_encoders.pkl"
SCALER_PATH = "model/scaler.pkl"

model = joblib.load(MODEL_PATH)
label_encoders = joblib.load(ENCODERS_PATH)
scaler = joblib.load(SCALER_PATH)

# DataFrame to store historical data
historical_data = pd.DataFrame(columns=['Date', 'Carbon Emission'])

@app.route('/')
def home():
    return redirect(url_for('dashboard'))  # Redirect to the dashboard


@app.route('/dashboard')
def dashboard():
    # Plot the data for Carbon Footprint
    graph = {
        'data': [
            go.Scatter(x=historical_data['Date'], y=historical_data['Carbon Emission'], mode='lines+markers', name='Carbon Footprint')
        ],
        'layout': {
            'title': 'Carbon Emissions History',
            'xaxis': {'title': 'Date'},
            'yaxis': {'title': 'Total Carbon Footprint'},
        }
    }

    # Weather Data
    city = request.args.get('city', 'Thiruvananthapuram').strip()
    weather = {}
    try:
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={openWeatherMapApiKey}&units=metric"
        weather_response = requests.get(weather_url).json()
        if weather_response.get('cod') == 200:
            weather = {
                'city': city,
                'temperature': weather_response['main']['temp'],
                'feels_like': weather_response['main']['feels_like'],
                'humidity': weather_response['main']['humidity'],
                'pressure': weather_response['main']['pressure'],
                'wind_speed': weather_response['wind']['speed'],
                'visibility': weather_response['visibility'] / 1000,
                'sunrise': datetime.utcfromtimestamp(weather_response['sys']['sunrise']).strftime('%I:%M:%S %p'),
                'sunset': datetime.utcfromtimestamp(weather_response['sys']['sunset']).strftime('%I:%M:%S %p'),
            }
    except Exception:
        weather['error'] = "Error retrieving weather data"

    # AQI Data
    aqi = "N/A"
    aqi_status = "N/A"
    try:
        aqi_url = f"https://api.waqi.info/feed/{city}/?token={aqiApiKey}"
        aqi_response = requests.get(aqi_url).json()
        if 'data' in aqi_response and 'aqi' in aqi_response['data']:
            aqi = aqi_response['data']['aqi']
            aqi_status = "Good" if aqi <= 50 else "Moderate" if aqi <= 100 else "Unhealthy"
    except Exception:
        aqi_status = "Error retrieving AQI data"

    # News Data
    news = []
    try:
        news_url = f"https://newsdata.io/api/1/news?apikey={newsApiKey}&q={city}&language=en"
        news_response = requests.get(news_url).json()
        news = [{'title': a['title'], 'link': a['link'], 'image': a.get('image_url')} for a in news_response.get('results', []) if 'title' in a]
    except Exception:
        news = []

    return render_template('dashboard.html', graph=graph, weather=weather, aqi=f"{aqi} ({aqi_status})", news=news)


@app.route('/carbon_interface')
def carbon_interface():
    return redirect(url_for('home'))  # Redirect to the form page for carbon footprint


@app.route('/form', methods=['GET', 'POST'])
def form_page():  # Renamed to avoid conflict with '/dashboard'
    form = CarbonFootprintForm()
    if form.validate_on_submit():
        # Collect form data
        input_data = {
            'Body Type': form.body_type.data,
            'Sex': form.sex.data,
            'Diet': form.diet.data,
            'How Often Shower': form.shower.data,
            'Heating Energy Source': form.heating_energy_source.data,
            'Transport': form.transport.data,
            'Vehicle Type': form.vehicle_type.data,
            'Social Activity': form.social_activity.data,
            'Monthly Grocery Bill': form.grocery_bill.data,
            'Frequency of Traveling by Air': form.air_travel.data,
            'Vehicle Monthly Distance Km': form.vehicle_distance.data,
            'Waste Bag Size': form.waste_bag_size.data,
            'Waste Bag Weekly Count': form.waste_bag_count.data,
            'How Long TV PC Daily Hour': form.tv_pc_hours.data,
            'How Many New Clothes Monthly': form.new_clothes.data,
            'How Long Internet Daily Hour': form.internet_hours.data,
            'Energy efficiency': form.energy_efficiency.data,
        }

        # Data preprocessing
        df = pd.DataFrame([input_data])
        mappings = {
            'Social Activity': {'often': 3, 'sometimes': 2, 'rarely': 1, 'never': 0},
            'Frequency of Traveling by Air': {'very frequently': 4, 'frequently': 3, 'rarely': 2, 'never': 1},
            'Waste Bag Size': {'small': 1, 'medium': 2, 'large': 3, 'extra large': 4},
            'Energy efficiency': {'No': 0, 'Sometimes': 1, 'Yes': 2},
        }
        for column, mapping in mappings.items():
            if column in df.columns:
                df[column] = df[column].map(mapping)

        categorical_columns = ['Body Type', 'Sex', 'Diet', 'Transport', 'Vehicle Type', 'Heating Energy Source']
        for col in categorical_columns:
            if col in label_encoders:
                df[col] = label_encoders[col].transform(df[col].astype(str))

        numerical_columns = ['Monthly Grocery Bill', 'Vehicle Monthly Distance Km', 'Waste Bag Weekly Count',
                             'How Long TV PC Daily Hour', 'How Many New Clothes Monthly', 'How Long Internet Daily Hour']
        df[numerical_columns] = scaler.transform(df[numerical_columns])

        # Make prediction
        prediction = model.predict(df)[0]

        # Append to historical data
        global historical_data
        historical_data = pd.concat(
            [historical_data, pd.DataFrame({'Date': [pd.Timestamp.now()], 'Carbon Emission': [prediction]})],
            ignore_index=True
        )

        # Redirect to result page
        return redirect(url_for('result', emission=prediction))
    return render_template('form.html', form=form)

# Sample leaderboard data
leaderboard_data = []

@app.route('/result', methods=['GET', 'POST'])
def result():
    emission = request.args.get('emission', None)
    
    if request.method == 'POST':
        name = request.form.get('name')  # Get the user's name from the form
        if name and emission:
            # Add the user's data to the leaderboard
            leaderboard_data.append({'name': name, 'carbon_emission': float(emission)})
            # Sort the leaderboard by carbon emission in descending order
            leaderboard_data.sort(key=lambda x: x['carbon_emission'], reverse=True)

        # Redirect to the leaderboard
        return redirect(url_for('leaderboard'))
    
    # Pass sorted leaderboard to the result page
    return render_template('result.html', emission=emission, leaderboard=leaderboard_data, enumerate=enumerate)

@app.route('/leaderboard')
def leaderboard():
    # Render the leaderboard page
    return render_template('leaderboard.html', leaderboard=leaderboard_data, enumerate=enumerate)

@app.route('/visualize')
def visualize():
    # Sample historical data for carbon emission trends
    historical_data = pd.DataFrame({
        'Date': pd.date_range('2022-01-01', periods=10, freq='D'),
        'Carbon Emission': [100, 150, 200, 250, 300, 350, 400, 450, 500, 550]
    })
    
    if historical_data.empty:
        return "No data available for visualization!"
    
    # Create the Plotly figure
    fig = px.line(historical_data, x='Date', y='Carbon Emission', title='Carbon Emission Trends Over Time')
    
    # Convert the figure to HTML to embed it in the template
    fig_html = fig.to_html(full_html=False)
    
    # Render the HTML template and pass the graph HTML
    return render_template('visualize.html', plot_html=fig_html)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = create_user(form.username.data, form.email.data, form.password.data)
        login_user(user)
        flash('Account created!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_email(form.email.data)
        if user and user.password == form.password.data:
            login_user(user, remember=form.remember.data)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Check your email and/or password.', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)