from flask import json
from flask import jsonify
from datetime import datetime
import uuid
from db_access_models import *
from operator import itemgetter
from send_emails_helper import *

ip_addresses = {}
MAX_ZIPS = 100
MAX_DOCS = 10000
MAX_TIME_LOGIN = 1


def send_return_response(message, error):
    response = jsonify({'message': message})
    response.status_code = error
    return response


class Welcome(Resource):
    def get(self):
        return_message = '<h1>Welcome to the Doctor Search API using ORM</h1>'
        return Response(return_message, mimetype='html')


class ApiUserRegister(Resource):
    def get(self):
        organization = request.args.get('organization')
        email = request.args.get('email')
        message = request.args.get('message')
        return_url = request.url
        remote_ip = request.remote_addr
        try:
            ip_count = ip_addresses[remote_ip]
            ip_addresses[remote_ip] = ip_count + 1
        except KeyError:
            ip_addresses[remote_ip] = 1

        if ip_addresses[remote_ip] > 5:
            return send_return_response('Requests limit exceeded', 400)
        # print(remote_ip)
        if not is_phrase_good(organization, 50):
            return send_return_response(
                'Organization must but be <= 50 characters with spaces, and no special characters', 400)
        if not check_email(email):
            return send_return_response('Invalid email format', 400)
        if message != '' and message is not None:
            message = filter_message(message, 150)
        else:
            message = 'No Message'

        yes_url = return_url + '&allow=true'
        no_url = return_url + '&allow=false'
        email_message = '<span><strong>Organization: </strong>' + organization + '</span></br><span><strong>Email: </strong>' \
                  + email + '</span></br></br><span><strong>Message: </strong>' + message + '</span></br></br>' \
                  '<form method="post" action="' + yes_url + '"class="inline"><input type="hidden" name="" value="">' \
                  '<button type="submit" name="allow" value="True"class="link-button">Allow new API User?</button></form>' \
                  '<form method="post" action="' + no_url + '" class="inline"><input type="hidden" name="extra_submit_param" ' \
                  'value="extra_submit_value"><button type="submit" name="allow"value="True" class="link-button">Reject ' \
                  'new API User?</button></form>'
        send_to_email = 'ron.knighton@orasi.com'
        email_response = send_email(send_to_email, email_message)
        return send_return_response('API User credentials requested from Admin. ' + email_response, 200)

    def post(self):
        url = request.url
        organization = request.args.get('organization')
        email = request.args.get('email')
        allow = request.args.get('allow')
        if allow == 'true':
            api_key = str(uuid.uuid4())
            api_secret = str(uuid.uuid4())
            # Use this if I want to hash the secret.
            # hashed_secret = hash_password(api_secret)
            try:
                api_user = ApiUser()
                if not api_user.is_api_email_available(email):
                    return send_return_response('There is already an API account associated with this email.', 400)

                new_api_user = ApiUser(
                    Organization=organization,
                    Email=email,
                    ApiKey=api_key,
                    ApiSecret=api_secret,
                    Created=datetime.now(),
                    ApiCalls=0,
                    Violations=0
                )
                api_user.create_api_user(new_api_user)
                message = "<h3>Your account has been authorized.</h3> <h4>API key: " + api_key + "</h4>" \
                          "<h4>API Secret: " + api_secret

                email_response = send_email(email, message)
                return_message = '<h1>The API account has been accepted</h1> <h2>' + email_response + '</h2>'

                return Response(return_message, mimetype='html')

            except Exception as e:
                return send_return_response(str(e), 500)
        else:
            return_message = '<h1>The API account has been rejected</h1>'
        return Response(return_message, mimetype='html')


class UserRegister(Resource):
    def get(self):
        code = request.args.get('code')
        url = request.url

        if not is_uuid_good(code):
            return_message = '<h1>Your verification code appears to be corrupted</h1>'
            return Response(return_message, mimetype='html')
        try:
            user = User()
            if user.verify_user(code):
                return_message = '<h1>Your email has been verified.</h1>'
                return Response(return_message, mimetype='html')
            else:
                return_message = '<h1>Something went wrong! Your email has NOT been verified</h1>'
                return Response(return_message, mimetype='html')

        except Exception as e:
            return send_return_response(str(e), 500)

    def post(self):
        api_key = request.args.get('key')
        api_secret = request.args.get('secret')
        firstname = request.args.get('firstname', '')
        lastname = request.args.get('lastname', '')
        nickname = request.args.get('nickname', '')
        email = request.args.get('email', '')
        password = request.args.get('password', '')
        url = request.url

        api_user = ApiUser()
        if not api_user.is_valid_api_user(api_key, api_secret):
            return send_return_response("Invalid Key or Secret", 400)

        if not is_string_good(firstname, 25):
            return send_return_response('First name but be <= 25 characters, and no special characters', 400)

        if not is_string_good(lastname, 25):
            return send_return_response('Last name but be <= 25 characters, and no special characters', 400)

        if not is_string_good(nickname, 25):
            return send_return_response('Nickname but be <= 25 characters, and no special characters', 400)

        if not check_email(email):
            return send_return_response('Invalid email format', 400)

        if not validate_password(password):
            return send_return_response('Password cannot have space, and must be less <= 15 characters.', 400)

        try:
            user = User()
            if not user.is_email_available(email):
                return send_return_response('There is already an account associated with this email.', 400)

            hashed_password = hash_password(password)
            date_time = datetime.now()
            verify_uuid = str(uuid.uuid4())
            new_user = User(
                Firstname=firstname,
                Lastname=lastname,
                Nickname=nickname,
                Email=email,
                Password=hashed_password,
                LoginTime=datetime.now(),
                VerifyUUID=verify_uuid
            )
            user.add_user(new_user)
            return_url = request.url
            end_of_url = return_url.find('/UserRegister/')
            return_url = return_url[:end_of_url + 14]
            return_url = return_url + '?code=' + verify_uuid
            message = "Please click <a href=" + return_url + ">link</a> to verify your email"
            email_response = send_email(email, message)
            return send_return_response('User saved. ' + email_response, 200)

        except Exception as e:
            return send_return_response(str(e), 500)


class UserLogin(Resource):
    def get(self):
        api_key = request.args.get('key')
        api_secret = request.args.get('secret')
        email = request.args.get('email')
        password = request.args.get('password')
        url = request.url

        api_user = ApiUser()
        if not api_user.is_valid_api_user(api_key, api_secret):
            return send_return_response("Invalid Key or Secret", 400)

        if not check_email(email):
            return send_return_response('Invalid email format', 400)

        if not validate_password(password):
            return send_return_response('Invalid password.', 400)

        try:
            user = User()
            dt = datetime.now()
            logged_in = user.login_user(email, password, dt)
            if not logged_in:
                return send_return_response('User not found or wrong password', 400)

            return send_return_response('User is logged in for ' + str(MAX_TIME_LOGIN) + ' hour', 200)

        except Exception as e:
            return send_return_response(str(e), 500)


class Practitioners(Resource):
    invalid_zip = False

    def get(self):
        api_key = request.args.get('key')
        api_secret = request.args.get('secret')
        postal_code = request.args.get('postalcode')
        radius_miles = request.args.get('radius_miles')
        taxonomy = request.args.get('taxonomy')
        url = request.url

        api_user = ApiUser()
        if not api_user.is_valid_api_user(api_key, api_secret):
            return send_return_response("Bad API Credentials", 400)

        if not is_postal_code_good(postal_code):
            return send_return_response('Only 5 digit zip code allowed', 400)

        if not is_radius_good(radius_miles):
            return send_return_response('Radius must be a positive integer value <= 50', 400)
        else:
            radius_miles = int(radius_miles)

        if taxonomy is not None:
            if not is_taxonomy_good(taxonomy):
                return send_return_response('Taxonomy is invalid format', 400)

        try:
            pc = Postalcodes()
            return_dict = pc.get_all_by_radius(postal_code, radius_miles)

            if len(return_dict) == 0:
                return send_return_response('Invalid zip code', 400)

            if len(return_dict['tested_zip_codes']) > MAX_ZIPS:
                return send_return_response('Too many zip codes to search! Please narrow search', 400)

            tested_zip_codes = return_dict['tested_zip_codes']
            zips_distance = return_dict['zips_distance']

            provider = Provider()
            doc_list = []
            if len(tested_zip_codes) == 1:
                if taxonomy:
                    docs = provider.get_all_by_zip_and_taxonomy(tested_zip_codes[0], taxonomy)
                else:
                    docs = provider.get_all_by_zip(tested_zip_codes[0])

            else:
                if taxonomy:
                    docs = provider.get_all_by_zips_and_taxonomy(tested_zip_codes, taxonomy)
                else:
                    docs = provider.get_all_by_zips(tested_zip_codes)

            for doc in docs:
                docs[doc].update({"Distance": round(zips_distance[docs[doc]["PostalCode"]], 2)})
                doc_list.append(docs[doc])

            if len(doc_list) == 0:
                return send_return_response('No providers match search', 400)
            results = sorted(doc_list, key=itemgetter('Distance'))
            if len(doc_list) > MAX_DOCS:
                results = results[:MAX_DOCS - 1]

            return jsonify(results)

        except Exception as e:
            return send_return_response(str(e), 500)


class PractitionersByName(Resource):
    def get(self):
        api_key = request.args.get('key')
        api_secret = request.args.get('secret')
        postal_code = request.args.get('postalcode')
        radius_miles = request.args.get('radius_miles')
        firstname = request.args.get('firstname')
        lastname = request.args.get('lastname')
        url = request.url

        api_user = ApiUser()
        if not api_user.is_valid_api_user(api_key, api_secret):
            return send_return_response("Bad API Credentials", 400)

        if not is_postal_code_good(postal_code):
            return send_return_response('Only 5 digit zip code allowed', 400)

        if not is_radius_good(radius_miles):
            return send_return_response('Radius must be a positive integer value <= 50', 400)
        else:
            radius_miles = int(radius_miles)

        if firstname != '':
            if not is_string_good(firstname):
                return send_return_response('First name but be <= 25 characters, and no special characters', 400)

        if not is_string_good(lastname):
            return send_return_response('Last name but be <= 25 characters, and no special characters', 400)

        try:
            pc = Postalcodes()
            return_dict = pc.get_all_by_radius(postal_code, radius_miles)

            if len(return_dict) == 0:
                return send_return_response('Invalid zip code', 400)

            if len(return_dict['tested_zip_codes']) > MAX_ZIPS:
                return send_return_response('Too many zip codes to search! Please narrow search', 400)

            tested_zip_codes = return_dict['tested_zip_codes']
            zips_distance = return_dict['zips_distance']

            provider = Provider()
            doc_list = []
            if len(tested_zip_codes) == 1:
                if firstname:
                    docs = provider.get_all_by_zip_and_fullname(tested_zip_codes[0], firstname, lastname)
                else:
                    docs = provider.get_all_by_zips_and_lastname(tested_zip_codes, lastname)

            else:
                if firstname:
                    docs = provider.get_all_by_zips_and_fullname(tested_zip_codes, firstname, lastname)
                else:
                    docs = provider.get_all_by_zips_and_lastname(tested_zip_codes, lastname)

            for doc in docs:
                docs[doc].update({"Distance": round(zips_distance[docs[doc]["PostalCode"]], 2)})
                doc_list.append(docs[doc])

            if len(doc_list) == 0:
                return send_return_response('No providers match search', 400)
            results = sorted(doc_list, key=itemgetter('Distance'))

            if len(doc_list) > MAX_DOCS:
                results = results[:MAX_DOCS - 1]

            return jsonify(results)

        except Exception as e:
            return send_return_response(str(e), 500)


class PractitionersByNpi(Resource):
    def get(self):
        api_key = request.args.get('key')
        api_secret = request.args.get('secret')
        npi = request.args.get('npi')
        postal_code = request.args.get('postalcode')
        url = request.url

        api_user = ApiUser()
        if not api_user.is_valid_api_user(api_key, api_secret):
            return send_return_response("Bad API Credentials", 400)

        if not is_postal_code_good(postal_code):
            return send_return_response('Only 5 digit zip code allowed', 400)

        if not is_npi_good(npi):
            return send_return_response('Invalid NPI', 400)

        try:
            pc = Postalcodes()
            zip = pc.get_by_zip(postal_code)

            if not zip:
                return send_return_response('Starting zip code not in database', 400)

            starting_lat = zip['Latitude']
            starting_long = zip['Longitude']

            provider = Provider()
            doc = provider.get_by_npi(npi)

            if not doc:
                return send_return_response('No matching providers', 400)

            doc_postal_code = doc["PostalCode"]
            if doc_postal_code == '':
                distance = -1
            else:
                doc_zip = pc.get_by_zip(doc_postal_code)
                if not doc_zip:
                    distance = -1
                else:
                    ending_lat = float(doc_zip['Latitude'])
                    ending_long = float(doc_zip['Longitude'])
                    distance = get_distance_geopy(starting_long, starting_lat, ending_long, ending_lat)

            doc.update({"Distance": round(distance, 2)})
            doc_list = [doc]

            return jsonify(doc_list)

        except Exception as e:
            return send_return_response(str(e), 500)


class Comments(Resource):
    def get(self):
        api_key = request.args.get('key')
        api_secret = request.args.get('secret')
        npi = request.args.get('npi')
        email = request.args.get('email')
        url = request.url

        api_user = ApiUser()
        if not api_user.is_valid_api_user(api_key, api_secret):
            return send_return_response("Bad API Credentials", 400)

        if not is_npi_good(npi):
            return send_return_response('Invalid NPI', 400)
        try:
            user = User()
            user_id = user.get_id_by_email(email)

            if not user_id:
                return send_return_response("Email not registered", 400)

            db_comments = Comment()
            comments = db_comments.get_all_by_npi(npi)

            for comment in comments:
                c_user_id = comment['User_Id']
                if c_user_id == user_id:
                    comment['User_Id'] = True
                else:
                    comment['User_Id'] = False

            return jsonify(comments)

        except Exception as e:
            print(str(e))
            return send_return_response(str(e), 500)

    def post(self):
        api_key = request.args.get('key')
        api_secret = request.args.get('secret')
        npi = request.args.get('npi')
        comment = request.args.get('comment')
        email = request.args.get('email')
        url = request.url

        api_user = ApiUser()
        if not api_user.is_valid_api_user(api_key, api_secret):
            return send_return_response("Bad API Credentials", 400)

        if not is_npi_good(npi):
            return send_return_response('Invalid NPI', 400)

        if not is_comment_good(comment):
            return send_return_response('Comment does not meet validation', 400)

        try:
            user = User()
            comment_user = user.get_by_email(email)

            if not user:
                return send_return_response("Email not registered", 400)

            now = datetime.now()
            if not is_user_allowed_post_comment(comment_user, now, MAX_TIME_LOGIN):
                return send_return_response("User not logged in or verified", 400)

            db_comment = Comment()
            new_comment = Comment(
                NPI=npi,
                Comment=comment,
                Created=now,
                User_Id=comment_user['Id']
            )
            db_comment.add_comment(new_comment)

            return send_return_response('Comment added', 200)
        
        except Exception as e:
            return send_return_response(str(e), 500)

    def put(self):
        api_key = request.args.get('key')
        api_secret = request.args.get('secret')
        comment = request.args.get('comment')
        id = request.args.get('id')
        email = request.args.get('email')
        url = request.url

        api_user = ApiUser()
        if not api_user.is_valid_api_user(api_key, api_secret):
            return send_return_response("Bad API Credentials", 400)

        if id is None:
            return send_return_response('Comment ID is not valid', 400)
        if not id.isdigit():
            return send_return_response('Comment ID is not valid', 400)

        if not is_comment_good(comment):
            return send_return_response('Comment does not meet validation', 400)

        try:
            user = User()
            comment_user = user.get_by_email(email)

            if not comment_user:
                return send_return_response("User not found", 400)

            now = datetime.now()
            if not is_user_allowed_post_comment(comment_user, now, MAX_TIME_LOGIN):
                return send_return_response("User not logged in or verified", 400)

            user_id = comment_user['Id']
            db_comment = Comment()
            old_comment = db_comment.get_by_id(id)
            if not old_comment:
                return send_return_response("Comment not found", 400)
            comment_user_id = old_comment['User_Id']
            if user_id != comment_user_id:
                return send_return_response("User not authorized to edit comment", 400)
            db_comment.update_comment(id, comment)

            return send_return_response('Comment edited', 200)

        except Exception as e:
            return send_return_response(str(e), 500)

    def delete(self):
        api_key = request.args.get('key')
        api_secret = request.args.get('secret')
        id = request.args.get('id')
        email = request.args.get('email')
        url = request.url

        api_user = ApiUser()
        if not api_user.is_valid_api_user(api_key, api_secret):
            return send_return_response("Bad API Credentials", 400)

        if id is None:
            return send_return_response('Comment ID is not valid', 400)
        if not id.isdigit():
            return send_return_response('Comment ID is not valid', 400)

        try:
            user = User()
            comment_user = user.get_by_email(email)

            if not comment_user:
                return send_return_response("User not found", 400)

            now = datetime.now()
            if not is_user_allowed_post_comment(comment_user, now, MAX_TIME_LOGIN):
                return send_return_response("User not logged in or verified", 400)

            user_id = comment_user['Id']
            db_comment = Comment()
            old_comment = db_comment.get_by_id(id)
            comment_user_id = old_comment['User_Id']
            if user_id != comment_user_id:
                return send_return_response("User not authorized to delete comment", 400)
            db_comment.delete_comment(id)

            return send_return_response('Comment deleted', 200)

        except Exception as e:
            return send_return_response(str(e), 500)


class GetAllUsers(Resource):
    def get(self):
        user = User()
        users = user.get_all_users()
        return jsonify(users)


class GetUserByEmail(Resource):
    def get(self):
        email = request.args.get('email')
        user = User()
        return jsonify(user.get_by_email(email))


class GetUserById(Resource):
    def get(self):
        id = int(request.args.get('id'))
        user = User()
        return jsonify(user.get_by_id(id))


class GetDoctorsByRadius(Resource):
    def get(self):
        api_key = request.args.get('key')
        api_secret = request.args.get('secret')
        postal_code = request.args.get('postalcode')
        radius_miles = int(request.args.get('radius'))
        api_user = ApiUser()
        start_time0 = datetime.now()
        if not api_user.is_valid_api_user(api_key, api_secret):
            return "Bad API Credentials"
        stop_time0 = datetime.now()
        print(str('Time to authorize API Key & Secret: {}').format(stop_time0 - start_time0))
        pc = Postalcodes()
        start_time1 = datetime.now()
        zips = pc.get_all_by_radius(postal_code, radius_miles)
        stop_time1 = datetime.now()
        tested_zip_codes = zips['tested_zip_codes']
        zips_distance = zips['zips_distance']
        print(str('Time to get zips: {}, count: {}').format(stop_time1 - start_time1, len(zips_distance)))
        doc = Provider()
        start_time2 = datetime.now()
        docs = doc.get_all_by_zips(tested_zip_codes)
        stop_time2 = datetime.now()
        print(str('Time to get docs: {}, count: {}').format(stop_time2 - start_time2, len(docs)))
        doc_list = []
        start_time3 = datetime.now()
        for doc in docs:
            docs[doc].update({"Distance": round(zips_distance[docs[doc]["PostalCode"]], 2)})
            doc_list.append(docs[doc])
        stop_time3 = datetime.now()
        print(str('Time to add distance to docs: {}, count: {}').format(stop_time3 - start_time3, len(doc_list)))
        print(str('Total time: {}').format(stop_time3 - start_time0))

        results = sorted(doc_list, key=itemgetter('Distance'))
        return jsonify({'Providers': results})


class GetDoctorByTaxonomy(Resource):
    def get(self):
        taxonomy = request.args.get('taxonomy')
        doc = Provider()
        doc_result = doc.get_by_taxonomy(taxonomy)
        return jsonify(doc_result)


api.add_resource(Welcome, '/')
api.add_resource(GetAllUsers, '/GetAllUsers/')
api.add_resource(GetDoctorsByRadius, '/GetByRadius/')
api.add_resource(GetDoctorByTaxonomy, '/GetDoctorByTaxonomy/')
api.add_resource(GetUserByEmail, '/GetUserByEmail/')
api.add_resource(GetUserById, '/GetUserById/')
api.add_resource(ApiUserRegister, '/ApiUserRegister/')
api.add_resource(UserRegister, '/UserRegister/')
api.add_resource(UserLogin, '/UserLogin/')
api.add_resource(Practitioners, '/Practitioners/')
api.add_resource(PractitionersByName, '/PractitionersByName/')
api.add_resource(PractitionersByNpi, '/PractitionersByNpi/')
api.add_resource(Comments, '/Comments/')


if __name__ == '__main__':
    app.run(debug=True)
