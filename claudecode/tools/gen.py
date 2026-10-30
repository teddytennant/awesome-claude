import json,re,collections,os,sys
S,REPO,SRC=sys.argv[1:4]
P=f'{S}/pub'; OUT=f'{REPO}/claudecode'
t=json.load(open(f'{P}/npm.json'))['time']
key=lambda v:tuple(int(x) for x in v.split('.'))
txt=open(f'{P}/CHANGELOG.md').read()
vers=[]
for p in re.split(r'^## ',txt,flags=re.M)[1:]:
    h,_,b=p.partition('\n'); v=h.split()[0]
    if key(v)<(2,1,89): continue
    bl=[l[2:].strip() for l in b.split('\n') if l.startswith('- ')]
    vers.append((v,t[v][:10],bl))
vers.sort(key=lambda r:key(r[0]))
TOP=[('agents',r'subagent|sub-agent|agent team|teammate|background (agent|session|task)|/agents|\bfork|workflow|ultracode|orchestrat|\bAgent tool|worktree'),
('hooks',r'\bhooks?\b|PreToolUse|PostToolUse|SessionStart|Stop hook'),
('mcp',r'\bMCP\b|elicitation|connector'),
('plugins-skills',r'plugin|marketplace|\bskills?\b|slash command'),
('permissions-sandbox',r'permission|sandbox|auto mode|allowlist|denylist|bypass|allowedTools|disallowed'),
('ide',r'^\[VSCode\]|VS ?Code|JetBrains|Cursor|\bIDE\b'),
('cloud-remote',r'^\[Cloud|^\[Code|Remote Control|remote control|teleport|routine|claude\.ai/code|/schedule|ultraplan|ultrareview|Self-hosted|\bcron\b|artifact'),
('sdk-headless',r'\bSDK\b|headless|--print|\b-p\b|stream-json|--output-format|\bCI\b'),
('models-providers',r'\bmodel\b|Opus|Sonnet|Haiku|Fable|Bedrock|Vertex|Foundry|gateway|ANTHROPIC_|effort|thinking|fast mode|/fast|OAuth|login|proxy|mTLS|prompt cach|1M'),
('memory-context',r'CLAUDE\.md|memory|compact|context|session|resume|/rewind|checkpoint|transcript'),
('tools',r'\bBash\b|\bRead\b|\bEdit\b|\bWrite\b|\bGrep\b|\bGlob\b|PowerShell|\bLSP\b|WebFetch|WebSearch|Monitor|notebook'),
('enterprise-telemetry',r'managed|policy|OTEL|OpenTelemetry|telemetry|enterprise|audit'),
('tui-input',r'fullscreen|statusline|status line|keybind|theme|\bvim\b|voice|render|terminal|tmux|prompt input|autocomplete|paste|spinner|/[a-z-]+'),
('install-update',r'install|update|upgrade|Windows|Linux|macOS|Homebrew|WinGet|native'),]
isfix=lambda b:bool(re.match(r'(\[[^\]]+\]\s*)?(\w+:\s*)?(Fixed|Fix)\b',b))
def topic(b):
    for n,r in TOP:
        if re.search(r,b): return n
    return 'other'
months=collections.defaultdict(list); topics=collections.defaultdict(list); stat=collections.Counter(); nf=nb=0
for v,d,bl in vers:
    months[d[:7]].append((v,d,bl))
    for b in bl:
        nb+=1
        if isfix(b): continue
        nf+=1; tp=topic(b); topics[tp].append((v,d,b)); stat[tp]+=1
for m,rows in sorted(months.items()):
    o=[f'# Claude Code releases — {m}\n','Non-fix changelog entries, quoted from the public changelog. Each heading gives the version, its npm publish date, and how many fix entries were left out.\n']
    for v,d,bl in reversed(rows):
        fs=[b for b in bl if not isfix(b)]
        o.append(f'## {v} — {d} ({len(fs)} entries, {len(bl)-len(fs)} fixes omitted)\n')
        o+= [f'- `{topic(b)}` {b}' for b in fs]+['']
    open(f'{OUT}/releases/{m}.md','w').write('\n'.join(o))
os.makedirs(f'{S}/topic',exist_ok=True)
for tp,rows in topics.items():
    open(f'{S}/topic/{tp}.md','w').write('\n'.join(f'{v} ({d}): {b}' for v,d,b in rows))
o=['# Post-leak release log\n',f'Coverage: **{len(vers)} versions**, {vers[0][0]} ({vers[0][1]}) through {vers[-1][0]} ({vers[-1][1]}). The public changelog has {nb} entries for this range: {nf} kept here and {nb-nf} fixes omitted.\n','Entries are classified by a first-match keyword rule, so a topic tag is a filing aid and can be wrong for an individual entry.\n','| Month | Versions | Kept entries |','|---|---|---|']
for m,rows in sorted(months.items()):
    o.append(f'| [{m}]({m}.md) | {len(rows)} | {sum(1 for r in rows for b in r[2] if not isfix(b))} |')
o+=['','| Topic | Kept entries |','|---|---|']+[f'| `{k}` | {c} |' for k,c in stat.most_common()]
open(f'{OUT}/releases/README.md','w').write('\n'.join(o)+'\n')
print(len(vers),nb,nf,stat.most_common())
