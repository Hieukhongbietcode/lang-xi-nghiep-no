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
p=sync_playwright().start(); b=p.chromium.launch(); errs=[]
ok=lambda c,m: print(('  ✅ ' if c else '  ❌ ')+m)
def fresh():
    pg=b.new_page(viewport={'width':1200,'height':900}); pg.route('**/*', pw.route); pg.on('dialog', lambda d: d.accept()); pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto('file://'+ROOT+'/index.html', wait_until='load', timeout=120000); pg.wait_for_timeout(700); return pg
def setup(pg, seats, day=2, seating=True):
    # seats: [(ten, vai)] theo thứ tự chỗ ngồi
    pg.evaluate("""([S, day, seating])=>{ state.players=S.map(([n,r],i)=>({id:'p_'+i,name:n,roleId:r,initialRoleId:r,isAlive:true})); state.seatOrder=S.map(x=>x[0]); state.selectedPlayers=state.seatOrder.slice(); state.totalPlayers=S.length;
        state.seatMode = seating ? 'on' : 'off'; state.dealMode='app'; ROLES_DB.forEach(r=>state.deck[r.id]=0); S.forEach(([n,r])=>state.deck[r]=(state.deck[r]||0)+1); state.dayCount=day; state.nightResume=null; state.eventLog=[];
        state.dealAssignment={}; S.forEach(([n,r])=>state.dealAssignment[n]=r);
        }""", [seats, day, seating])
def start(pg):
    pg.evaluate("()=>startNightPhase()"); pg.wait_for_timeout(300)
    pg.evaluate("()=>{ if (state.dayCount===1) { state.n1TempData=state.n1TempData||{}; Object.entries(state.dealAssignment).forEach(([n,r])=>{ let L=(state.n1TempData[r]=state.n1TempData[r]||[]); if(!L.includes(n)) L.push(n); }); } }")
def go_step(pg, rid):
    i=pg.evaluate(f"()=>state.nightSequence.findIndex(s=>(s.role&&s.role.id==='{rid}')||s.type==='{rid}')")
    pg.evaluate(f"()=>{{state.currentStepIndex={i};renderNightStep();}}"); pg.wait_for_timeout(300); return i
def pick(pg, sel, name):
    pg.evaluate(f"""()=>{{ const L=[...document.querySelectorAll('#night-action-container {sel}')]; const s=L.find(x=>[...x.options].some(o=>o.text.trim().startsWith('{name}'))); const o=[...s.options].find(o=>o.text.trim().startsWith('{name}')); s.value=o.value; s.dispatchEvent(new Event('change',{{bubbles:true}})); }}"""); pg.wait_for_timeout(250)
def wolf_bite(pg, name): go_step(pg,'group_action'); pick(pg,'select', name)
dead=lambda pg,n: pg.evaluate(f"()=>!state.players.find(p=>p.name==='{n}').isAlive")
pg=fresh()
print('   hasSeating khi seatMode=on:', pg.evaluate("()=>{state.seatMode='on'; return hasSeating()}"), '| off:', pg.evaluate("()=>{state.seatMode='off'; return hasSeating()}"))
# 0. bộ bài
pg.evaluate("()=>{ state.totalPlayers=12; switchView('view-deck'); renderDeck(); }"); pg.wait_for_timeout(500)
txt=pg.locator('#view-deck').inner_text()
ok(all(x in txt for x in ['Người Điều Khiển Gấu','Con Cáo','Hiệp Sĩ Rỉ Sét','Thiên Thần','Chó Sói','Thẩm Phán Nói Lắp']), '0. ca 6 vai moi co trong man Thiet lap bo bai')
# 1. Cáo (có xếp chỗ): An | Cáo | Bình(Sói) | Chi | Dũng | Em
S=[('An','villager'),('Cao','fox'),('Binh','wolf'),('Chi','villager'),('Dung','seer'),('Em','villager')]
setup(pg,S); pg.evaluate("()=>startNightPhase()"); pg.wait_for_timeout(400); go_step(pg,'fox'); pick(pg,'.act-fox-sel','Chi')
r=pg.evaluate("()=>document.querySelector('#night-action-container .fox-res .soi-result-text').textContent+' | '+document.querySelector('#night-action-container .fox-res .soi-result-name').textContent"); ok('👍' in r and 'Binh' in r, f'1. Cao chon Chi -> nhom Chi + 2 nguoi sat (co Binh la Soi) -> "{r}"')
ok(pg.locator('#night-action-container .fox-res .soi-result-box').count()==1, '1. ket qua dung o "soi-result-box" -> tu up la ❓ + tu gui dien thoai online')
pick(pg,'.act-fox-sel','Em'); r=pg.evaluate("()=>document.querySelector('#night-action-container .fox-res .soi-result-text').textContent")
ok('👎' in r, f'1. doi sang Em -> nhom Em/Dung/An khong co Soi -> "{r}"')
pg.evaluate("()=>resolveNight()"); pg.wait_for_timeout(500)
pg.evaluate("()=>{ state.dayCount=3; startNightPhase(); }"); pg.wait_for_timeout(400)
ok(pg.evaluate("()=>state.foxLost && !state.nightSequence.some(s=>s.role&&s.role.id==='fox')"), '1. ra 👎 -> dem sau KHONG goi Cao nua')
# 2. Gấu (có xếp chỗ): Bình(Sói) ngồi sát Gấu
pg=fresh(); S=[('An','villager'),('Gau','bear_tamer'),('Binh','wolf'),('Chi','villager'),('Dung','villager'),('Em','villager')]
setup(pg,S); pg.evaluate("()=>startNightPhase()"); pg.wait_for_timeout(300); pg.evaluate("()=>resolveNight()"); pg.wait_for_timeout(600)
t=pg.locator('#night-result-text').inner_text(); ok('gấu gầm' in t.lower(), '2. Soi ngoi sat Gau -> sang ra "🐻 Gau gam!"')
pg=fresh(); S=[('An','villager'),('Gau','bear_tamer'),('Chi','villager'),('Binh','wolf'),('Dung','villager'),('Em','villager')]
setup(pg,S); pg.evaluate("()=>startNightPhase()"); pg.wait_for_timeout(300); pg.evaluate("()=>resolveNight()"); pg.wait_for_timeout(600)
t=pg.locator('#night-result-text').inner_text(); ok('gấu im lặng' in t.lower() and 'gấu gầm' not in t.lower(), '2. Soi KHONG ngoi sat -> "Gau im lang"')
# 2b. Gấu, ván không xếp chỗ -> quản trò chọn
setup(pg,S,seating=False); pg.evaluate("()=>startNightPhase()"); pg.wait_for_timeout(300); pg.evaluate("()=>resolveNight()"); pg.wait_for_timeout(600)
ok(pg.locator('#night-result-text .bear-nb0').count()==1, '2. khong xep cho -> quan tro chon 2 nguoi sat Gau')
pg.select_option('#night-result-text .bear-nb0','An'); pg.select_option('#night-result-text .bear-nb1','Binh'); pg.wait_for_timeout(300)
ok('gấu gầm' in pg.locator('#night-result-text').inner_text().lower(), '2. quan tro chon An + Binh(Soi) -> Gau gam')
# 3. Hiệp Sĩ Rỉ Sét: bên trái Hiệp Sĩ (seatNeighbor +1) là ai?
pg=fresh(); S=[('An','villager'),('HiepSi','rusty_knight'),('Binh','wolf'),('Chi','villager'),('Soi2','wolf'),('Em','villager'),('Gia','villager')]
setup(pg,S); left=pg.evaluate("()=>seatNeighbor('HiepSi',1)"); print('   ben TRAI Hiep Si theo quy uoc app:', left)
pg.evaluate("()=>startNightPhase()"); pg.wait_for_timeout(300); wolf_bite(pg,'HiepSi'); pg.evaluate("()=>resolveNight()"); pg.wait_for_timeout(600)
inf=pg.evaluate("()=>state.rustyInf"); expect=pg.evaluate("()=>seatNeighbor('HiepSi',1,isWolfReal)")
ok(dead(pg,'HiepSi') and inf and inf['name']==expect, f'3. Soi can Hiep Si -> {expect} (Soi gan nhat ben trai) bi nhiem trung: {inf}')
ok(not dead(pg,expect), '3. sang hom do Soi do CHUA chet')
pg.evaluate("()=>endDayPhase(false)"); pg.wait_for_timeout(300); pg.evaluate("()=>startNightPhase()"); pg.wait_for_timeout(300); pg.evaluate("()=>resolveNight()"); pg.wait_for_timeout(600)
ok(dead(pg,expect) and 'nhiễm trùng' in pg.locator('#night-result-text').inner_text(), f'3. sang sau dem ke tiep -> {expect} chet "nhiem trung"')
# 3b. bị Phù Thủy đầu độc -> KHÔNG kích hoạt
pg=fresh(); S=[('An','villager'),('HiepSi','rusty_knight'),('Binh','wolf'),('PT','witch'),('Em','villager'),('Gia','villager')]
setup(pg,S); pg.evaluate("()=>startNightPhase()"); pg.wait_for_timeout(300); go_step(pg,'witch')
pick(pg,'select','HiepSi')
pg.evaluate("()=>resolveNight()"); pg.wait_for_timeout(500)
ok(dead(pg,'HiepSi') and not pg.evaluate("()=>state.rustyInf"), '3. Hiep Si bi Phu Thuy doc chet -> KHONG nhiem trung ai')
# 4. Thiên Thần
pg=fresh(); S=[('An','villager'),('TT','angel'),('Binh','wolf'),('Chi','villager'),('Dung','villager')]
setup(pg,S,day=1); start(pg); print('   DEBUG n1TempData:', pg.evaluate("()=>JSON.stringify(state.n1TempData)")[:160]); wolf_bite(pg,'TT'); pg.evaluate("()=>resolveNight()"); pg.wait_for_timeout(2600)
ok(pg.evaluate("()=>state.currentView")=='view-end' and 'THIÊN THẦN' in pg.locator('#end-game-title').inner_text(), '4. Thien Than bi can Dem 1 -> ket thuc van, "THIEN THAN THANG!"')
pg=fresh(); setup(pg,S,day=1); pg.evaluate("()=>{ switchView('view-day-execute'); }"); pg.wait_for_timeout(300); pg.evaluate("()=>executePlayer('p_1','TT')"); pg.wait_for_timeout(2600)
ok(pg.evaluate("()=>state.currentView")=='view-end', '4. Thien Than bi treo Ngay 1 -> thang ngay')
pg=fresh(); setup(pg,S,day=2); pg.evaluate("()=>startNightPhase()"); pg.wait_for_timeout(300)
ok(pg.evaluate("()=>state.players.find(p=>p.name==='TT').roleId")=='villager', '4. song toi Dem 2 -> thanh Dan Lang')
# 5. Chó Sói
pg=fresh(); S=[('An','villager'),('Cho','wolf_hound'),('Binh','wolf'),('Chi','seer'),('Dung','villager')]
setup(pg,S,day=1); start(pg)
seq=pg.evaluate("()=>state.nightSequence.map(s=>(s.role&&s.role.id)||s.type)"); ok('wolf_hound' in seq and seq.index('wolf_hound') < seq.index('group_action'), f'5. Cho Soi goi Dem 1, TRUOC bay Soi: {seq}')
go_step(pg,'wolf_hound'); pg.locator('#night-action-container .hound-b.wolfc').click(); pg.wait_for_timeout(300)
go_step(pg,'group_action'); pack=pg.evaluate("()=>namesCalledInStep(state.nightSequence[state.currentStepIndex])")
ok('Cho' in pack, f'5. chon Soi -> day cung bay ngay Dem 1: {pack}')
pg.evaluate("()=>resolveNight()"); pg.wait_for_timeout(500)
ok(pg.evaluate("()=>state.players.find(p=>p.name==='Cho').roleId")=='wolf', '5. sau Dem 1 thanh Ma Soi')
# 6. Thẩm Phán
pg=fresh(); S=[('An','villager'),('TP','stuttering_judge'),('Binh','wolf'),('Chi','villager'),('Dung','villager'),('Em','villager')]
setup(pg,S,day=2); pg.evaluate("()=>switchView('view-day-execute')"); pg.wait_for_timeout(800)
ok(pg.locator('#judge-box .judge-b').count()==1, '6. man Treo co co nut Tham Phan')
pg.locator('#judge-box .judge-b').click(); pg.wait_for_timeout(300)
pg.evaluate("()=>executePlayer('p_3','Chi')"); pg.wait_for_timeout(800)
ok(pg.evaluate("()=>state.currentView")=='view-day-execute' and dead(pg,'Chi') and pg.evaluate("()=>state.dayCount")==2, '6. treo Chi xong -> VAN o man Treo co (bo phieu lan 2), chua sang dem')
pg.evaluate("()=>executePlayer('p_4','Dung')"); pg.wait_for_timeout(800)
ok(dead(pg,'Dung') and pg.evaluate("()=>state.currentView")!='view-day-execute' and pg.locator('#judge-box').count()==0, '6. treo nguoi thu 2 -> sang dem; nut Tham Phan bien mat (1 lan/van)')
print('JS errors:', len(errs)); [print('  ', e) for e in errs[:4]]
b.close(); p.stop()
