from flask_api import FlaskAPI, status
from flask_sqlalchemy import SQLAlchemy
from app.models.database import db
from app.models.users_model import User 
from app.models.drives_model import Rides
from flask import Blueprint, render_template, abort, request, make_response, jsonify, redirect, session, url_for # Blueprints

# For route
from sqlalchemy import exc

# local import
from instance.config import app_config


def create_app(config_name):
    # creates flask application
    app = FlaskAPI(
            __name__, 
            instance_relative_config=True,
            static_url_path='/assets',
            static_folder='../html/light-bootstrap-dashboard-master/assets',
            template_folder='../html/light-bootstrap-dashboard-master',
            )

    # register blueprint here

    # set configurations
    app.config.from_object(app_config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

    # initialize database with application
    db.init_app(app)

    # POST /authenticate
    """
    Sample
    POST /authenticate
    Host: localhost:5000
    Content-Type: application/json

    {
        "username": "joe",
        "password": "pass"
    }
    """
    @app.route('/auth', methods=['POST', 'GET'])
    def authenticate():
        if request.method == 'POST':
            print('Post auth')
            print('Email: ' + request.form.get('email'))
            print('PW: ' + request.form.get('password'))
            try:
                # Get the user object using their email (unique to every user)

                user = User.query.filter_by(
                        email=request.form.get('email')
                        ).first()

                # Try to authenticate the found user using their password
                if user and user.validate_password(request.form.get('password')):
                    print('PW correct')
                    # Generate the access token.
                    # This will be used as the authorization header
                    access_token = user.generate_token(user.user_id)
                    if access_token:
                        # redirect_to_index = redirect('/request')
                        # response = make_response(redirect_to_index)
                        # response.set_cookie('access_token', value=access_token.decode())
                        # return response
                        session['email'] = request.form.get('email')
                        return redirect('request')

                else:
                    # User does not exist. Therefore, we return an error message
                    response = {
                            'err': 'Invalid username or password, Please try again'
                            }
                    return make_response(jsonify(response)), 401

            except Exception as e:
                # Create a response containing an string error message
                response = {'err': str(e)}
                # Return a server error using the HTTP Error
                # Code 500 (Internal Server Error)
                return make_response(jsonify(response)), 500
        else:
            return render_template('login.html')

    # POST /register
    """
    Sample json data
    {
        "first_name": "a",
        "last_name": "a12",
        "credit_card": 1234,
        "email": "1.@.1c22o1m1",
        "driver": false,
        "username": "na21211me",
        "password": "a"
    }
    """
    @app.route('/register', methods=['POST', 'GET'])
    def register():
        if request.method == 'POST':
            try:
                print('POST register')
                print('firstname: ' + request.form.get('firstname'))
                print('lastname: ' + request.form.get('lastname'))
                print('cc: ' + request.form.get('creditcard'))
                print('email: ' + request.form.get('email'))
                print('driver: ' + str(True if request.form.get('driver') else False))
                print('pw: ' + request.form.get('password'))
                temp_user = User(
                        first_name=request.form.get('firstname'),
                        last_name=request.form.get('lastname'),
                        credit_card=request.form.get('creditcard'),
                        email=request.form.get('email'),
                        driver=True if request.form.get('driver') else False,
                        username=request.form.get('username'),
                        password=request.form.get('password'),
                        date_created='S',
                        date_modified='S',
                        )
                temp_user.save()
                # access_token = temp_user.generate_token(temp_user.user_id)

                session['email'] = request.form.get('email')
                return redirect('request')
            except exc.OperationalError as e:
                # SQLalchemy missing value
                content = {'err': 'Missing value', 'info': 'Error: %s' % e}
                print(content)
                return render_template('register.html', content=content)
            except exc.IntegrityError as e:
                # SQLalchemy insertion error (such as duplicate value)
                content = {'err': 'Duplicate value', 'info': 'Error: %s' % e}
                print(content)
                return render_template('register.html', content=content)
        else:
            return render_template('register.html')

    @app.route("/request", methods=['POST', 'GET'])
    def request_ride():
        # access_token = parse_access_token(request)
        # Access token found
        if 'email' in session:
            # user_id = User.decode_token(request.cookies.get(''))
            # user_id = User.decode_token(access_token)
            # Token is valid
            print('Logged in as: ' + session['email'])
            if request.method == 'POST':
                # Decode access token and get user_id that
                # belongs to the user who requested the ride
                ride_data = request.data
                user = User.query.filter_by(
                        email=session['email']
                        ).first()
                temp_ride = Rides(
                        customer=user,
                        # driver is null at this moment
                        start_location=ride_data['start_location'],
                        end_location=ride_data['end_location'],
                        )
                temp_ride.save()
                response = {
                        'message': 'Ride request created'
                        }
                return response, status.HTTP_201_CREATED
            else:
                print('Render maps.html')
                return render_template('maps.html', requestingFlag=True)

    @app.route("/waiting", methods=['GET'])
    def waiting():
        # Access token found
        if 'email' in session:
            # Token is valid
            print('Looking for driver')
            print('Logged in as: ' + session['email'])
            # Find client
            user = User.query.filter_by(
                    email=session['email']
                    ).first()
            # Find the ride assosiated with the client
            ride = Rides.query.filter_by(
                    customer_id=user.user_id
                    ).first()
            print(ride.tojson())

            # If the ride.driver is null
            if ride.driver_id is None:
                # Render html with message Looking for driver to pick you up
                # Refresh the page periodically
                return render_template(
                        'waitmap.html', 
                        requestedFlag=True,
                        start=ride.start_location,
                        end=ride.end_location,
                        )
            # Else if the ride.driver is NOT null
            else:
                # Render html with driver found
                # Show where the driver is
                # Refresh the page periodically
                print('Driver found')
                return render_template(
                        'waitmap.html', 
                        driverFoundFlag=True,
                        start=ride.start_location,
                        driverpos={'lat': ride.current_lat, 'lng': ride.current_lng},
                        end=ride.end_location,
                        )

        # Token is invalid
        # Access token NOT found
        else:
            print('Render maps.html')
            return render_template('maps.html', requestingFlag=True)

    """
    GET /search
    Find all the imcompleted ride requests
    Only driver can access this API

    Return JSON: List of imcompleted ride requests
    """
    @app.route("/search", methods=['GET', 'POST'])
    def seach_ride():
        # Access token found
        if 'email' in session:
            # If POST: Called when driver chooses a ride
            if request.method == 'POST':
                print(request.data['id'])
                print(request.data['lat'])
                print(request.data['lng'])
                print(type(request.data['lat']))

                # request should contain driver's current location
                # and ride_id
                # Find the ride data by ride_id
                ride = Rides.query.filter_by(
                        ride_id=request.data['id']
                        ).first()
                print(ride)
                # Assign the driver to the ride
                user = User.query.filter_by(
                        email=session['email']
                        ).first()
                ride.driver_id = user.user_id
                ride.current_lat = str(request.data['lat'])
                ride.current_lng = str(request.data['lng'])
                ride.save()
                # Redirect to pick up page (Shows the route to the user)
                # MUST use js to refirect
                response = {'info': 'Ride appcepted'}
                return response, status.HTTP_200_OK
                
            # If GET
            else:
                # Render maps.html with all none picked up riders
                # Get user data
                user = User.query.filter_by(
                        email=session['email']
                        ).first()
                # User must be a driver
                if user.is_driver():
                    # If driver
                    # get all none picked up user data
                    print('Rides')
                    rides = Rides.find_all_no_driver_assigned_rides_in_json()
                    # render html with ride_id and user locations
                    return render_template(
                            'drivermap.html',
                            searchFlag=True,
                            rides=rides
                            )
                else:
                    return redirect('request')

        else:
            response = {'err': 'No access token found'}
            status_code = status.HTTP_400_BAD_REQUEST
            return response, status_code

    @app.route("/pickup", methods=['GET', 'POST'])
    def pickup():
        # Access token found
        if 'email' in session:
            # If POST: Called when driver chooses a ride
            if request.method == 'POST':
                print(request.data)
                # Picked up
                # Change the status to picked_up = True
                # Show the route to the destination

            else:
                # Show the route to the user
                # Show picked up button
                # Find user id
                user = User.query.filter_by(
                        email=session['email']
                        ).first()

                # Get ride data and send user location by user id and pick_up = false
                ride = Rides.query.filter_by(
                        driver_id=user.user_id,
                        picked_up=False
                        ).first()

                print('GET /pickup Ride info')
                print(ride.tojson())

                return render_template(
                        'drivermap.html',
                        pickupFlag=True,
                        ride=ride.tojson()
                        )

        else:
            response = {'err': 'No access token found'}
            status_code = status.HTTP_400_BAD_REQUEST
            return response, status_code

    return app
