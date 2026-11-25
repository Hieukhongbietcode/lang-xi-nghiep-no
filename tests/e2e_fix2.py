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
gm.locator('#online-foot .ol-btn.main').click(); gm.wait_for_timeout(900)
gm.evaluate("()=>{ROLES_DB.forEach(r=>state.deck[r.id]=0); Object.assign(state.deck,{wolf:1,wolf_hound:1,actor:1,ghost:1,villager:3}); renderDeck();}")
gm.locator('#view-deck .bottom-safe button').last.click(); gm.wait_for_timeout(1000)
if gm.locator('#deck-warn-modal:not(.hidden)').count(): gm.locator('#deck-warn-modal button').last.click(); gm.wait_for_timeout(500)
asg=gm.evaluate("()=>state.dealAssignment")
gm.evaluate("()=>{Object.keys(state.dealAssignment).forEach(n=>state.dealViewed[n]=1); onlineSaveDeal(); renderDealView();}")
gm.locator('#btn-deal-start').click(); gm.wait_for_timeout(800)
if gm.locator('#deal-warn-overlay').count(): gm.locator('#deal-warn-overlay button', has_text='Vẫn bắt đầu').click(); gm.wait_for_timeout(400)
gm.wait_for_timeout(1300); [x.click() for x in gm.locator('.tk-ov .tk-close').all()]
role=lambda r:[n for n in names if asg[n]==r][0]
H,A,M,W=role('wolf_hound'),role('actor'),role('ghost'),role('wolf')
gm.locator('#view-night-transition button[onclick="startNightPhase()"]').click(); gm.wait_for_timeout(1200)
for n in names: P[n].evaluate("()=>document.querySelectorAll('.sky-ov,.death-ov,#night-dim').forEach(x=>x.remove())")
# 1. Chó Sói chọn trên điện thoại
gm.evaluate("()=>{state.currentStepIndex=state.nightSequence.findIndex(s=>s.role&&s.role.id==='wolf_hound');renderNightStep();}"); gm.wait_for_timeout(2200)
ph=P[H]; ok(ph.locator('#pick-bar .pfc').count()==2, f'1. Cho Soi ({H}): dien thoai hien 2 nut: {[x.inner_text() for x in ph.locator("#pick-bar .pfc").all()]}')
ph.locator('#pick-bar .pfc', has_text='Ma Sói').click(); ph.wait_for_timeout(200); ph.locator('#pf-ok').click(); gm.wait_for_timeout(1500)
ok(gm.evaluate("()=>state.houndChoice")=='wolf', '1. bam "Theo Phe Ma Soi" + xac nhan -> quan tro ghi dung: wolf')
# 2. Diễn Viên: quản trò đặt 3 lá ở Đêm 1, Đêm 2 người chơi tự chọn lá + mục tiêu
gm.evaluate("()=>{state.currentStepIndex=state.nightSequence.findIndex(s=>s.role&&s.role.id==='actor');renderNightStep();}"); gm.wait_for_timeout(500)
for k,v in enumerate(['seer','guard','priest']): gm.select_option(f'#night-action-container .actor-setup[data-k="{k}"]', v); gm.wait_for_timeout(200)
gm.evaluate("()=>{ resolveNight(); }"); gm.wait_for_timeout(800)
gm.evaluate(f"()=>{{ state.players.forEach(p=>{{ if(p.name==='{M}') {{ p.isAlive=false; p.deathInfo={{day:1,phase:'Đêm',reason:'Bị Sói cắn'}}; }} }}); state.dayCount=2; state.nightResume=null; startNightPhase(); }}"); gm.wait_for_timeout(800)
gm.evaluate("()=>{state.currentStepIndex=state.nightSequence.findIndex(s=>s.role&&s.role.id==='actor');renderNightStep();}"); gm.wait_for_timeout(2200)
pa=P[A]; pa.evaluate("()=>document.querySelectorAll('.sky-ov,.death-ov,#night-dim').forEach(x=>x.remove())")
ok(pa.locator('#pick-bar .pfc').count()>=3, f'2. Dien Vien ({A}): dien thoai hien cac la: {[x.inner_text() for x in pa.locator("#pick-bar .pfc").all()]}')
ok(pa.locator('#pick-bar .pfc-i').count()==3, '2b. dien thoai: 3 la deu co nut ⓘ')
pa.locator('#pick-bar .pfc-i').first.click(); pa.wait_for_timeout(300)
dsc=pa.locator('#pfc-desc').inner_text() if pa.locator('#pfc-desc').is_visible() else ''
ok('Tiên Tri' in dsc and len(dsc)>30 and not pa.evaluate("()=>choiceV"), '2b. bam ⓘ -> hien mo ta la Tien Tri, KHONG chon nham: "'+dsc.replace(chr(10),' ')[:60]+'..."')
pa.locator('#pick-bar .pfc', has_text='Tiên Tri').click(); pa.wait_for_timeout(200); pa.locator('#pf-ok').click(); gm.wait_for_timeout(2200)
ok(gm.evaluate("()=>state.actorPick && state.actorPick.card")=='seer', '2. chon la Tien Tri tren dien thoai -> quan tro ghi dung')
gm.evaluate("()=>{ state.currentStepIndex=state.nightSequence.findIndex(s=>s._actor); renderNightStep(); }"); gm.wait_for_timeout(2200)
pa.evaluate("()=>document.querySelectorAll('.sky-ov,.death-ov,#night-dim').forEach(x=>x.remove())")
ok(pa.locator('#pick-bar').is_visible() and 'Soi' in pa.locator('#pick-bar').inner_text(), '2. sang buoc Tien Tri cua Dien Vien -> dien thoai nhan khung "Soi ai?" cua Tien Tri')
pa.locator(f'#ring .seat[data-n="{W}"]').click(); pa.wait_for_timeout(300); pa.locator('#pf-ok').click(); gm.wait_for_timeout(1800)
r=gm.evaluate("()=>{const e=document.querySelector('#night-action-container .soi-result-box'); return e?e.textContent:''}")
ok('Sói' in r, f'2. cham {W} tren vong lang de soi -> quan tro co ket qua "{r[:40]}"')
# 3. Con Ma đã chết: ô viết chữ trên điện thoại
gm.evaluate("()=>{state.currentStepIndex=state.nightSequence.findIndex(s=>s.role&&s.role.id==='ghost');renderNightStep();}"); gm.wait_for_timeout(2500)
pm=P[M]; pm.evaluate("()=>document.querySelectorAll('.sky-ov,.death-ov,#night-dim').forEach(x=>x.remove())")
ok(pm.locator('#pick-bar #pf-letter').count()==1 and pm.locator('#pick-bar').is_visible(), f'3. Con Ma ({M}) da chet: toi luot -> o viet chu HIEN tren dien thoai')
print('JS errors:', len(errs)); [print('  ', e) for e in errs[:3]]
b.close(); p.stop()
