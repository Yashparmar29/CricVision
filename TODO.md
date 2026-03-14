# Resend Verification Page Fix - TODO

## Plan Implementation Steps

### 1. Update app.py ✅ Pending
- [ ] Fix /resend-verification POST handler to render resend_verification.html with success/error messages instead of redirecting to login.html

### 2. Update login.html
- [ ] Add "Resend verification email" link for unverified users or after failed login

### 3. Update signup.html  
- [ ] Add resend link in success message after account creation

### 4. Testing
- [ ] Test form submission shows success message on same page
- [ ] Test invalid email shows error on same page
- [ ] Verify email sending works (configure SMTP first)

### 5. Optional Improvements
- [ ] Configure real SMTP credentials
- [ ] Add rate limiting for resend requests
- [ ] Add expiration/checks for verification tokens

**Current Status:** Starting implementation...
