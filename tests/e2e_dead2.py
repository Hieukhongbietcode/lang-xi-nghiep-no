# Tu dong chep tu bo test cua quan tro (chay tren GitHub Actions)
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))
try:
    import pw as _pw
    class pw:  # phuc vu thu vien CDN khi KHONG co mang (may nguoi viet test); tren GitHub co mang that
        route = staticmethod(_pw.route)
except Exception:
    class pw:
        @staticmethod
        def route(r): r.continue_()
from playwright.sync_api import sync_playwright
WS='ws://localhost:8787'
p=sync_playwright().start(); b=p.chromium.launch(); errs=[]
def ctx(w=390,h=844):
    c=b.new_context(viewport={'width':w,'height':h}); pg=c.new_page(); pg.route('**/*', pw.route); pg.on('dialog', lambda d: d.accept()); pg.on('pageerror', lambda e: errs.append(str(e)[:200])); return c,pg
ok=lambda c,m: print(('  ✅ ' if c else '  ❌ ')+m)
gc,gm=ctx(1300,860)
gm.goto('file://'+ROOT+f'/index.html?ws={WS}', wait_until='load', timeout=180000); gm.wait_for_timeout(900)
gm.locator('#btn-online-home').click(); gm.wait_for_timeout(1500); link=gm.locator('.ol-link span').inner_text()
link='file://'+ROOT+'/play.html?'+link.split('?',1)[1]+'&ws='+WS
names=['Một','Hai','Ba','Bốn','Năm','Sáu','Bảy']; P={}
for n in names:
    c,pg=ctx(); pg.goto(link); pg.wait_for_timeout(300); pg.fill('#in-name',n); pg.locator('#btn-join').click(); pg.wait_for_timeout(300); P[n]=pg
c,sp=ctx(); sp.goto(link); sp.wait_for_timeout(300); sp.fill('#in-name','Khoa'); sp.locator('#btn-spec').click(); sp.wait_for_timeout(800)
gm.locator('#online-foot .ol-btn.main').click(); gm.wait_for_timeout(900)
gm.evaluate("()=>{ROLES_DB.forEach(r=>state.deck[r.id]=0); Object.assign(state.deck,{wolf:1,seer:1,guard:1,ghost:1,villager:3}); renderDeck();}")
gm.locator('#view-deck .bottom-safe button').last.click(); gm.wait_for_timeout(1000)
if gm.locator('#deck-warn-modal:not(.hidden)').count(): gm.locator('#deck-warn-modal button').last.click(); gm.wait_for_timeout(500)
asg=gm.evaluate("()=>state.dealAssignment")
gm.evaluate("()=>{Object.keys(state.dealAssignment).forEach(n=>state.dealViewed[n]=1); onlineSaveDeal(); renderDealView();}")
gm.locator('#btn-deal-start').click(); gm.wait_for_timeout(800)
if gm.locator('#deal-warn-overlay').count(): gm.locator('#deal-warn-overlay button', has_text='Vẫn bắt đầu').click(); gm.wait_for_timeout(400)
gm.wait_for_timeout(1300); [x.click() for x in gm.locator('.tk-ov .tk-close').all()]
G=[n for n in names if asg[n]=='guard'][0]; M=[n for n in names if asg[n]=='ghost'][0]; V=[n for n in names if asg[n]=='villager']; D=V[0]
gm.evaluate(f"""()=>{{ state.players=Object.entries(state.dealAssignment).map(([n,r],i)=>({{id:'p_'+i,name:n,roleId:r,initialRoleId:r,isAlive:!(n==='{D}'||n==='{M}'),
   deathInfo:(n==='{D}'?{{day:1,phase:'Đêm',reason:'Bị Sói cắn'}}:(n==='{M}'?{{day:1,phase:'Đêm',reason:'Bị Sói cắn'}}:null))}}));
   state.eventLog=[{{title:'Đêm 1',content:'Sói cắn {D}'}}]; state.dayCount=2; state.nightResume=null; startNightPhase(); }}"""); gm.wait_for_timeout(800)
seq=gm.evaluate("()=>state.nightSequence.map(s=>(s.role&&s.role.id)||s.type)"); print('   dem 2:', seq)
gm.evaluate("()=>{state.currentStepIndex=state.nightSequence.findIndex(s=>s.role&&s.role.id==='guard');renderNightStep();}"); gm.wait_for_timeout(2500)
for n in names: P[n].evaluate("()=>document.querySelectorAll('.sky-ov,.death-ov').forEach(x=>x.remove())")
pd, pm = P[D], P[M]
# 2. Con Ma
ok(pm.evaluate("()=>revealData")==None and pm.locator('#ring .rrole').count()==0, f'2. Con Ma ({M}) da chet: KHONG thay vai, KHONG nhat ky')
ok(not pm.evaluate("()=>!!can.dead"), '2. Con Ma KHONG vao phong Nguoi chet (khong ai mach duoc)')
ok(pm.locator('#conma-bar').is_visible() and not pm.evaluate("()=>document.body.classList.contains('ghost')") and pm.locator('#role-bar').is_visible(), '2. Con Ma: thanh rieng "van dang choi cho phe Dan", khong xam, van co thanh vai')
# 1 + 6 + 7 + 5
lab=pd.evaluate("()=>{ const l=document.querySelector('#ring .rrole'); const av=document.querySelector('#ring .seat .av'); return [getComputedStyle(l).color, getComputedStyle(l).filter, getComputedStyle(av).filter, getComputedStyle(document.getElementById('ring-box')).filter] }")
ok('grayscale' in lab[2] and lab[3]=='none' and lab[0] not in ('rgb(128, 128, 128)',), f'1. nguoi chet: hinh dai dien xam, CHU TEN VAI GIU MAU ({lab[0]})')
ok(not pd.locator('#role-bar').is_visible(), '6. nguoi chet: khong con thanh vai cua minh')
gb=pd.locator('.ghost-bar').inner_text()
ok('Bị Sói cắn — Đêm 1' in gb, '7. ly do chet: "'+(gb.split(chr(10))[1] if chr(10) in gb else gb)[:40]+'"')
ok('Còn lại:' in gb and 'Sói' in gb and 'Dân' in gb, '5. tom tat: "'+[l for l in gb.split(chr(10)) if 'Còn lại' in l][0]+'"')
# 3. theo dõi đêm trực tiếp
pg_=P[G]; pg_.locator(f'#ring .seat[data-n="{V[1]}"]').click(); pg_.wait_for_timeout(300); pg_.locator('#pf-ok').click(); pg_.wait_for_timeout(2600)
nf=pd.evaluate("()=>revealData && revealData.night && revealData.night.items.map(x=>x.who+'>'+(x.targets||[]).join(','))")
ok(nf and any('Bảo Vệ>'+V[1] in x for x in nf), f'3. dem nay (truc tiep): {nf}')
ok(pd.locator('#ring .dead-arr').count()>=1, '3. mui ten Bao Ve -> '+V[1]+' tren vong lang cua nguoi chet')
ok('Bảo Vệ' in pd.locator('.ghost-bar .gb-feed').inner_text(), '3. thanh Linh hon: "'+pd.locator('.ghost-bar .gb-feed').inner_text()+'"')
ok(pm.evaluate("()=>revealData")==None and P[V[2]].evaluate("()=>revealData")==None, '3. Con Ma va nguoi song KHONG nhan "dem nay"')
pd.locator('.ghost-bar .rev-btn').click(); pd.wait_for_timeout(300); pd.locator('#rv-night').click(); pd.wait_for_timeout(300)
ok('Bảo Vệ' in pd.locator('#rev-body').inner_text(), '3. tab "Dem nay" trong bang')
pd.screenshot(path=os.path.join(__import__('tempfile').gettempdir(), 'dead2.png')); pd.keyboard.press('Escape')
# 2. tới lượt Con Ma: khung viết chữ hiện, không bị che
gm.evaluate("()=>{state.currentStepIndex=state.nightSequence.findIndex(s=>s.role&&s.role.id==='ghost');renderNightStep();}"); gm.wait_for_timeout(2500)
pm.evaluate("()=>document.querySelectorAll('.sky-ov,.death-ov').forEach(x=>x.remove())")
print('   DEBUG Con Ma luc toi luot:', pm.evaluate("()=>({fields: fieldsMsg && fieldsMsg.fields.map(f=>f.kind||'pick'), turn: can.turn, dm: can.dm, ghostL: typeof ghostL!=='undefined' ? ghostL : null, visible: [...document.querySelectorAll('#pick-bar, [id*=ghost], [class*=ghost-]')].filter(e=>e.offsetParent).map(e=>e.id||e.className).slice(0,6)})"), '| GM dm:', gm.evaluate("()=>(window._gmPermNames||{}).dm"))
ok(pm.locator('#pick-bar:not(.hidden)').count()==1 and pm.locator('#pick-bar').is_visible() and pm.locator('#night-dim.on').count()==0, '2. toi luot Con Ma: khung viet chu HIEN, khong bi man toi hay man xam che')
# 8. khán giả
ok(sp.evaluate("()=>revealData")==None, '8. cong tac TAT: khan gia khong thay vai')
gm.evaluate("()=>{ gmOpts.specReveal=true; gmOptsSave(); }"); gm.wait_for_timeout(2600)
print('   DEBUG khan gia:', sp.evaluate("()=>({rev: revealData && revealData.roles.length, body: document.body.className, phase, gphase: gstatus && gstatus.phase, bar: !!document.getElementById('spec-bar'), barDisp: document.getElementById('spec-bar') && getComputedStyle(document.getElementById('spec-bar')).display})"))
print('   DEBUG roster.spec:', gm.evaluate("()=>window._onlineRoster && window._onlineRoster.spec"), '| da gui:', gm.evaluate("()=>Object.keys(_revSent2)"), '| khan gia me:', sp.evaluate("()=>me && {id:me.id, spec:me.spec}"))
ok(sp.evaluate("()=>!!revealData && revealData.roles.length")==7 and sp.locator('#spec-bar .rev-btn').is_visible(), '8. BAT cong tac: khan gia thay vai + nut "Vai & nhat ky"')
# 4. đoán phe thắng
pd.locator('.ghost-bar .pd-chip', has_text='Sói').click(); sp.locator('#spec-bar .pd-chip', has_text='Dân').click(); gm.wait_for_timeout(800)
pr=gm.evaluate("()=>state.online.predict"); ok(pr.get(D)=='wolf' and pr.get('Khoa')=='villager', f'4. du doan da gui ve quan tro: {pr}')
gm.evaluate("()=>{ state.gameOver=true; state.gameResult='PHE SÓI THẮNG!'; switchView('view-end'); }"); gm.wait_for_timeout(3000)
res=pd.locator('#g-end .pd-res').inner_text() if pd.locator('#g-end .pd-res').count() else '-'
ok(D in res and 'Khoa' not in res and 'Phe Sói' in res, f'4. het van: "{res}"')
print('JS errors:', len(errs)); [print('  ', e) for e in errs[:3]]
b.close(); p.stop()
