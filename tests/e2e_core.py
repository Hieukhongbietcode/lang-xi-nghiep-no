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

def pick_all(pg, sel, names):
    pg.evaluate("""([sel,names])=>{ const L=[...document.querySelectorAll('#night-action-container '+sel)].filter(s=>s.offsetParent||true);
      names.forEach((n,k)=>{ const s=L[k]; if(!s) return; const o=[...s.options].find(o=>o.text.trim().startsWith(n)); if(o){ s.value=o.value; s.dispatchEvent(new Event('change',{bubbles:true})); } }); }""", [sel,names]); pg.wait_for_timeout(250)
def night(pg): pg.evaluate("()=>resolveNight()"); pg.wait_for_timeout(500)
def nextday(pg): pg.evaluate("()=>{ endDayPhase(false); startNightPhase(); }"); pg.wait_for_timeout(400)
def hang(pg, n): pg.evaluate("(n)=>{ switchView('view-day-execute'); const p=state.players.find(x=>x.name===n); executePlayer(p.id,p.name); }", n); pg.wait_for_timeout(900)
B=[('Bao','wolf'),('Cuc','villager'),('Dao','villager'),('Em','villager'),('Gia','villager'),('Hoa','villager')]
# 1-2 Bảo Vệ
pg=fresh(); setup(pg,[('Ann','guard')]+B); start(pg); go_step(pg,'guard'); pick(pg,'.act-protect-sel','Cuc'); wolf_bite(pg,'Cuc'); night(pg)
ok(not dead(pg,'Cuc'), '1. Bao Ve che Cuc + Soi can Cuc -> Cuc SONG')
nextday(pg); go_step(pg,'guard')
opt=pg.evaluate("()=>{ const s=document.querySelector('#night-action-container .act-protect-sel'); const o=[...s.options].find(o=>o.text.trim().startsWith('Cuc')); return o ? !o.disabled : false }")
ok(not opt, '2. dem sau KHONG duoc che lai Cuc (2 dem lien tiep)')
# 3-4 Phù Thủy
pg=fresh(); setup(pg,[('Ann','witch')]+B); start(pg); wolf_bite(pg,'Cuc'); go_step(pg,'witch')
pick_all(pg,'select',['Cuc']); pick(pg,'.act-poison-sel','Dao'); night(pg)
ok(not dead(pg,'Cuc'), '3. Phu Thuy dung binh cuu cho Cuc (nguoi bi can) -> Cuc SONG')
ok(dead(pg,'Dao'), '4. Phu Thuy dung binh doc Dao -> Dao CHET')
nextday(pg); wolf_bite(pg,'Em'); go_step(pg,'witch')
ok(pg.locator('#night-action-container button:not([disabled])', has_text='Cứu').count()==0 and not pg.locator('#night-action-container .act-poison-sel:not([disabled])').count(), '3b. dem sau: binh cuu + binh doc da dung -> KHONG dung lai duoc')
# 5-6 Thợ Săn (luật đã chốt)
pg=fresh(); setup(pg,[('Ann','hunter')]+B); start(pg); go_step(pg,'hunter'); pick(pg,'.act-hunter-sel','Dao'); wolf_bite(pg,'Ann'); night(pg)
ok(dead(pg,'Ann') and dead(pg,'Dao'), '5. Tho San chon Dao ban dem + bi Soi can -> Tho San CHET va Dao CHET')
pg=fresh(); setup(pg,[('Ann','hunter')]+B); start(pg); go_step(pg,'hunter'); pick(pg,'.act-hunter-sel','Dao'); night(pg); hang(pg,'Ann')
ok(dead(pg,'Ann') and not dead(pg,'Dao'), '6. Tho San bi TREO ban ngay -> KHONG ban (Dao van song)')
# 7 Cupid
pg=fresh(); setup(pg,[('Ann','cupid')]+B,day=1); start(pg); go_step(pg,'cupid'); pick_all(pg,'select',['Ann','Dao']); night(pg)
nextday(pg); wolf_bite(pg,'Dao'); night(pg)
ok(dead(pg,'Dao') and dead(pg,'Ann'), '7. Cupid (Ann) ghep doi voi Dao: Dao bi can -> Ann CHET THEO')
pg=fresh(); setup(pg,[('Ann','cupid')]+B,day=1); start(pg); go_step(pg,'cupid'); pick_all(pg,'select',['Ann','Dao']); night(pg)
hang(pg,'Ann'); d0=dead(pg,'Dao'); pg.evaluate("()=>startNightPhase()"); pg.wait_for_timeout(400); night(pg)
ok(not d0 and dead(pg,'Dao'), '7b. Ann bi TREO -> Dao chet vao cuoi dem sau (dung luat nha dang dung trong app)')
# 8 Kẻ Bị Nguyền
pg=fresh(); setup(pg,[('Ann','cursed')]+B); start(pg); wolf_bite(pg,'Ann'); night(pg)
ok(not dead(pg,'Ann') and pg.evaluate("()=>state.players.find(p=>p.name==='Ann').roleId")=='wolf', '8. Ke Bi Nguyen bi can -> KHONG chet, hoa Ma Soi')
# 9 Người Cứng Cỏi
pg=fresh(); setup(pg,[('Ann','tough_guy')]+B); start(pg); wolf_bite(pg,'Ann'); night(pg)
a1=dead(pg,'Ann'); nextday(pg); night(pg)
ok(not a1 and dead(pg,'Ann'), '9. Nguoi Cung Coi bi can -> sang do SONG, sang hom sau moi chet')
# 10 Hoàng Tử
pg=fresh(); setup(pg,[('Ann','prince')]+B); hang(pg,'Ann')
ok(not dead(pg,'Ann'), '10. Hoang Tu bi treo lan dau -> lat bai, SONG')
# 11 Kẻ Chán Đời
pg=fresh(); setup(pg,[('Ann','tanner')]+B); hang(pg,'Ann'); pg.wait_for_timeout(1500)
ok(pg.evaluate("()=>state.currentView")=='view-end', f'11. Ke Chan Doi bi treo -> thang, ket thuc van: "{pg.evaluate("()=>state.gameResult")}"')
# 12 Sói Con
pg=fresh(); setup(pg,[('Ann','wolf_cub')]+B); hang(pg,'Ann'); pg.evaluate("()=>startNightPhase()"); pg.wait_for_timeout(400); go_step(pg,'group_action')
n=pg.evaluate("()=>[...document.querySelectorAll('#night-action-container select')].filter(s=>[...s.options].some(o=>o.text.trim().startsWith('Cuc'))).length")
ok(n>=2, f'12. Soi Con bi treo -> dem sau bay Soi duoc can 2 nguoi ({n} o chon)')
# 13 Tiên Tri
pg=fresh(); setup(pg,[('Ann','seer'),('Bao','wolf'),('Cuc','lycan'),('Dao','villager'),('Em','wolf_sorcerer'),('Gia','villager')])
r=pg.evaluate("()=>['Bao','Cuc','Dao'].map(n=>soiIsWolf(state.players.find(p=>p.name===n).id))")
ok(r==[True,True,False], f'13. Tien Tri soi: Soi -> Soi, Nguoi Hoa Soi -> Soi, Dan -> khong: {r}')
# 14-15 thắng thua
pg=fresh(); setup(pg,[('Ann','wolf'),('Bao','wolf'),('Cuc','villager'),('Dao','villager')]); pg.evaluate("()=>{ state.players[2].isAlive=false; }")
ok(pg.evaluate("()=>checkWinCondition() && /SÓI/i.test(state.gameResult)"), '14. 2 Soi vs 1 Dan -> PHE SOI THANG')
pg=fresh(); setup(pg,[('Ann','wolf'),('Cuc','villager'),('Dao','villager')]); pg.evaluate("()=>{ state.players[0].isAlive=false; }")
ok(pg.evaluate("()=>checkWinCondition() && /DÂN|LÀNG/i.test(state.gameResult)"), '15. het Soi -> PHE DAN THANG')
# 16 Bà Già (trục xuất)
pg=fresh(); setup(pg,[('Ann','old_hag')]+B); start(pg); go_step(pg,'old_hag'); pick(pg,'.act-hag-sel','Dao'); night(pg)
ok(pg.evaluate("()=>(typeof getBanishedAliveNames==='function' ? getBanishedAliveNames() : []).includes('Dao')"), '16. Ba Gia truc xuat Dao -> ngay hom do Dao bi cam')
# ===== ĐỢT 2: tương tác chéo =====
pg=fresh(); setup(pg,[('Ann','cupid'),('TS','hunter')]+B[:5],day=1); start(pg); go_step(pg,'cupid'); pick_all(pg,'select',['Ann','Dao']); night(pg)
nextday(pg); go_step(pg,'hunter'); pick(pg,'.act-hunter-sel','Dao'); wolf_bite(pg,'TS'); night(pg)
ok(dead(pg,'TS') and dead(pg,'Dao') and dead(pg,'Ann'), '17. Tho San chet ban dem, ban trung Dao (Cap Doi) -> Ann (nguoi yeu) CHET THEO')
pg=fresh(); setup(pg,[('Ann','guard'),('PT','witch')]+B[:5]); start(pg); go_step(pg,'guard'); pick(pg,'.act-protect-sel','Dao'); go_step(pg,'witch'); pick(pg,'.act-poison-sel','Dao'); night(pg)
ok(dead(pg,'Dao'), '18. Bao Ve che Dao nhung Phu Thuy dau doc Dao -> Dao VAN CHET (Bao Ve chi chan Soi)')
pg=fresh(); setup(pg,[('Ann','guard'),('KN','cursed')]+B[:5]); start(pg); go_step(pg,'guard'); pick(pg,'.act-protect-sel','KN'); wolf_bite(pg,'KN'); night(pg)
ok(not dead(pg,'KN') and pg.evaluate("()=>state.players.find(p=>p.name==='KN').roleId")=='cursed', '19. Ke Bi Nguyen duoc Bao Ve che + bi can -> KHONG hoa Soi')
pg=fresh(); setup(pg,[('Ann','guard'),('CC','tough_guy')]+B[:5]); start(pg); go_step(pg,'guard'); pick(pg,'.act-protect-sel','CC'); wolf_bite(pg,'CC'); night(pg); nextday(pg); night(pg)
ok(not dead(pg,'CC'), '20. Nguoi Cung Coi duoc Bao Ve che + bi can -> KHONG chet tre')
pg=fresh(); setup(pg,[('SC','wolf_cub'),('PT','witch'),('Bao','wolf')]+B[1:5]); start(pg); go_step(pg,'witch'); pick(pg,'.act-poison-sel','SC'); night(pg)
nextday(pg); go_step(pg,'group_action'); n=pg.evaluate("()=>[...document.querySelectorAll('#night-action-container select')].filter(s=>[...s.options].some(o=>o.text.trim().startsWith('Cuc'))).length")
ok(dead(pg,'SC') and n>=2, f'21. Soi Con chet vi bi DAU DOC -> dem sau bay Soi can 2 nguoi ({n} o chon)')
pg=fresh(); setup(pg,[('Ann','prince')]+B); hang(pg,'Ann'); pg.evaluate("()=>{ state.dayCount=3; }"); hang(pg,'Ann')
ok(dead(pg,'Ann'), '22. Hoang Tu bi treo LAN 2 -> chet')
pg=fresh(); setup(pg,[('Ann','tanner')]+B); start(pg); wolf_bite(pg,'Ann'); night(pg); pg.wait_for_timeout(800)
ok(dead(pg,'Ann') and pg.evaluate("()=>state.currentView")!='view-end', '23. Thang Ngoc bi Soi can (khong bi treo) -> KHONG thang, van tiep tuc')
pg=fresh(); setup(pg,[('TT','priest')]+B,day=1); start(pg); go_step(pg,'priest'); pick(pg,'select:not(.name-gather-input)','Dao'); print('   o ban phuoc:', pg.evaluate("()=>[...document.querySelectorAll('#night-action-container select:not(.name-gather-input)')].map(s=>s.className.split(' ').filter(c=>/act-/.test(c)).join('.')+'='+s.value)")); night(pg)
nextday(pg); wolf_bite(pg,'Dao'); night(pg); d1=dead(pg,'Dao')
nextday(pg); wolf_bite(pg,'Dao'); night(pg); d2=dead(pg,'Dao')
hang(pg,'TT'); pg.evaluate("()=>startNightPhase()"); pg.wait_for_timeout(400); wolf_bite(pg,'Dao'); night(pg)
ok(not d1 and not d2 and dead(pg,'Dao'), '24. Thay Tu ban phuoc Dao: bi can Dem 2 + Dem 3 van SONG; Thay Tu bi treo -> lan can sau Dao CHET')
print('JS errors:', len(errs)); [print('  ', e) for e in errs[:4]]
b.close(); p.stop()
