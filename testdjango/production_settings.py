DEBUG = False
TEMPLATE_DEBUG = False

DATABASES = {'default': dj_database_url.config(default='postgres://sqguvtgbcxghvw:GroOvsQuE8TMB_hZfuZMo7Dsn5@ec2-23-21-216-174.compute-1.amazonaws.com:5432/d4rens7jb901f0')}
BROKER_URL = 'amqp://app7168026_heroku.com:F_AF6puAqTqTS9Ezj_j3LF_NOwvB6Gxb@tiger.cloudamqp.com/app7168026_heroku.com'