
from datetime import datetime, timezone, timedelta
import pandas as pd
import time
    

m = 30 #set minutes delta
mh = m//2 #set halftime
now = datetime.now(timezone.utc)
start_time_1 = (now - timedelta(minutes=mh)).isoformat() #15 minutes ago
start_time_2 = (now - timedelta(minutes=m)).isoformat() #30 minutes ago

print(now)
print(start_time_1)
print(start_time_2)
print(timedelta(minutes=mh))
print(timedelta(minutes=m))
print(now)
print(now-timedelta(minutes=mh))
print(now-timedelta(minutes=m))