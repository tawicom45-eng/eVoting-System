# Verify logins for synthetic voters and inspect profiles/departments
from django.test import RequestFactory
import json, re, os
from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.db import SessionStore
from evoting_system import pages

rf = RequestFactory()
User = get_user_model()

in_path = os.path.join(os.getcwd(), 'admin_credentials_voters.txt')
blocks = []
if not os.path.exists(in_path):
    print('MISSING:', in_path)
else:
    with open(in_path, 'r') as fh:
        content = fh.read()
    parts = [p.strip() for p in content.split('---') if p.strip()]
    for p in parts:
        d = {}
        for line in p.splitlines():
            if ':' in line:
                k,v = line.split(':',1)
                d[k.strip()] = v.strip()
        if 'username' in d and 'password' in d:
            blocks.append(d)

print('Parsed blocks:', len(blocks))

# Try to detect Department model
dept_model = None
for candidate in ('departments.models','academics.models','accounts.models','profiles.models','core.models'):
    try:
        mod = __import__(candidate, fromlist=['Department'])
        if hasattr(mod, 'Department'):
            dept_model = getattr(mod, 'Department')
            print('Found Department model at', candidate)
            break
    except Exception:
        pass

# Regex checks for institution_id format
pattern1 = re.compile(r'^U\d{4}/\d{5}$')
pattern2 = re.compile(r'^STU/\d{4}/\d{4}$')
pattern_generic = re.compile(r'^[A-Za-z0-9/_\-]{3,64}$')

success_total = 0
fail_total = 0
per_user = []

for idx, b in enumerate(blocks, start=1):
    username = b.get('username')
    email = b.get('email')
    password = b.get('password')
    inst = b.get('institution_id')
    tried = []
    ok = False
    resp_data = None
    for ident in (username, email, inst):
        if not ident:
            continue
        payload = json.dumps({'identifier': ident, 'password': password})
        # Build a WSGI request with a session so login() can succeed
        req = rf.post('/api/login/', data=payload, content_type='application/json')
        # vary REMOTE_ADDR to avoid per-IP rate limits during bulk verification
        req.META['REMOTE_ADDR'] = f'127.0.0.{(idx % 250) + 1}'
        req.session = SessionStore()
        req.session.create()
        resp = pages.login_api(req)
        tried.append((ident, getattr(resp, 'status_code', None)))
        try:
            j = json.loads(resp.content.decode('utf-8'))
        except Exception:
            j = {'raw': resp.content[:200].decode('utf-8','replace')}
        if getattr(resp, 'status_code', None) in (200, 201) or j.get('ok') is True:
            ok = True
            resp_data = j
            break
    if ok:
        success_total += 1
    else:
        fail_total += 1
    # inspect profile
    role = None
    dept = None
    profile_exists = False
    try:
        from accounts.models import Profile
        p = Profile.objects.filter(user__username__iexact=username).select_related('user').first()
        if p:
            profile_exists = True
            role = getattr(p, 'role', None)
            dept = getattr(p, 'department', None)
    except Exception:
        # fallback: try to get user and attributes
        try:
            u = User.objects.filter(username__iexact=username).first()
            if u:
                profile_exists = bool(getattr(u, 'profile', None))
                dept = getattr(u, 'department', None)
        except Exception:
            pass
    # department presence check
    dept_in_db = None
    if dept_model and dept:
        try:
            dept_in_db = dept_model.objects.filter(name__iexact=dept).exists()
        except Exception:
            dept_in_db = None
    # id format
    id_ok = bool(pattern_generic.match(inst or '')) and (bool(pattern1.match(inst or '')) or bool(pattern2.match(inst or '')))

    per_user.append({
        'username': username,
        'tried': tried,
        'success': ok,
        'resp': resp_data,
        'profile_exists': profile_exists,
        'role': role,
        'department': dept,
        'dept_in_db': dept_in_db,
        'institution_id': inst,
        'id_format_ok': id_ok,
    })

# write results
out = os.path.join('/app', 'verify_login_results.json')
try:
    with open(out, 'w') as fh:
        import json as _j
        _j.dump({'summary': {'total': len(per_user), 'success': success_total, 'fail': fail_total}, 'users': per_user}, fh, indent=2)
    print('WROTE', out)
except Exception as e:
    print('WRITE_FAILED', e)

# Print concise summary
print('TOTAL', len(per_user), 'SUCCESS', success_total, 'FAIL', fail_total)
# show up to 10 failed samples
fails = [u for u in per_user if not u['success']]
print('Failed sample count:', len(fails))
for u in fails[:10]:
    print(u['username'], 'tried', u['tried'], 'role', u['role'], 'dept', u['department'], 'id_ok', u['id_format_ok'])

# show departments aggregate
from collections import Counter
depts = [u['department'] for u in per_user if u.get('department')]
print('Departments used:', len(set(depts)))
print(Counter(depts).most_common(20))

print('Done')
