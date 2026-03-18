# Remove Email Verification Features - Progress Tracker

## Plan Summary
- Delete dedicated verification template
- Remove all verification logic from app.py (model fields, functions, routes, checks, config, imports)
- Remove resend links from login/signup templates
- Test functionality post-removal

## Steps Checklist

### 1. Delete templates/resend_verification.html [ ]
### 2. Edit app.py - Remove verification-related code [ ]
   - Remove User model fields: is_verified, verification_token
   - Remove send_verification_email() function
   - Remove routes: /verify/<token>, /resend-verification
   - Remove all is_verified checks (login, upload, dashboard, settings)
   - Remove MAIL_* config
   - Remove email imports (smtplib, email.mime)
   - Update signup(): no email send, direct login possible
### 3. Edit templates/login.html - Remove resend link [ ]
### 4. Edit templates/signup.html - Remove resend link [ ]
### 5. Test: Signup, login, upload without verification [ ]
### 6. DB Migration if needed (check db_init.py) [ ]
### 7. Verify no errors, update TODO [ ]

**Next Step: Delete resend_verification.html**
