from __future__ import absolute_import

# Python imports
import random
from datetime import timedelta

# Django imports
from testdjango.models import Pokemon

# RabbitMQ imports
from testdjango.celery import celery
from celery.task.schedules import crontab
from celery.decorators import periodic_task

#@celery.task
@periodic_task(run_every=timedelta(seconds=1))
def make_pokemon():
    first = ['Tiny', 'Small', 'Little', 'Big', 'Giant', 'Skinny', 'Chubby', 'Tall', 'Short', 'Super', 'Ultra', 'Mega']
    second = ['fire', 'water', 'sand', 'air', 'wind', 'grass', 'leaf', 'tree', 'rock', 'stone']
    third = ['cat', 'dog', 'rat', 'bird', 'horse', 'pig', 'cow', 'chicken', 'lion', 'tiger', 'wolf', 'deer', 'hippopotamus', 'octopus', 'squid', 'fish', 'shark', 'meerkat', 'lemur']
    i1 = random.randint(0, len(first)-1)
    i2 = random.randint(0, len(second)-1)
    i3 = random.randint(0, len(third)-1)
    poke_name = first[i1] + second[i2] + third[i3] + 'mon'

    poke_num = random.randint(1, 9999)

    types = ['Fire', 'Water', 'Electric', 'Grass', 'Rock', 'Ground', 'Fighting', 'Poison', 'Ghost', 'Psychic', 'Bug', 'Flying', 'Ice', 'Dragon', 'Dark', 'Steel', 'Normal']
    poke_type = types[random.randint(0, len(types)-1)]

    new_pokemon = Pokemon(name=poke_name, number=poke_num, type=poke_type)
    new_pokemon.save()
    return new_pokemon
  

