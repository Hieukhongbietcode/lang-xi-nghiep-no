# Test trình duyệt cho kho web: đường đi chính của 1 ván online.
# Bất kỳ mục ❌ hay lỗi JavaScript nào -> thoát mã lỗi (GitHub báo đỏ).
import os, sys
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
WS = os.environ.get('LXN_WS', 'ws://localhost:8787')
try:
    import pw  # chỉ có trên máy người viết test (không có mạng): phục vụ thư viện CDN từ máy
    ROUTE = pw.route
except ImportError:
    ROUTE = None

bad = 0
def ok(cond, msg):
    global bad
    print(('  ✅ ' if cond else '  ❌ ') + msg)
    if not cond: bad += 1

p = sync_playwright().start(); b = p.chromium.launch(); errs = []
def page(w=390, h=844):
    c = b.new_context(viewport={'width': w, 'height': h}); pg = c.new_page()
    if ROUTE: pg.route('**/*', ROUTE)
    pg.on('dialog', lambda d: d.accept())
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    return pg

gm = page(1400, 860)
gm.goto(f'file://{ROOT}/index.html?ws={WS}', wait_until='load', timeout=120000); gm.wait_for_timeout(1500)
ok(gm.locator('#btn-online-home').is_visible(), 'trang quan tro mo duoc')
gm.locator('#btn-online-home').click(); gm.wait_for_timeout(2000)
link = gm.locator('.ol-link span').inner_text().replace('http://localhost/play.html', f'file://{ROOT}/play.html')
if 'play.html' in link and not link.startswith('file://'):
    link = f'file://{ROOT}/play.html?' + link.split('?', 1)[1]
ok('room=' in link, 'tao phong online, co link moi')
names = ['Một', 'Hai', 'Ba', 'Bốn', 'Năm']; P = {}
for n in names:
    pg = page(); pg.goto(link + ('&' if '?' in link else '?') + f'ws={WS}'); pg.wait_for_timeout(500)
    pg.fill('#in-name', n); pg.locator('#btn-join').click(); pg.wait_for_timeout(400); P[n] = pg
gm.wait_for_timeout(800)
ok(gm.locator('.ol-p').count() == 5, '5 nguoi vao phong')
gm.locator('#online-foot .ol-btn.main').click(); gm.wait_for_timeout(1000)
gm.evaluate("()=>{ROLES_DB.forEach(r=>state.deck[r.id]=0); Object.assign(state.deck,{wolf:1,seer:1,guard:1,villager:2}); renderDeck();}")
gm.locator('#view-deck .bottom-safe button').last.click(); gm.wait_for_timeout(1200)
if gm.locator('#deck-warn-modal:not(.hidden)').count(): gm.locator('#deck-warn-modal button').last.click(); gm.wait_for_timeout(600)
asg = gm.evaluate("()=>state.dealAssignment")
ok(len(asg) == 5, 'chia bai cho 5 nguoi')
for n in names:
    q = P[n]; q.locator('#card-zone .btn-main').click(); q.wait_for_timeout(700)
    q.locator('#dl-q').click(); q.wait_for_timeout(900); q.locator('#dl-ok').click(); q.wait_for_timeout(1000)
ok(gm.locator('#btn-deal-start:not([disabled])').count() == 1, 'ca 5 nguoi da xem bai')
gm.locator('#btn-deal-start').click(); gm.wait_for_timeout(800)
if gm.locator('#deal-warn-overlay').count(): gm.locator('#deal-warn-overlay button', has_text='Vẫn bắt đầu').click(); gm.wait_for_timeout(500)
gm.wait_for_timeout(1500); [x.click() for x in gm.locator('.tk-ov .tk-close').all()]
gm.locator('#view-night-transition button[onclick="startNightPhase()"]').click(); gm.wait_for_timeout(1500)
G = [n for n in names if asg[n] == 'guard'][0]; S = [n for n in names if asg[n] == 'seer'][0]
gm.evaluate("()=>{state.currentStepIndex=state.nightSequence.findIndex(s=>s.role&&s.role.id==='guard');renderNightStep();}"); gm.wait_for_timeout(2000)
pg_ = P[G]; pg_.evaluate("()=>document.querySelectorAll('.sky-ov').forEach(x=>x.remove())")
pg_.locator(f'#ring .seat[data-n="{S}"]').click(); pg_.wait_for_timeout(300); pg_.locator('#pf-ok').click(); pg_.wait_for_timeout(1200)
ok(gm.evaluate(f"()=>seatFields().some(f=>f.values.map(v=>valToName(v)||v).includes('{S}'))"), 'Bao Ve tu chon tren dien thoai -> tu dien vao man hinh quan tro')
gm.evaluate("()=>{ state.players=Object.entries(state.dealAssignment).map(([n,r],i)=>({id:'p_'+i,name:n,roleId:r,initialRoleId:r,isAlive:true})); state.dayCount=1; switchView('view-night-result'); }")
gm.wait_for_timeout(2500)
ok(all('Trời sáng' in ' '.join(P[n].evaluate("()=>chatList.map(m=>m.text||'')")) for n in names), 'troi sang: ca lang nhan thong bao')
gm.evaluate("()=>{state.gameOver=true; state.gameResult='DÂN LÀNG THẮNG!'; switchView('view-end');}"); gm.wait_for_timeout(2500)
ok(all('DÂN LÀNG THẮNG' in P[n].locator('#g-end').inner_text() for n in names), 'het van: moi nguoi thay phe thang')
ok(not errs, 'khong co loi JavaScript' + (': ' + ' | '.join(errs[:3]) if errs else ''))
b.close(); p.stop()
print('\nTất cả đạt' if not bad else f'\n{bad} mục hỏng'); sys.exit(1 if bad else 0)
