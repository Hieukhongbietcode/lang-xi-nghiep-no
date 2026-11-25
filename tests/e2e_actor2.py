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

def night(pg): pg.evaluate("()=>resolveNight()"); pg.wait_for_timeout(500)
def nextday(pg): pg.evaluate("()=>{ endDayPhase(false); startNightPhase(); }"); pg.wait_for_timeout(400)
def setpool(pg, cards):
    for k,v in enumerate(cards): pg.select_option(f'#night-action-container .actor-setup[data-k="{k}"]', v); pg.wait_for_timeout(200)
def card(pg, v): pg.locator(f'#night-action-container .actor-b[data-v="{v}"]').click(); pg.wait_for_timeout(300)
seqids=lambda pg: pg.evaluate("()=>state.nightSequence.map(s=>((s.role&&s.role.id)||s.type)+(s._actor?'*':''))")
S=[('DV','actor'),('Bao','wolf'),('Cuc','villager'),('Dao','villager'),('Em','villager'),('Gia','villager')]
# Đêm 1: đặt 3 lá (Phù Thủy, Tiên Tri, Thợ Săn) rồi bỏ qua
pg=fresh(); setup(pg,S,day=1); start(pg); go_step(pg,'actor'); setpool(pg,['witch','seer','hunter']); card(pg,''); night(pg)
# 1. Đêm 2: lá Phù Thủy
nextday(pg); go_step(pg,'actor'); card(pg,'witch'); sq=seqids(pg)
ok('witch*' in sq and sq.index('witch*')==sq.index('actor')+1, f'1. chon la Phu Thuy -> buoc Phu Thuy chen NGAY SAU Dien Vien: {sq}')
ok('là Phù Thủy' in pg.locator('#night-action-container .actor-now').inner_text(), '1. loi dan: "Dem nay Dien Vien la Phu Thuy"')
wolf_bite(pg,'Cuc'); go_step(pg,'witch')
ui=pg.locator('#night-action-container').inner_text()
ok('bình cứu' in ui.lower() and 'bình độc' in ui.lower(), '1. buoc Phu Thuy cua Dien Vien: CO o binh cuu + o binh doc (khong con "Dung ... len ai?")')
ok(pg.evaluate("()=>namesCalledInStep(state.nightSequence[state.currentStepIndex])")==['DV'], '1. nguoi giu buoc nay la Dien Vien (dien thoai DV nhan khung Phu Thuy)')
pg.evaluate("""()=>{ const L=[...document.querySelectorAll('#night-action-container select')]; const heal=L.find(s=>[...s.options].some(o=>o.text.trim().startsWith('Cuc')) && !s.classList.contains('act-poison-sel')); const o=[...heal.options].find(o=>o.text.trim().startsWith('Cuc')); heal.value=o.value; heal.dispatchEvent(new Event('change',{bubbles:true})); }"""); pg.wait_for_timeout(200)
pick(pg,'.act-poison-sel','Dao'); night(pg)
ok(not dead(pg,'Cuc') and dead(pg,'Dao'), '1. binh cuu Cuc (bi can) -> Cuc SONG; binh doc Dao -> Dao CHET')
ok(pg.evaluate("()=>state.players.find(p=>p.name==='DV').roleId")=='actor', '1. het dem: Dien Vien tro lai la Dien Vien')
# 2. Đêm 3: lá Phù Thủy đã dùng -> gạch; chọn Thợ Săn nhưng KHÔNG dùng -> mất
nextday(pg); go_step(pg,'actor')
ok(pg.locator('#night-action-container .actor-b[data-v="witch"]').is_disabled(), '2. dem sau: la Phu Thuy bi gach')
card(pg,'hunter'); night(pg)
ok('hunter' in pg.evaluate("()=>state.actorUsed"), '2. chon la Tho San nhung khong dung gi -> la van MAT (chi dung 1 dem)')
# 3. lá Thợ Săn: Diễn Viên bị cắn chết -> bắn mục tiêu đã chọn
pg=fresh(); setup(pg,S,day=1); start(pg); go_step(pg,'actor'); setpool(pg,['witch','seer','hunter']); card(pg,''); night(pg)
nextday(pg); go_step(pg,'actor'); card(pg,'hunter'); go_step(pg,'hunter'); pick(pg,'.act-hunter-sel','Em'); wolf_bite(pg,'DV'); night(pg)
ok(dead(pg,'DV') and dead(pg,'Em'), '3. la Tho San: chon Em, Dien Vien bi Soi can chet -> BAN chet Em')
# 4. Đêm 1 dùng luôn lá Tiên Tri
pg=fresh(); setup(pg,S,day=1); start(pg); go_step(pg,'actor'); setpool(pg,['witch','seer','hunter']); card(pg,'seer')
go_step(pg,'seer'); pick(pg,'select:not(.name-gather-input)','Bao'); pg.wait_for_timeout(300)
r=pg.evaluate("()=>{ const e=document.querySelector('#night-action-container .soi-result-box'); return e ? e.textContent.replace(/\\s+/g,' ') : '' }")
ok('sói' in r.lower(), f'4. Dem 1 dung luon la Tien Tri soi Bao -> ket qua co "Soi": "{r[:70]}"')
night(pg); pl=pg.evaluate("()=>state.players.map(p=>p.name+':'+p.roleId)")
ok(pl.count('DV:actor')==1 and not any(x.startswith('DV:') and x!='DV:actor' for x in pl), f'4. het Dem 1: Dien Vien chi co 1 ban ghi, van la Dien Vien: {[x for x in pl if x.startswith("DV")]}')
print('JS errors:', len(errs)); [print('  ', e) for e in errs[:3]]
b.close(); p.stop()
