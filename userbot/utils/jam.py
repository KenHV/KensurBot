import time
from time import gmtime, mktime
import datetime
from datetime import datetime

def clock():
  wib = 7 * 60 * 60 #GMT+7
  now_utc = datetime.utcnow()
  base_utc = datetime(1970, 1, 1)
  time_delta = now_utc - base_utc
  time_delta = time_delta.total_seconds()
  time_delta = time_delta + wib
  asem = datetime.fromtimestamp(mktime(gmtime(time_delta)))
  return asem
