# Python imports
import urllib2
import json

# Django imports
from django.http import HttpResponse
from django.shortcuts import render_to_response
from testdjango.models import FacebookUser

def add_user(request):
    errors = []
    if 'q_user' in request.GET:
        q = request.GET['q_user']
        if not q:
            errors.append('Enter a search term.')
        if len(errors) != 0:
            return render_to_response('add_user_form.html', {'errors': errors})
        else:
            facebook_data = retrieve_facebook_user_data(q)
            if type(facebook_data) is str and 'Error:' in facebook_data:
                return render_to_response('add_user_form.html', {'httperror': facebook_data})
            elif type(facebook_data) is dict:
                add_user_to_db(facebook_data)
                return render_to_response('add_user_form.html', {'success': True})
            else:
                return render_to_response('add_user_form.html')
    else:
        return render_to_response('add_user_form.html')

def show_all_users(request):
    html = "<html><body><b>ID::Name::Username</b><br>"
    users = FacebookUser.objects.all()
    for user in users:
        html += "<li>%d::%s::%s<br>" % (user.id, user.name, user.username)
    html += "</body></html>"
    return HttpResponse(html)

def show_user_info(request, input_name):
    all_usernames = map(lambda x: x['username'].lower(), FacebookUser.objects.all().values('username'))
    if input_name.lower() in all_usernames:
        facebook_user = FacebookUser.objects.get(username__iregex=r"(%s)" % input_name)
        html = "<html><body>"
        for column in FacebookUser._meta.fields:
            html += "%s: %s<br>" % (column.name, getattr(facebook_user, column.name))
        html += "</body></html>"
    else:
        html = "<html><h1>User not found!</h1></html>"
    return HttpResponse(html)

# Helper functions

def retrieve_facebook_user_data(input_name):
    base_url = 'http://graph.facebook.com/%s'
    try:
        response = urllib2.urlopen(base_url % input_name)
        return json.loads(response.read())
    except urllib2.HTTPError, e:
        return "Error: Either could not connect to Facebook or user was not found."
    except ValueError, e:
        return "Error: JSON could not be decoded. Maybe you were redirected to another page."

def add_user_to_db(facebook_data):
    all_columns = FacebookUser._meta.fields
    facebook_user = FacebookUser()
    for column in all_columns:
        if column.name in facebook_data:
            setattr(facebook_user, column.name, facebook_data[column.name])
    facebook_user.save()
