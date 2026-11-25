# Chay tat ca bo test luat + online. Co bat ky "❌" hoac loi JavaScript -> thoat ma loi (GitHub bao do).
import subprocess, sys, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
SUITES = ['e2e_core', 'e2e_roles1', 'e2e_roles2', 'e2e_roles3', 'e2e_audit', 'e2e_fix2b', 'e2e_rev', 'e2e_dead2', 'e2e_fix2']
bad = 0
for s in SUITES:
    r = subprocess.run([sys.executable, os.path.join(HERE, s + '.py')], capture_output=True, text=True, timeout=600)
    out = r.stdout + r.stderr
    okc, badc = out.count('✅'), out.count('❌')
    js = re.search(r'JS errors: (\d+)', out); jsn = int(js.group(1)) if js else 0
    crash = r.returncode != 0 or 'Traceback' in out
    status = 'DAT' if not badc and not jsn and not crash else 'HONG'
    print(f"{'✅' if status == 'DAT' else '❌'} {s}: {okc} dung, {badc} sai, loi JS: {jsn}{', SCRIPT LOI' if crash else ''}")
    if status != 'DAT':
        bad += 1; print('\n'.join(l for l in out.splitlines() if '❌' in l or 'Error' in l or 'Traceback' in l)[:3000])
print('Tat ca test luat deu dat' if not bad else f'{bad} bo test hong'); sys.exit(1 if bad else 0)
