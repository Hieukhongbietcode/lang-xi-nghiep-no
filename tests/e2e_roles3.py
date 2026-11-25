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
pg.evaluate("()=>{ state.totalPlayers=6; switchView('view-deck'); renderDeck(); }"); pg.wait_for_timeout(500)
txt=pg.locator('#view-deck').inner_text()
ok('Diễn Viên' in txt and 'Kẻ Trộm' in txt, '0. Dien Vien + Ke Trom co trong man Thiet lap bo bai')
ids=['bear_tamer','fox','rusty_knight','angel','wolf_hound','stuttering_judge','pyromaniac','wild_child','devoted_servant','white_werewolf','actor','thief']
ic=pg.evaluate("(ids)=>ids.map(id=>{ const e=document.createElement('i'); e.className='fa-solid fa-ic-'+id; document.body.appendChild(e); const bg=getComputedStyle(e,'::before').backgroundImage; const w=getComputedStyle(e,'::before').width; e.remove(); return [id, bg.includes('svg'), w]; })", ids)
ok(all(x[1] for x in ic), f'0. ca 12 icon co hinh ve SVG that: {sum(1 for x in ic if x[1])}/12')
on=pg.evaluate("()=>[...document.querySelectorAll('#view-deck i')].filter(e=>/fa-ic-(actor|thief|fox|bear_tamer)/.test(e.className) && getComputedStyle(e,'::before').backgroundImage.includes('svg')).length")
ok(on>=4, f'0. icon hien tren man bo bai ({on} icon vai moi dang hien)')
# 1. Kẻ Trộm: số người + 2
def deckset(d): pg.evaluate("(d)=>{ ROLES_DB.forEach(r=>state.deck[r.id]=0); Object.assign(state.deck,d); renderDeck(); }", d); pg.wait_for_timeout(300)
btn=lambda: pg.evaluate("()=>{ const b=[...document.querySelectorAll('#view-deck .bottom-safe button')].pop(); return !b.disabled }")
deckset({'thief':1,'wolf':2,'seer':1,'villager':3})
ok(btn() and pg.locator('#target-count').inner_text().strip()=='8', '1. 6 nguoi + Ke Trom: 7 la -> CHUA cho tiep? (kiem tiep)') if False else None
ok(not btn(), '1. 6 nguoi + Ke Trom, bo bai 7 la -> nut Tiep tuc KHOA')
deckset({'thief':1,'wolf':2,'seer':1,'villager':4})
ok(btn() and pg.locator('#target-count').inner_text().strip()=='8' and '/ 8 lá' in pg.locator('#deck-balance').inner_text(), '1. bo bai 8 la (6 nguoi + 2) -> nut MO, muc tieu "8", thanh can bang "/ 8 la"')
deckset({'wolf':2,'seer':1,'villager':3}); ok(btn(), '1. khong co Ke Trom -> van can dung 6 la nhu cu')
# 2. chia bài giữ 2 lá dư
deckset({'thief':1,'wolf':2,'seer':1,'villager':4})
pg.evaluate("()=>{ state.selectedPlayers=['An','Binh','Chi','Dung','Em','Gia']; state.seatOrder=state.selectedPlayers.slice(); state.seatMode='off'; prepareDealView(); }"); pg.wait_for_timeout(400)
da=pg.evaluate("()=>state.dealAssignment"); ex=pg.evaluate("()=>state.thiefExtra")
from collections import Counter
ok(len(da)==6 and len(ex)==2 and Counter(list(da.values())+ex)==Counter({'thief':1,'wolf':2,'seer':1,'villager':4}), f'2. chia 6 la cho 6 nguoi, GIU 2 la du: {ex}')
# 3. Kẻ Trộm Đêm 1
def thief_game(extra, choice):
    pg2=fresh(); S=[('An','villager'),('Trom','thief'),('Binh','wolf'),('Chi','seer'),('Dung','villager')]
    setup(pg2,S,day=1); pg2.evaluate("(e)=>{ state.deck.thief=1; state.thiefExtra=e; }", extra); start(pg2); go_step(pg2,'thief'); return pg2
pg2=thief_game(['wolf','priest'],'k0')
seq=pg2.evaluate("()=>state.nightSequence.map(s=>(s.role&&s.role.id)||s.type)"); ok(seq[0]=='thief', f'3. Ke Trom goi DAU TIEN Dem 1: {seq[:3]}')
pg2.locator('#night-action-container .thief-b').first.click(); pg2.wait_for_timeout(300)
go_step(pg2,'group_action'); ok('Trom' in pg2.evaluate("()=>namesCalledInStep(state.nightSequence[state.currentStepIndex])"), '3. lay la Ma Soi -> day cung bay ngay Dem 1')
pg2.evaluate("()=>resolveNight()"); pg2.wait_for_timeout(400); ok(pg2.evaluate("()=>state.players.find(p=>p.name==='Trom').roleId")=='wolf', '3. het Dem 1 -> Ke Trom thanh Ma Soi')
pg2=thief_game(['wolf','wolf'],'')
ok(pg2.locator('#night-action-container .thief-b[data-v="keep"]').is_disabled(), '3. ca 2 la deu la Soi -> nut "Khong doi" BI KHOA')
pg2.evaluate("()=>resolveNight()"); pg2.wait_for_timeout(400); ok(pg2.evaluate("()=>state.players.find(p=>p.name==='Trom').roleId")=='wolf', '3. khong chon gi + 2 la Soi -> bat buoc thanh Soi')
pg2=thief_game(['seer','priest'],''); pg2.locator('#night-action-container .thief-b[data-v="keep"]').click(); pg2.wait_for_timeout(200)
pg2.evaluate("()=>resolveNight()"); pg2.wait_for_timeout(400); ok(pg2.evaluate("()=>state.players.find(p=>p.name==='Trom').roleId")=='villager', '3. chon "Khong doi" -> choi nhu Dan Lang')
# 4. Diễn Viên
pg=fresh(); S=[('An','villager'),('DV','actor'),('Binh','wolf'),('Chi','villager'),('Dung','villager'),('Em','villager')]
setup(pg,S,day=1); start(pg); go_step(pg,'actor')
for k,v in enumerate(['seer','guard','priest']): pg.select_option(f'#night-action-container .actor-setup[data-k="{k}"]', v); pg.wait_for_timeout(200)
ok(pg.evaluate("()=>state.actorPool")==['seer','guard','priest'], '4. Dem 1 dat rieng 3 la: Tien Tri, Bao Ve, Thay Tu')
pg.evaluate("()=>resolveNight()"); pg.wait_for_timeout(400)
pg.evaluate("()=>{ endDayPhase(false); startNightPhase(); }"); pg.wait_for_timeout(400); go_step(pg,'actor')
pg.locator('#night-action-container .actor-b[data-v="seer"]').click(); pg.wait_for_timeout(300); pick(pg,'.act-actor-sel','Binh'); pg.wait_for_timeout(300)
r=pg.evaluate("()=>document.querySelector('#night-action-container .actor-res .soi-result-text').textContent"); ok('Là Sói' in r, f'4. Dem 2 dung la Tien Tri soi Binh -> "{r}" (o ket qua up la ❓)')
pg.evaluate("()=>resolveNight()"); pg.wait_for_timeout(400)
pg.evaluate("()=>{ endDayPhase(false); startNightPhase(); }"); pg.wait_for_timeout(400); go_step(pg,'actor')
ok(pg.locator('#night-action-container .actor-b[data-v="seer"]').is_disabled(), '4. Dem 3: la Tien Tri da dung -> bi gach')
pg.locator('#night-action-container .actor-b[data-v="guard"]').click(); pg.wait_for_timeout(300); pick(pg,'.act-actor-sel','Chi'); wolf_bite(pg,'Chi')
pg.evaluate("()=>resolveNight()"); pg.wait_for_timeout(500)
ok(not dead(pg,'Chi'), '4. dung la Bao Ve che Chi + Soi can Chi -> Chi SONG (bao ve co hieu luc that)')
pg.evaluate("()=>{ endDayPhase(false); startNightPhase(); }"); pg.wait_for_timeout(400); go_step(pg,'actor')
pg.locator('#night-action-container .actor-b[data-v="priest"]').click(); pg.wait_for_timeout(200); pg.evaluate("()=>resolveNight()"); pg.wait_for_timeout(400)
pg.evaluate("()=>{ endDayPhase(false); startNightPhase(); }"); pg.wait_for_timeout(400)
ok(not pg.evaluate("()=>state.nightSequence.some(s=>s.role&&s.role.id==='actor')"), '4. dung het 3 la -> dem sau KHONG goi Dien Vien')
print('JS errors:', len(errs)); [print('  ', e) for e in errs[:4]]
b.close(); p.stop()
