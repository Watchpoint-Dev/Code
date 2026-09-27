import sys,socket,pathlib
from watchpoint.commun.utils import get
for h in ["kollerauktionen.ch","www.kollerauktionen.ch","www.kollerauctions.com"]:
    try: print("DNS",h,socket.gethostbyname_ex(h)[2])
    except Exception as e: print("DNS",h,"ERR",repr(e)[:100])
for u in ["https://kollerauktionen.ch/robots.txt","http://www.kollerauktionen.ch/robots.txt"]:
    try:
        r=get(u,pause=3.0,allow_redirects=True)
        print(u,r.status_code,r.url,len(r.text),dict(list(r.headers.items())[:6]))
        print("   ",r.text[:250].replace("\n"," | "))
    except Exception as e: print(u,"ERR",repr(e)[:150])
