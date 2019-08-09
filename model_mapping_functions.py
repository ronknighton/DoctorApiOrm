def make_providers(docs):
    providers = []
    for doc in docs:
        providers.append(make_provider(doc))
    return providers


def make_providers_from_join(docs):
    providers_dict = dict()
    providers = []
    for doc in docs:
        if doc.Provider.NPI in providers_dict:
            if doc.Comment:
                providers_dict[doc.Provider.NPI]['Comments'].append(make_comment_dict(doc.Comment))
        else:
            providers_dict.update({doc.Provider.NPI: make_provider_from_join(doc)})

    return providers_dict


def make_users(users):
    user_list = []
    for user in users:
        user_list.append(make_user_dict(user))
    return user_list


def make_comments(comments):
    comment_list = []
    if len(comments) > 0:
        for comm in comments:
            comment_list.append(make_comment_dict(comm))
    return comment_list


def make_zips(zips):
    zip_list = []
    for zip in zips:
        zip_list.append(make_zip_dict(zip))
    return zip_list


def make_provider(doc):
    if doc:
        provider_dict = {
            'Id': doc.Id,
            'NPI': doc.NPI,
            'Organization': doc.Organization,
            'Lastname': doc.Lastname,
            'Firstname': doc.Firstname,
            'Address1': doc.Address1,
            'Address2': doc.Address2,
            'City': doc.City,
            'State': doc.State,
            'PostalCode': doc.PostalCode,
            'Phone': doc.Phone,
            'Taxonomy1': doc.Taxonomy1,
            'Taxonomy2': doc.Taxonomy2,
            'Comments': make_comments(doc.comment_collection)
        }
        return provider_dict
    else:
        return doc


def make_provider_from_join(doc):
    provider_dict = {
        'Id': doc.Provider.Id,
        'NPI': doc.Provider.NPI,
        'Organization': doc.Provider.Organization,
        'Lastname': doc.Provider.Lastname,
        'Firstname': doc.Provider.Firstname,
        'Address1': doc.Provider.Address1,
        'Address2': doc.Provider.Address2,
        'City': doc.Provider.City,
        'State': doc.Provider.State,
        'PostalCode': doc.Provider.PostalCode,
        'Phone': doc.Provider.Phone,
        'Taxonomy1': doc.Provider.Taxonomy1,
        'Taxonomy2': doc.Provider.Taxonomy2,
        'Comments': [make_comment_dict(doc.Comment)]
    }
    return provider_dict


def make_comment_dict(comm):
    if comm:
        comment_dict = {
            'Id': comm.Id,
            'NPI': comm.NPI,
            'Comment': comm.Comment,
            'Created': comm.Created,
            'User_Id': comm.User_Id
        }
        return comment_dict
    else:
        return comm


def make_user_dict(user):
    if user:
        user_dict = {
            'Id': user.Id,
            'Firstname': user.Firstname,
            'Lastname': user.Lastname,
            'Nickname': user.Nickname,
            'Email': user.Email,
            'LoginTime': user.LoginTime,
            'LoggedIn': user.LoggedIn,
            'Verified': user.Verified,
            'Comments': make_comments(user.comment_collection)
        }
        return user_dict
    else:
        return user


def make_zip_dict(zip_code):
    if zip_code:
        zip_dict = {
            'Id': zip_code.Id,
            'ZipCode': zip_code.ZipCode,
            'City': zip_code.City,
            'State': zip_code.State,
            'Latitude': zip_code.Latitude,
            'Longitude': zip_code.Longitude,
            'Timezone': zip_code.ZipCode
        }
        return zip_dict
    else:
        return zip_code


def make_provider_list_from_tuple(providers):
    doc_list = []
    for doc in providers:
        provider_dict = {
            'Id': doc[0],
            'NPI': doc[1],
            'Organization': doc[2],
            'Lastname': doc[3],
            'Firstname': doc[4],
            'Address1': doc[5],
            'Address2': doc[6],
            'City': doc[7],
            'State': doc[8],
            'PostalCode': doc[9],
            'Phone': doc[10],
            'Taxonomy1': doc[11],
            'Taxonomy2': doc[12]
        }
        doc_list.append(provider_dict)
    return doc_list
