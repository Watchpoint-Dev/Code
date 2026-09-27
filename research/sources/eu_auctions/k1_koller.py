import sys,pathlib,re
from watchpoint.commun.utils import get
S=pathlib.Path("samples")
for name,u in [("robots_koller_retry.txt","https://www.kollerauktionen.ch/robots.txt"),
               ("robots_kollerauctions.txt","https://www.kollerauctions.com/robots.txt")]:
    try:
        r=get(u,pause=3.0); print(name,r.status_code,r.url,len(r.text),r.headers.get("server"))
        (S/name).write_text(r.text,encoding="utf-8")
        print("   ",r.text[:400].replace("\n"," | "))
    except Exception as e: print(name,"ERR",repr(e)[:150])
