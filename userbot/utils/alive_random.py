import random
from requests import get

def alive():
  xx = get('https://del.dog/raw/parakuy').json()
  result = random.choice(xx)
  return result
