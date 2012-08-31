from __future__ import absolute_import
from celery import Celery

celery = Celery('testdjango.celery',
                #broker='amqp://app7168026_heroku.com:F_AF6puAqTqTS9Ezj_j3LF_NOwvB6Gxb@tiger.cloudamqp.com/app7168026_heroku.com',
                broker='amqp://guest:guest@localhost:5672//',
                backend='ampq://',
                include=['testdjango.tasks'])

if __name__ == '__main__':
    celery.start()
