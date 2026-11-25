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
pg.evaluate("()=>{ state.totalPlayers=12; switchView('view-deck'); renderDeck(); }"); pg.wait_for_timeout(500)
txt=pg.locator('#view-deck').inner_text()
ok(all(x in txt for x in ['Kẻ Phóng Hỏa','Đứa Trẻ Hoang Dã','Người Hầu Tận Tụy','Sói Trắng']), '0. ca 4 vai moi co trong man Thiet lap bo bai')
# 1. Kẻ Phóng Hỏa
S=[('An','villager'),('PH','pyromaniac'),('Binh','wolf'),('Chi','villager'),('Dung','villager'),('Soi2','wolf'),('Em','villager')]
setup(pg,S); start(pg)
seq=pg.evaluate("()=>state.nightSequence.map(s=>(s.role&&s.role.id)||s.type)")
ok(seq.index('pyromaniac') < seq.index('group_action'), f'1. Ke Phong Hoa goi TRUOC bay Soi: {seq}')
go_step(pg,'pyromaniac'); pick(pg,'.act-pyro-sel','Chi'); wolf_bite(pg,'Chi')
right=pg.evaluate("()=>seatNeighbor('Chi',-1,isWolfReal)")
pg.evaluate("()=>resolveNight()"); pg.wait_for_timeout(600)
ok(not dead(pg,'Chi'), '1. Soi can trung nha bi dot (Chi) -> Chi THOAT CHET')
ok(dead(pg,right) and 'bị thiêu' in pg.evaluate("()=>document.getElementById('night-result-text').textContent").lower(), f'1. Soi gan nhat ben PHAI Chi ({right}) bi thieu chet')
pg.evaluate("()=>{ endDayPhase(false); startNightPhase(); }"); pg.wait_for_timeout(400)
ok(not pg.evaluate("()=>state.nightSequence.some(s=>s.role&&s.role.id==='pyromaniac')"), '1. da dot 1 lan -> dem sau KHONG goi nua')
pg=fresh(); setup(pg,S); start(pg); go_step(pg,'pyromaniac'); pick(pg,'.act-pyro-sel','Chi'); wolf_bite(pg,'Dung'); pg.evaluate("()=>resolveNight()"); pg.wait_for_timeout(600)
ok(dead(pg,'Dung') and not dead(pg,'Binh') and not dead(pg,'Soi2') and pg.evaluate("()=>state.pyroUsed"), '1. dot Chi nhung Soi can Dung -> Dung chet binh thuong, khong Soi nao bi thieu, van mat luot dot')
# 2. Đứa Trẻ Hoang Dã
pg=fresh(); S=[('An','villager'),('Tre','wild_child'),('Binh','wolf'),('Chi','seer'),('Dung','villager'),('Em','villager')]
setup(pg,S,day=1); start(pg); go_step(pg,'wild_child'); pick(pg,'.act-wild-sel','Dung'); pg.evaluate("()=>resolveNight()"); pg.wait_for_timeout(500)
ok(pg.evaluate("()=>state.wildIdol")=='Dung', '2. Dem 1 chon Dung lam Hinh Mau')
pg.evaluate("()=>switchView('view-day-execute')"); pg.wait_for_timeout(300)
did=pg.evaluate("()=>state.players.find(p=>p.name==='Dung').id"); pg.evaluate(f"()=>executePlayer('{did}','Dung')"); pg.wait_for_timeout(800)
ok(pg.evaluate("()=>state.players.find(p=>p.name==='Tre').roleId")=='wolf', '2. Hinh Mau bi treo -> Dua Tre hoa Ma Soi NGAY')
pg.evaluate("()=>startNightPhase()"); pg.wait_for_timeout(300); go_step(pg,'group_action')
ok('Tre' in pg.evaluate("()=>namesCalledInStep(state.nightSequence[state.currentStepIndex])"), '2. dem sau day cung bay Soi')
# 3. Người Hầu Tận Tụy
pg=fresh(); S=[('An','villager'),('Hau','devoted_servant'),('Binh','wolf'),('Chi','seer'),('Dung','villager'),('Em','villager')]
setup(pg,S); pg.evaluate("()=>switchView('view-day-execute')"); pg.wait_for_timeout(800)
ok(pg.locator('#servant-box .servant-b').count()==1, '3. man Treo co co nut Nguoi Hau')
pg.locator('#servant-box .servant-b').click(); pg.wait_for_timeout(300); pg.evaluate("()=>executePlayer('p_3','Chi')"); pg.wait_for_timeout(800)
ok(dead(pg,'Chi') and pg.evaluate("()=>state.players.find(p=>p.name==='Hau').roleId")=='seer' and not dead(pg,'Hau'), '3. treo Chi (Tien Tri) -> Chi chet, Nguoi Hau thanh Tien Tri, van song')
pg.evaluate("()=>{ switchView('view-day-execute'); }"); pg.wait_for_timeout(800)
ok(pg.locator('#servant-box').count()==0, '3. da dung -> nut bien mat (1 lan/van)')
# 4. Sói Trắng
pg=fresh(); S=[('An','villager'),('Trang','white_werewolf'),('Binh','wolf'),('Chi','seer'),('Dung','villager'),('Em','villager')]
setup(pg,S,day=2); start(pg)
seq=pg.evaluate("()=>state.nightSequence.map(s=>(s.role&&s.role.id)||s.type)")
ok('white_werewolf' in seq and seq.index('white_werewolf') > seq.index('group_action'), f'4. dem 2 (chan): co buoc rieng Soi Trang SAU bay Soi: {seq}')
go_step(pg,'group_action'); ok('Trang' in pg.evaluate("()=>namesCalledInStep(state.nightSequence[state.currentStepIndex])"), '4. day cung bay Soi')
ok(pg.evaluate("()=>soiIsWolf(state.players.find(p=>p.name==='Trang').id)"), '4. Tien Tri soi Soi Trang -> ra SOI')
go_step(pg,'white_werewolf'); pick(pg,'.act-white-sel','Binh'); pg.evaluate("()=>resolveNight()"); pg.wait_for_timeout(600)
ok(dead(pg,'Binh'), '4. dem chan Soi Trang giet Binh (Soi)')
pg.evaluate("()=>{ endDayPhase(false); startNightPhase(); }"); pg.wait_for_timeout(400)
ok(not pg.evaluate("()=>state.nightSequence.some(s=>s.role&&s.role.id==='white_werewolf')"), '4. dem 3 (le): KHONG co buoc rieng')
pg=fresh(); setup(pg,[('An','villager'),('Trang','white_werewolf'),('Binh','wolf')],day=3)
pg.evaluate("()=>{ state.players[0].isAlive=false; state.players[2].isAlive=false; }")
ok(pg.evaluate("()=>checkWinCondition() && state.gameResult")=='SÓI TRẮNG THẮNG!', '4. chi con Soi Trang -> "SOI TRANG THANG!"')
pg=fresh(); setup(pg,[('An','villager'),('Trang','white_werewolf'),('Binh','wolf'),('Chi','villager')],day=3)
pg.evaluate("()=>{ state.players[3].isAlive=false; }")
res=pg.evaluate("()=>checkWinCondition() ? state.gameResult : 'chua ket thuc'")
ok('SÓI' in res.upper() and 'TRẮNG' not in res.upper(), f'4. Soi Trang + Soi vs 1 Dan -> bay Soi thang (Soi Trang tinh la Soi): "{res}"')
pg=fresh(); setup(pg,[('An','villager'),('Trang','white_werewolf'),('Binh','wolf'),('Chi','villager'),('Dung','villager')],day=3)
pg.evaluate("()=>{ state.players[2].isAlive=false; }")
res=pg.evaluate("()=>checkWinCondition() ? state.gameResult : 'chua ket thuc'")
ok(res=='chua ket thuc', f'4. het Soi thuong nhung Soi Trang con song -> Dan CHUA thang: "{res}"')
print('JS errors:', len(errs)); [print('  ', e) for e in errs[:4]]
b.close(); p.stop()
