from __future__ import absolute_import

# Python imports
import urllib2
import json
from datetime import timedelta

# Django imports
from testdjango.facebookgraph.models import FacebookUser

# RabbitMQ imports
from celery.task.schedules import crontab
from celery.decorators import periodic_task

@periodic_task(run_every=crontab(minute="*/10"))
#@periodic_task(run_every=timedelta(seconds=3))
def sync_database():
    base_url = 'http://graph.facebook.com/%s'
    all_facebook_users = FacebookUser.objects.all()
    all_columns = FacebookUser._meta.fields
    for facebook_user in all_facebook_users:
        try:
            response = urllib2.urlopen(base_url % facebook_user.username)
            json_response = json.loads(response.read())
            for column in all_columns:
                if column.name in json_response:
                    setattr(facebook_user, column.name, json_response[column.name])
            facebook_user.save()
        except urllib2.HTTPError:
            continue
    return True
