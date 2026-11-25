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
link=link.replace(link.split('?')[0], 'file://'+ROOT+'/play.html')
names=['Một','Hai','Ba','Bốn','Năm','Sáu']; P={}
for n in names:
    c,pg=ctx(); pg.goto(link+('&' if '?' in link else '?')+'ws='+WS); pg.wait_for_timeout(300); pg.fill('#in-name',n); pg.locator('#btn-join').click(); pg.wait_for_timeout(300); P[n]=pg
gm.wait_for_timeout(800); print('   so nguoi vao phong:', gm.locator('.ol-p').count())
gm.locator('#online-foot .ol-btn.main').click(); gm.wait_for_timeout(900)
gm.evaluate("()=>{ROLES_DB.forEach(r=>state.deck[r.id]=0); Object.assign(state.deck,{wolf:1,seer:1,guard:1,cursed:1,villager:2}); renderDeck();}")
gm.locator('#view-deck .bottom-safe button').last.click(); gm.wait_for_timeout(1000)
if gm.locator('#deck-warn-modal:not(.hidden)').count(): gm.locator('#deck-warn-modal button').last.click(); gm.wait_for_timeout(500)
asg=gm.evaluate("()=>state.dealAssignment"); print('   chia bai:', asg)
gm.evaluate("()=>{Object.keys(state.dealAssignment).forEach(n=>state.dealViewed[n]=1); onlineSaveDeal(); renderDealView();}")
gm.locator('#btn-deal-start').click(); gm.wait_for_timeout(800)
if gm.locator('#deal-warn-overlay').count(): gm.locator('#deal-warn-overlay button', has_text='Vẫn bắt đầu').click(); gm.wait_for_timeout(400)
gm.wait_for_timeout(1300); [x.click() for x in gm.locator('.tk-ov .tk-close').all()]
C=[n for n in names if asg[n]=='cursed'][0]; W=[n for n in names if asg[n]=='wolf'][0]; V=[n for n in names if asg[n]=='villager']; dead=V[0]; alive=V[1]
gm.evaluate(f"""()=>{{ state.players=Object.entries(state.dealAssignment).map(([n,r],i)=>({{id:'p_'+i,name:n,roleId:(n==='{C}'?'wolf':r),initialRoleId:r,isAlive:n!=='{dead}'}}));
  state.eventLog=[{{title:'Đêm 1', content:'<b>Sói</b> cắn {dead}<br>Tiên Tri soi {W}: <span>Phe Sói</span>'}}, {{title:'Ngày 1', content:'Không ai bị treo cổ'}}]; state.dayCount=1; switchView('view-day-discuss'); }}""")
gm.wait_for_timeout(3500)
for n in names: P[n].evaluate("()=>document.querySelectorAll('.sky-ov,.death-ov').forEach(x=>x.remove())")
pd=P[dead]; rd=pd.evaluate("()=>revealData && {roles:revealData.roles.length, log:revealData.log.length, c:revealData.roles.find(r=>r.r0)}")
ok(rd and rd['roles']==6 and rd['log']==2, f'nguoi chet ({dead}) nhan du vai 6 nguoi + 2 dong nhat ky: {rd}')
ok(rd and rd['c'] and rd['c']['r0']=='Kẻ Bị Nguyền' and rd['c']['r']=='Ma Sói', f'doi vai hien dung: {rd and rd["c"]}')
lab=pd.locator('#ring .rrole').count(); ok(lab==6, f'vong lang cua nguoi chet: ten vai duoi ca {lab}/6 ghe')
ok(all(P[n].evaluate("()=>revealData")==None and P[n].locator('#ring .rrole').count()==0 for n in names if n!=dead), 'NGUOI SONG khong nhan gi, khong thay vai ai')
ok(pd.locator('.ghost-bar .rev-btn').is_visible(), 'thanh Linh hon co nut "📜 Vai & nhat ky"')
pd.locator('.ghost-bar .rev-btn').click(); pd.wait_for_timeout(500)
rt=pd.locator('#rev-body').inner_text()
ok(pd.locator('#rev-body .rv-row').count()==6 and 'Kẻ Bị Nguyền ➡ Ma Sói' in rt and '(bạn)' in rt, 'tab Vai moi nguoi: 6 dong, co "Ke Bi Nguyen ➡ Ma Soi", danh dau (ban)')
pd.screenshot(path=os.path.join(__import__('tempfile').gettempdir(), 'rev_roles.png'))
pd.locator('#rv-log').click(); pd.wait_for_timeout(300); lt=pd.locator('#rev-body').inner_text()
ok('Đêm 1' in lt and 'Ngày 1' in lt and '<b>' not in lt and lt.index('Ngày 1') < lt.index('Đêm 1'), 'tab Nhat ky: co Dem 1 + Ngay 1 (moi nhat o tren), da bo ma HTML')
pd.screenshot(path=os.path.join(__import__('tempfile').gettempdir(), 'rev_log.png'))
pd.keyboard.press('Escape'); pd.wait_for_timeout(300)
pd.reload(wait_until='load'); pd.wait_for_timeout(3500)
ok(pd.evaluate("()=>!!revealData && revealData.roles.length")==6, 'tai lai trang -> van con (server giu lai)')
gm.evaluate(f"()=>{{ state.players.find(p=>p.name==='{dead}').isAlive=true; }}"); gm.wait_for_timeout(2500)
ok(pd.evaluate("()=>revealData")==None and pd.locator('#ring .rrole').count()==0, f'quan tro cho {dead} song lai -> THU HOI: het vai, het nhat ky')
print('JS errors:', len(errs)); [print('  ', e) for e in errs[:3]]
b.close(); p.stop()
