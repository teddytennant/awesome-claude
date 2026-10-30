import os,re,sys,collections
R,SRC,S=sys.argv[1:4]
files=[os.path.join(r,f) for r,_,fs in os.walk(f'{R}/claudecode') for f in fs if f.endswith('.md')]
specs=[f for f in files if '/specs/' in f]
print('md files',len(files),'specs',len(specs),'words',sum(len(open(f).read().split()) for f in files))
print(collections.Counter(f.split('/specs/')[1].split('/')[0] for f in specs))
# format
miss=collections.Counter()
for f in specs:
    t=open(f).read()
    for k in ['**Status:**','**Provenance:**','**Sources:**','## Purpose','## Changes since the snapshot']:
        if k not in t: miss[k]+=1; print('MISSING',k,f[len(R):])
# versions
cl=set(re.findall(r'^## (\d+\.\d+\.\d+)',open(f'{S}/pub/CHANGELOG.md').read(),re.M))
bad=collections.Counter()
for f in specs:
    for v in re.findall(r'(?<![\d.])v?(2\.\d+\.\d+)(?![\d])',open(f).read()):
        if v not in cl: bad[v]+=1
print('uncited-versions',bad.most_common(20))
# links
br=[]
for f in files:
    for l in re.findall(r'\]\((?!http)([^)#]+\.md)',open(f).read()):
        if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(f),l))): br.append((f[len(R):],l))
print('broken',br[:15],len(br))
# verbatim overlap: 14-word shingles
tok=lambda s:re.findall(r"[A-Za-z0-9_']+",s.lower())
sh=set(); N=14
for r,_,fs in os.walk(SRC):
    if '.git' in r: continue
    for f in fs:
        if f.endswith(('.ts','.tsx')):
            w=tok(open(os.path.join(r,f),errors='ignore').read())
            sh.update(hash(tuple(w[i:i+N])) for i in range(len(w)-N+1))
hits=[]
for f in specs:
    w=tok(open(f).read()); c=0;ex=None
    for i in range(len(w)-N+1):
        if hash(tuple(w[i:i+N])) in sh: c+=1; ex=ex or ' '.join(w[i:i+N])
    if c: hits.append((c,f[len(R):],ex))
print('overlap',sorted(hits,reverse=True)[:15])
# code fences
print('fenced code lines ts-like', sum(len(re.findall(r'```(ts|tsx|typescript|javascript|js)\b',open(f).read())) for f in specs))
