import random
from requests import get

def aliv():
  xx = get('https://del.dog/raw/parakuy').json()
  result = random.choice(xx)
  return result
