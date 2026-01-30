"""Backfill synthetic users' Profile.faculty from admin_credentials_voters.txt

Maps the `department` field in the credentials file to `Profile.faculty`.
Run via: `python manage.py shell < scripts/backfill_profile_faculty.py`
"""
import os
from django.contrib.auth import get_user_model

in_path = os.path.join(os.getcwd(), 'admin_credentials_voters.txt')
if not os.path.exists(in_path):
    print('Missing', in_path)
else:
    from django.db import transaction
    User = get_user_model()
    with open(in_path) as fh:
        content = fh.read()
    parts = [p.strip() for p in content.split('---') if p.strip()]
    updated = 0
    with transaction.atomic():
        for p in parts:
            d = {}
            for line in p.splitlines():
                if ':' in line:
                    k,v = line.split(':',1)
                    d[k.strip()] = v.strip()
            username = d.get('username')
            dept = d.get('department')
            if not username or not dept:
                continue
            u = User.objects.filter(username__iexact=username).first()
            if not u:
                continue
            try:
                from accounts.models import Profile
                p = Profile.objects.filter(user=u).first()
                if not p:
                    # create a profile if missing
                    p = Profile.objects.create(user=u)
                # map 'department' -> 'faculty' field
                if getattr(p, 'faculty', None) != dept:
                    setattr(p, 'faculty', dept)
                    p.save(update_fields=['faculty'])
                    updated += 1
            except Exception as exc:
                print('Error for', username, exc)
    print('Updated profiles:', updated)
