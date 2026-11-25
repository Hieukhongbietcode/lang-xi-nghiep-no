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
import sys
FILE=sys.argv[1] if len(sys.argv)>1 else 'index.html'
from playwright.sync_api import sync_playwright
p=sync_playwright().start(); b=p.chromium.launch(); errs=[]
ok=lambda c,m: print(('  ✅ ' if c else '  ❌ ')+m)
def fresh():
    pg=b.new_page(viewport={'width':1200,'height':900}); pg.route('**/*', pw.route); pg.on('dialog', lambda d: d.accept()); pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto('file://'+ROOT+'/'+FILE, wait_until='load', timeout=120000); pg.wait_for_timeout(700); return pg
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

R={}
# 1+2. sang ván mới: trạng thái cũ phải được xoá
pg=fresh(); S=[('An','villager'),('Cao','fox'),('Binh','wolf'),('Cho','wolf_hound'),('Dung','villager')]
setup(pg,S,day=1)
pg.evaluate("()=>{ state.foxLost=true; state.pyroUsed=true; state.judgeUsed=true; state.wildIdol='Dung'; state.houndChoice='wolf'; if(!PACK_ROLES.includes('wolf_hound')) PACK_ROLES.push('wolf_hound'); }")
start(pg)
R['1. van moi: Cao duoc goi lai (co "da mat nang luc" van truoc bi xoa)']=pg.evaluate("()=>state.nightSequence.some(s=>s.role&&s.role.id==='fox') && !state.foxLost && !state.pyroUsed && !state.judgeUsed && !state.wildIdol")
R['2. van moi: Cho Soi CHUA chon phe -> khong day cung bay']=not pg.evaluate("()=>PACK_ROLES.includes('wolf_hound')")
# 3. Cáo dùng ở Đêm 1
pg=fresh(); S=[('An','villager'),('Cao','fox'),('Binh','wolf'),('Chi','villager'),('Dung','seer'),('Em','villager')]
setup(pg,S,day=1); start(pg); go_step(pg,'fox'); pick(pg,'.act-fox-sel','Chi')
R['3. Cao o Dem 1 chon Chi (sat Binh la Soi) -> 👍 (khong mat nang luc oan)']='👍' in pg.evaluate("()=>{const e=document.querySelector('#night-action-container .fox-res .soi-result-text'); return e?e.textContent:''}")
# 9. Tiên Tri soi Chó Sói ngay Đêm 1 sau khi chọn Sói
pg=fresh(); S=[('An','villager'),('Cho','wolf_hound'),('Binh','wolf'),('Chi','seer'),('Dung','villager')]
setup(pg,S,day=1); start(pg); go_step(pg,'wolf_hound'); pg.locator('#night-action-container .hound-b.wolfc').click(); pg.wait_for_timeout(200)
R['9. Tien Tri soi Cho Soi ngay Dem 1 (vua chon Soi) -> ra SOI']=pg.evaluate("()=>soiIsWolf('Cho')")
# 4. Sói Trắng 1-1 với Dân
pg=fresh(); setup(pg,[('An','villager'),('Trang','white_werewolf'),('Binh','wolf')],day=3); pg.evaluate("()=>{ state.players[2].isAlive=false; }")
res=pg.evaluate("()=>checkWinCondition() ? state.gameResult : 'tiep tuc'")
R[f'4. chi con Soi Trang + 1 Dan -> van TIEP TUC (ket qua: {res})']=(res=='tiep tuc')
# 5. Cáo bỏ chọn
pg=fresh(); S=[('An','villager'),('Cao','fox'),('Binh','wolf'),('Chi','villager'),('Dung','seer'),('Em','villager')]
setup(pg,S); start(pg); go_step(pg,'fox'); pick(pg,'.act-fox-sel','Em')
pg.evaluate("()=>{ const s=document.querySelector('#night-action-container .act-fox-sel'); s.value=''; s.dispatchEvent(new Event('change',{bubbles:true})); }"); pg.wait_for_timeout(200)
pg.evaluate("()=>resolveNight()"); pg.wait_for_timeout(300)
R['5. Cao chon roi BO CHON -> khong mat nang luc oan']=not pg.evaluate("()=>!!state.foxLost")
# 7. bộ bài ngẫu nhiên
pg=fresh(); n=pg.evaluate("()=>{ let c=0; for(let i=0;i<60;i++){ let d=randomBalancedDeck(12); if(d && (d.thief||0)>0) c++; } return c }")
R[f'7. 60 bo bai ngau nhien -> so lan boc trung Ke Trom: {n}']=(n==0)
# 10. lá Kẻ Trộm nằm trong 2 lá dư
pg=fresh(); S=[('An','villager'),('Binh','wolf'),('Chi','seer'),('Dung','villager'),('Em','villager')]
setup(pg,S,day=1); pg.evaluate("()=>{ state.deck.thief=1; state.deck.villager=4; state.thiefExtra=['thief','villager']; }"); start(pg)
R['10. la Ke Trom nam trong 2 la du -> KHONG con buoc Ke Trom']=not pg.evaluate("()=>state.nightSequence.some(s=>s.role&&s.role.id==='thief')")
for k,v in R.items(): ok(v,k)
print('JS errors:', len(errs)); [print('  ', e) for e in errs[:3]]
b.close(); p.stop()
