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

def night(pg): pg.evaluate("()=>resolveNight()"); pg.wait_for_timeout(600)
rt=lambda pg: pg.locator('#night-result-text').inner_text()
# 1. đúng video: Kẻ Phóng Hỏa thiêu Sói, không ai khác chết
pg=fresh(); S=[('An','villager'),('PH','pyromaniac'),('Evelyn','wolf'),('Faye','villager'),('Dung','villager'),('Soi2','wolf'),('Em','villager')]
setup(pg,S); start(pg); go_step(pg,'pyromaniac'); pick(pg,'.act-pyro-sel','Faye'); wolf_bite(pg,'Faye')
right=pg.evaluate("()=>seatNeighbor('Faye',-1,isWolfReal)"); night(pg); t=rt(pg)
ok('không ai chết' not in t and 'Có 1 người chết' in t.replace('\n',' '), f'1. Ke Phong Hoa thieu {right} -> tieu de "Co 1 nguoi chet" (khong con "Dem qua khong ai chet")')
ok(pg.locator('#night-result-text .rep-card.dead').count()==1 and 'Bị thiêu chết' in pg.evaluate("()=>document.querySelector('#night-result-text .censor-box').textContent"), '1. co the lat + nguyen nhan trong o che mo')
pg.evaluate("()=>{ switchView('view-day-discuss'); }"); pg.wait_for_timeout(300); pg.evaluate("()=>{ switchView('view-night-result'); }"); pg.wait_for_timeout(500)
ok('Có 1 người chết' in pg.evaluate("()=>state.nightResultHtml.replace(/<[^>]+>/g,' ').replace(/\\s+/g,' ')"), '1. quay ra roi vao lai -> bao cao da LUU dung')
# 2. đã có 1 người chết + Sói chết nhiễm trùng -> 2
pg=fresh(); S=[('An','villager'),('HiepSi','rusty_knight'),('Binh','wolf'),('Chi','villager'),('Soi2','wolf'),('Em','villager'),('Gia','villager')]
setup(pg,S); start(pg); wolf_bite(pg,'HiepSi'); night(pg); w=pg.evaluate("()=>state.rustyInf && state.rustyInf.name")
pg.evaluate("()=>{ endDayPhase(false); startNightPhase(); }"); pg.wait_for_timeout(400); wolf_bite(pg,'Chi'); night(pg); t=rt(pg).replace('\n',' ')
ok('Có 2 người chết' in t and pg.locator('#night-result-text .rep-card.dead').count()==2, f'2. Soi can Chi + {w} chet nhiem trung -> "Co 2 nguoi chet", 2 the lat')
# 3. Gấu giải thích rõ
pg=fresh(); S=[('An','villager'),('Gau','bear_tamer'),('Chi','villager'),('Binh','wolf'),('Dung','villager'),('Em','villager')]
setup(pg,S); start(pg); night(pg); t=rt(pg)
ok('Gấu im lặng' in t and 'An' in t and 'Chi' in t and 'không ai là Sói' in t and 'không gầm' in t, '3. Gau im lang: ghi ro 2 nguoi ngoi canh (An, Chi), khong ai la Soi, quan tro KHONG gam')
pg=fresh(); S=[('An','villager'),('Gau','bear_tamer'),('Binh','wolf'),('Chi','villager'),('Dung','villager'),('Em','villager')]
setup(pg,S); start(pg); night(pg); t=rt(pg)
ok('GẤU GẦM' in t and 'gầm lên' in t, '3. Gau gam: ghi ro co Soi ngoi canh + "Quan tro hay gam len"')
# 4. ⓘ trên lựa chọn Kẻ Trộm / Diễn Viên (quản trò)
pg=fresh(); S=[('An','villager'),('Trom','thief'),('Binh','wolf'),('Dung','villager'),('Em','villager')]
setup(pg,S,day=1); pg.evaluate("()=>{ state.deck.thief=1; state.thiefExtra=['seer','priest']; }"); start(pg); go_step(pg,'thief')
ok(pg.locator('#night-action-container .thief-b .opt-i').count()==2, '4. Ke Trom: 2 lua chon deu co nut ⓘ')
pg.locator('#night-action-container .thief-b .opt-i').first.click(); pg.wait_for_timeout(500)
info=pg.evaluate("()=>{ const m=[...document.querySelectorAll('[id*=modal]:not(.hidden), [role=dialog]')].filter(e=>e.offsetParent||getComputedStyle(e).display!=='none'); return {mo:m.map(e=>e.id+': '+e.innerText.trim().slice(0,40)), chon: state.thiefChoice||''} }")
print('   DEBUG sau khi bam i:', info)
modal=any('Tiên Tri' in x for x in info['mo'])
ok(modal and not pg.evaluate("()=>state.thiefChoice"), '4. bam ⓘ -> mo mo ta vai Tien Tri, KHONG chon nham la do')
pg=fresh(); S=[('An','villager'),('DV','actor'),('Binh','wolf'),('Dung','villager'),('Em','villager')]
setup(pg,S,day=1); start(pg); go_step(pg,'actor')
for k,v in enumerate(['seer','guard','priest']): pg.select_option(f'#night-action-container .actor-setup[data-k="{k}"]', v); pg.wait_for_timeout(200)
ok(pg.locator('#night-action-container .actor-b .opt-i').count()==3, '4. Dien Vien: 3 la deu co nut ⓘ')
f=pg.evaluate("()=>onlineStepFields().find(x=>x.kind==='choice')")
ok(f and sum(1 for o in f['options'] if o.get('d'))==3 and [o['t'] for o in f['options'] if o.get('d')]==['Tiên Tri','Bảo Vệ','Thầy Tu'], f'4. dien thoai nhan kem mo ta cua 3 la (vd Tien Tri: "{(f["options"][0].get("d") or "")[:50]}...")')
print('JS errors:', len(errs)); [print('  ', e) for e in errs[:3]]
b.close(); p.stop()
