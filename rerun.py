import os
import time
os.popen("pkill -9 -f usr/local/bin/uvicorn")
time.sleep(3)
os.popen("uvicorn server:app --host 0.0.0.0 --port 8009")
#os.popen("uvicorn main:app --host 0.0.0.0 --port 8000 --ssl-keyfile link-ify.space/privkey.pem --ssl-certfile link-ify.space/fullchain.pem")
exit(0)