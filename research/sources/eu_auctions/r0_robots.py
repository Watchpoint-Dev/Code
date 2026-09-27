import sys, pathlib, json
from watchpoint.commun.utils import get
S = pathlib.Path(__file__).resolve().parent / "samples"
targets = {
 "artcurial":"https://www.artcurial.com/robots.txt",
 "dorotheum":"https://www.dorotheum.com/robots.txt",
 "koller":"https://www.kollerauktionen.ch/robots.txt",
 "lempertz":"https://www.lempertz.com/robots.txt",
 "cortrie":"https://www.cortrie.de/robots.txt",
 "tajan":"https://www.tajan.com/robots.txt",
}
res={}
for k,u in targets.items():
    try:
        r=get(u,pause=2.5)
        (S/f"robots_{k}.txt").write_text(r.text,encoding="utf-8")
        res[k]={"status":r.status_code,"final":r.url,"len":len(r.text),"server":r.headers.get("server"),"ct":r.headers.get("content-type")}
    except Exception as e:
        res[k]={"error":repr(e)[:200]}
print(json.dumps(res,indent=1))
