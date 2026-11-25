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

# Người Hầu nhận vai Thợ Săn: người bị treo KHÔNG được bắn
pg=fresh(); S=[('An','villager'),('Hau','devoted_servant'),('Binh','wolf'),('TS','hunter'),('Dung','villager'),('Em','villager')]
setup(pg,S); pg.evaluate("()=>switchView('view-day-execute')"); pg.wait_for_timeout(800)
pg.locator('#servant-box .servant-b').click(); pg.wait_for_timeout(300)
pg.evaluate("()=>executePlayer('p_3','TS')"); pg.wait_for_timeout(1200)
shot=pg.evaluate("()=>[...document.querySelectorAll('[id*=hunter],[class*=hunter]')].some(e=>e.offsetParent && /bắn|Thợ Săn/i.test(e.textContent))")
ok(dead(pg,'TS') and pg.evaluate("()=>state.players.find(p=>p.name==='Hau').roleId")=='hunter' and pg.evaluate("()=>state.players.find(p=>p.name==='TS').roleId")=='devoted_servant', '1. treo Tho San + Nguoi Hau lo dien -> TS chet voi la Nguoi Hau, Hau thanh Tho San')
ok(not shot, '1. nguoi bi treo KHONG duoc ban (khong hien bang ban cua Tho San)')
# Kẻ Trộm lấy lá Tiên Tri -> tới lượt ngay Đêm 1
pg=fresh(); S=[('An','villager'),('Trom','thief'),('Binh','wolf'),('Dung','villager'),('Em','villager')]
setup(pg,S,day=1); pg.evaluate("()=>{ state.deck.thief=1; state.deck.seer=1; state.thiefExtra=['seer','villager']; }"); start(pg)
go_step(pg,'thief'); pg.locator('#night-action-container .thief-b[data-v="k0"]').click(); pg.wait_for_timeout(300)
i=pg.evaluate("()=>state.nightSequence.findIndex(s=>s.role&&s.role.id==='seer')")
called=pg.evaluate(f"()=>namesCalledInStep(state.nightSequence[{i}])") if i>=0 else None
ok(i>=0 and 'Trom' in (called or []), f'2. Ke Trom lay la Tien Tri -> buoc Tien Tri Dem 1 goi Trom: {called}')
print('JS errors:', len(errs)); [print('  ', e) for e in errs[:3]]
b.close(); p.stop()
