from settings import *
from model_mapping_functions import *
from distance_functions import *
from sqlalchemy.ext.automap import automap_base
from validation_helpers import *

'''Must be before mapping classes'''
Base = automap_base()

'''Alternate method, does not allow for adding methods'''
# User = Base.classes.users
# Provider = Base.classes.providers

npi_list = [1679576722, 1588667638, 1497758544, 1306849450, 1215930367, 1023011178, 1932102084, 1841293990, 1750384806,
            1669475711, 1992709968, 1992709950, 1992709943, 1992709935, 1992709976, 1992709968, 1992709950]

# query = db.query(Provider).filter(Provider.NPI.in_(npi_list)).all()


class User(Base):
    __tablename__ = 'users'

    def get_id_by_email(self, email):
        user = db.session.query(User).filter_by(Email=email).first().Id
        db.session.close()
        return user

    def get_by_id(self, id):
        user = make_user_dict(db.session.query(User).filter_by(Id=id).first())
        db.session.close()
        return user

    def get_by_email(self, email):
        user = make_user_dict(db.session.query(User).filter_by(Email=email).first())
        db.session.close()
        return user

    def get_all_users(self):
        user = make_users(db.session.query(User).all())
        db.session.close()
        return user

    def add_user(self, user):
        db.session.add(user)
        db.session.commit()
        db.session.close()

    def verify_user(self, code):
        user = db.session.query(User).filter_by(VerifyUUID=code).first()
        if user:
            user.Verified = True
            db.session.commit()
            db.session.close()
            return True
        else:
            return False

    def login_user(self, email, password, dt):
        user = db.session.query(User).filter_by(Email=email).first()
        if user:
            hashed_password = user.Password
            if check_password(hashed_password, password):
                user.LoginTime = dt
                user.LoggedIn = True
                db.session.commit()
                db.session.close()
                return True
        else:
            return False

    def is_email_available(self, email):
        if not check_email(email):
            return False
        api_user = db.session.query(User).filter_by(Email=email).first()
        db.session.close()
        if not api_user:
            return True
        else:
            return False


class ApiUser(Base):
    __tablename__ = 'apiusers'

    def is_valid_api_user(self, api_key, api_secret):
        if not is_uuid_good(api_key):
            return False
        if not is_uuid_good(api_secret):
            return False
        api_user = db.session.query(ApiUser).filter_by(ApiKey=api_key, ApiSecret=api_secret).first()
        if not api_user:
            return False
        api_user.ApiCalls += 1
        db.session.commit()
        db.session.close()
        return True

    def is_api_email_available(self, email):
        if not check_email(email):
            return False
        api_user = db.session.query(ApiUser).filter_by(Email=email).first()
        db.session.close()
        if not api_user:
            return True
        else:
            return False

    def create_api_user(self, api_user):
        db.session.add(api_user)
        db.session.commit()
        db.session.close()


class Provider(Base):
    __tablename__ = 'providers'

    def get_by_npi(self, npi):
        doc = make_provider(db.session.query(Provider).filter_by(NPI=npi).first())
        db.session.close()
        return doc

    def get_all_by_npi(self, npi_list):
        docs = make_providers(db.session.query(Provider).filter(Provider.NPI.in_(npi_list)).all())
        db.session.close()
        return docs

    def get_all_by_zip(self, zip):
        providers_results = db.session.query(Provider, Comment).outerjoin(Comment, Comment.NPI == Provider.NPI) \
            .filter(Provider.PostalCode == zip).all()
        providers = make_providers_from_join(providers_results)
        db.session.close()
        return providers

    def get_all_by_zip_and_taxonomy(self, zip, taxonomy):
        providers_results = db.session.query(Provider, Comment).outerjoin(Comment, Comment.NPI == Provider.NPI) \
            .filter(Provider.PostalCode == zip, Provider.Taxonomy1 == taxonomy).all()
        providers = make_providers_from_join(providers_results)
        db.session.close()
        return providers

    def get_all_by_zips(self, zip_list):
        # return make_providers(db.session.query(Provider).filter(Provider.PostalCode.in_(zip_list)).all())
        providers_results = db.session.query(Provider, Comment).outerjoin(Comment, Comment.NPI == Provider.NPI)\
            .filter(Provider.PostalCode.in_(zip_list)).all()
        print(str(len(providers_results)))
        providers = make_providers_from_join(providers_results)
        db.session.close()
        return providers

    def get_all_by_zips_and_taxonomy(self, zip_list, taxonomy):
        # return make_providers(db.session.query(Provider).filter(Provider.PostalCode.in_(zip_list)).all())
        providers_results = db.session.query(Provider, Comment).outerjoin(Comment, Comment.NPI == Provider.NPI)\
            .filter(Provider.PostalCode.in_(zip_list), Provider.Taxonomy1 == taxonomy).all()
        print(str(len(providers_results)))
        providers = make_providers_from_join(providers_results)
        db.session.close()
        return providers

    def get_by_taxonomy(self, taxonomy):
        provider_result = db.session.query(Provider, Comment).outerjoin(Comment, Comment.NPI == Provider.NPI)\
            .filter(Provider.Taxonomy1 == taxonomy).all()
        provider = make_providers_from_join(provider_result)
        db.session.close()
        return provider

    def get_all_by_zip_and_fullname(self, zip, firstname, lastname):
        providers_results = db.session.query(Provider, Comment).outerjoin(Comment, Comment.NPI == Provider.NPI) \
            .filter(Provider.PostalCode == zip, Provider.Firstname == firstname, Provider.Lastname == lastname).all()
        providers = make_providers_from_join(providers_results)
        db.session.close()
        return providers

    def get_all_by_zips_and_fullname(self, zip_list, firstname, lastname):
        providers_results = db.session.query(Provider, Comment).outerjoin(Comment, Comment.NPI == Provider.NPI) \
            .filter(Provider.PostalCode.in_(zip_list), Provider.Firstname == firstname, Provider.Lastname == lastname).all()
        print(str(len(providers_results)))
        providers = make_providers_from_join(providers_results)
        db.session.close()
        return providers

    def get_all_by_zip_and_lastname(self, zip, lastname):
        providers_results = db.session.query(Provider, Comment).outerjoin(Comment, Comment.NPI == Provider.NPI) \
            .filter(Provider.PostalCode == zip, Provider.Lastname == lastname).all()
        providers = make_providers_from_join(providers_results)
        db.session.close()
        return providers

    def get_all_by_zips_and_lastname(self, zip_list, lastname):
        providers_results = db.session.query(Provider, Comment).outerjoin(Comment, Comment.NPI == Provider.NPI) \
            .filter(Provider.PostalCode.in_(zip_list), Provider.Lastname == lastname).all()
        print(str(len(providers_results)))
        providers = make_providers_from_join(providers_results)
        db.session.close()
        return providers


class Comment(Base):
    __tablename__ = 'comments'

    def get_by_id(self, id):
        comment = make_comment_dict(db.session.query(Comment).filter_by(Id=id).first())
        db.session.close()
        return comment

    def get_all_by_npi(self, npi):
        comments = db.session.query(Comment).filter_by(NPI=npi).all()
        db.session.close()
        return make_comments(comments)

    def add_comment(self, comment):
        db.session.add(comment)
        db.session.commit()
        db.session.close()

    def update_comment(self, id, updated_comment):
        old_comment = db.session.query(Comment).get(id)
        old_comment.Comment = updated_comment
        db.session.commit()
        db.session.close()

    def delete_comment(self, id):
        db.session.query(Comment).filter_by(Id=id).delete()
        # db.session.remove(old_comment)
        db.session.commit()
        db.session.close()


class Postalcodes(Base):
    __tablename__ = 'postalcodes'

    def get_by_zip(self, zip):
        zc = make_zip_dict(db.session.query(Postalcodes).filter_by(ZipCode=zip).first())
        db.session.close()
        return zc

    def get_all_by_list(self, zips_list):
        zcs = make_zips((db.session.query(Postalcodes).filter(Postalcodes.ZipCode.in_(zips_list)).all()))
        db.session.close()
        return zcs

    def get_all_by_radius(self, zip, radius):
        zip_code = db.session.query(Postalcodes).filter_by(ZipCode=zip).first()
        distance_query = build_zip_query(zip_code, miles_to_km(radius))
        zip_rows = db.session.execute(distance_query).fetchall()
        tested_zip_codes = []
        zips_distance = dict()
        if len(zip_rows) == 0:
            zips_distance.update({zip: 0})
            tested_zip_codes.append(zip)
        else:
            for each_zip in zip_rows:
                zips_distance.update({each_zip[1]: km_to_miles(each_zip[7])})
                tested_zip_codes.append(each_zip[1])

        return_dict = {'tested_zip_codes': tested_zip_codes, 'zips_distance': zips_distance}
        db.session.close()
        return return_dict

'''Must be after mapping classes'''
Base.prepare(db.engine, reflect=True)
