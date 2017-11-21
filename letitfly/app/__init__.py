#<<<<<<< Dev_user_wait
from flask_api import FlaskAPI, status
from flask_sqlalchemy import SQLAlchemy
from app.models.database import db
from app.models.users_model import User
from app.models.drives_model import Rides
from flask import Blueprint, render_template, abort, request, make_response, jsonify, redirect, session, url_for # Blueprints

# For route
from sqlalchemy import exc
#=======
from flask import request
from flask_api import FlaskAPI
#>>>>>>> master

from app.models.database import db
from app.routes.user_routes import authenticate, register
from app.routes.ride_routes import request_ride, search_for_ride
from instance.config import app_config

# currently only being used by hello
from app.models.users_model import User
from app.models.drives_model import Rides


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
#<<<<<<< Dev_user_wait
    def authenticate():
        session.clear()
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

                    return render_template('login.html', responsecode=401, response="Invalid username or password, Please try again")

            except Exception as e:
                # Create a response containing an string error message
                response = {'err': str(e)}
                # Return a server error using the HTTP Error
                # Code 500 (Internal Server Error)
                return make_response(jsonify(response)), 500
        else:
            return render_template('login.html')
#=======
    def auth():
        return authenticate(request)
#>>>>>>> master

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
#<<<<<<< Dev_user_wait
    def register():
        session.clear()
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


    @app.route("/logout", methods=['POST', 'GET'])
    def logout():
        #log out of user session
        session.clear()
        return redirect('auth')

    @app.route("/request", methods=['POST', 'GET'])
    def request_ride():
        # access_token = parse_access_token(request)
        # Access token found
        print('In /request')
        
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
        else:
            print('Sessiong not found')
            return redirect('auth')



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
                    customer_id=user.user_id,
                    time_finished=None
                    ).first()
            print(ride.tojson())

            # If the ride.driver is null and
            # not picked up
            # not finished
            if ride.driver_id is None and \
               ride.picked_up is False and \
               ride.time_finished is None:
                # Render html with message Looking for driver to pick you up
                # Refresh the page periodically
                return render_template(
                        'waitmap.html',
                        requestedFlag=True,
                        start=ride.start_location,
                        end=ride.end_location,
                        )
            # Else if the ride.driver is NOT null
            # Not yet picked up
            # Not yet finished
            elif ride.driver_id is not None and \
                 ride.picked_up is False:
                # ride.time_finished is None:
                # Render html with driver found
                # Show where the driver is
                # Refresh the page periodically
                # TODO If driver_id is NOT null and picked_up = True
                # Show rider is picked up
                # TODO if driver id is NOT null and picked up = True and finished_date is NOT null
                # Show the rider amount they paid
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
#=======
    def reg():
        return register(request)

    @app.route("/request", methods=['POST', 'GET'])
    def req_ride():
        return request_ride(request)

#>>>>>>> master

    """
    GET /search
    Find all the imcompleted ride requests
    Only driver can access this API
    Return JSON: List of imcompleted ride requests
    """
#<<<<<<< Dev_user_wait
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

                # Save the ride id to session
                session['ride_id'] = ride.ride_id

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
                # Driver can pick up a rider only if
                # Distance between driver and rider is less than 1 mile
                # Distance check is already done by javascript in frontend
                # When the program goes here, distance between drivre and rider is less than 1 mile
                # Change the status to picked_up = True
                # Show the route to the destination
                # Redirect to drive
                # Redirect must be done by JS here
                ride = Rides.query.filter_by(
                        ride_id=session['ride_id']
                        ).first()
                ride.picked_up = True
                ride.save()
                response = {'info': 'Rider picked up'}
                return response, status.HTTP_200_OK

            else:
                # Show the route to the user
                # Show picked up button
                # Get ride data and send user location by user id and pick_up = false
                ride = Rides.query.filter_by(
                        ride_id=session['ride_id']
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
#=======
    @app.route("/search", methods=['GET'])
    def search_ride():
        return search_for_ride(request)

    @app.route("/history", methods=['GET'])
    def get_history():
        return get_drive_history(request)
#>>>>>>> master

    @app.route("/drive", methods=['GET', 'POST'])
    def drive():
        # Access token found
        if 'email' in session:
            # If POST: Called when driver chooses a ride
            # driver can see the the route to the destination from current location
            # Set the finished date so rider can also see the amount they paid
            if request.method == 'POST':
                # Driver dropping off the client
                # Set the finish time
                # Render to payment
                # rendering must be done by the js
                ride = Rides.query.filter_by(
                        ride_id=session['ride_id']
                        ).first()
                ride.set_current_to_time_finished()
                response = {'info': 'Dropped off a rider'}
                return response, status.HTTP_200_OK

            else:
                # Driver can see the route to the destination
                # [When I have time] Update the driver location periodically
                ride = Rides.query.filter_by(
                        ride_id=session['ride_id']
                        ).first()

                return render_template(
                        'drivermap.html',
                        driveFlag=True,
                        ride=ride.tojson()
                        )

        else:
            response = {'err': 'No access token found'}
            status_code = status.HTTP_400_BAD_REQUEST
            return response, status_code

    @app.route("/payment", methods=['GET'])
    def payment():
        # Access token found
        if 'email' in session:
            # Driver can see the money they earned
            # Driver can click a button to go /search
            # to find another ride and start ride again
            ride = Rides.query.filter_by(
                    ride_id=session['ride_id']
                    ).first()
            return render_template(
                    'drivermap.html',
                    ride=ride.tojson(),
                    paymentFlag=True,
                    )

        else:
            response = {'err': 'No access token found'}
            status_code = status.HTTP_400_BAD_REQUEST
            return response, status_code

    return app
