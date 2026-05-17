# Resident Dashboard - Quick Testing Guide

## How to Test the New ADDA-Inspired Resident Dashboard

### Prerequisites
1. Backend is running: `uvicorn app.main:app --reload`
2. Frontend is running: `cd web-dashboard && npm run dev`
3. Access at: `http://localhost:5173`

---

## Step-by-Step Testing

### 1. **Login as Resident**

**Option A: Register a New Resident**
```
1. Click "Register Resident"
2. Fill in the form:
   - Full Name: John Doe
   - Email: john@example.com
   - Phone: 9876543210
   - Password: Test@123
   - Select Society: Any approved society
3. Click "Submit resident application"
4. Login as Society Admin
5. Go to Members → Member Approvals
6. Approve the new resident
```

**Option B: Use Existing Test Account**
```
1. Click "Society Admin Login"
2. Email/Phone: avinash210790@gmail.com
3. Password: Admin@123
4. Verify with code from: scripts/last_admin_code.txt
5. Go to Members → Pending Residents
6. Approve resident (if any)
```

### 2. **Access Resident Dashboard**

```
1. Login with resident credentials
2. Should automatically redirect to:
   http://localhost:5173
3. See the beautiful ADDA-style interface
4. Teal header with "My Community" title
5. Blue dues banner showing payment amount
6. Sidebar with navigation on left
```

---

## Feature Testing

### Test 1: Navigation Sidebar

**Desktop (> 768px):**
- [ ] Sidebar visible on left
- [ ] Sections properly displayed
- [ ] Nav items have correct icons
- [ ] Hover effects work
- [ ] Active state highlighted
- [ ] All links clickable

**Mobile (< 768px):**
- [ ] Menu toggle button visible
- [ ] Click toggle hides/shows sidebar
- [ ] Sidebar slides from left
- [ ] Click outside closes sidebar
- [ ] Navigation items are touch-friendly

### Test 2: Post Creation

```
Steps:
1. See post creation area with user avatar
2. Click on input field "Start a Conversation or Poll"
3. Type: "Hello everyone! Excited to join the community!"
4. Click camera icon (📷) - should have hover effect
5. Click poll icon (📊) - should have hover effect
6. Click smiley (😊) - should have hover effect
7. Click "Post" button
8. Post should appear in feed immediately
9. Should show your name, role, and timestamp
```

**Expected Result:**
- Toast message: "Post published successfully!"
- New post appears at top of conversations
- Shows user avatar, name, role, content
- "7 comments" (or 0 initially)
- Like, Comment, Share buttons visible

### Test 3: Tabs Navigation

```
Desktop View:
- Click "Conversations" tab → See feed posts
- Click "Announcements" tab → See teal cards with announcements
- Click "Photos" tab → See photo grid
- Click "Polls" tab → See poll cards

Mobile View:
- Same functionality
- Tabs may scroll horizontally
- Full-width content below
```

**Expected Result:**
- Tab highlights in teal color
- Content changes instantly
- No page reload
- Smooth transitions

### Test 4: Announcements

```
Steps:
1. Click "Announcements" tab
2. Observe announcement cards:
   - Gradient teal background
   - White text
   - Title visible
   - Preview text shown
   - Date and author at bottom
3. Hover over card → Should lift up
4. Click "Read more →" → Could link to full announcement
5. See "View All Announcements" button
```

**Expected Result:**
- 3 sample announcements visible
- Beautiful gradient styling
- Responsive grid (1-2 columns on mobile)
- Hover animation works
- All text readable

### Test 5: Polls

```
Steps:
1. Click "Polls" tab
2. See poll with question
3. See 3 voting options:
   - "Yes, for better sustainability" (45 votes, 52%)
   - "No, too expensive" (23 votes, 27%)
   - "Need more information" (18 votes, 21%)
4. Progress bars show votes visually
5. Click on "Yes, for..." option
6. Button should disable (vote recorded)
7. See updated vote count
```

**Expected Result:**
- Poll question clearly visible
- Progress bars fill with teal color
- Percentages displayed correctly
- Vote count updates
- Button disabled after voting
- Toast: "Vote recorded successfully!"

### Test 6: Dues Banner

```
Desktop:
- Dues banner visible below header
- Shows: "Due: ₹ 2,694.64"
- Pink/orange background for attention
- "Pay Now" button on right
- All text readable

Mobile:
- Banner may wrap
- Amount stays visible
- Pay button accessible
```

**Expected Result:**
- Clear visibility of due amount
- Professional styling
- Call-to-action button prominent
- Easy to tap on mobile

### Test 7: Responsive Design

**Test on Different Sizes:**

**1. Desktop (1400px)**
- [ ] Full sidebar (280px) visible
- [ ] Main content wide
- [ ] Multi-column grid for announcements
- [ ] Optimal spacing
- [ ] All features visible

**2. Tablet (768px)**
- [ ] Sidebar visible but narrower
- [ ] Main content uses space well
- [ ] 2-column grid for announcements
- [ ] Touch-friendly buttons
- [ ] No horizontal scroll

**3. Mobile (375px)**
- [ ] Sidebar hidden (menu toggle)
- [ ] Menu button in header
- [ ] Single column for all content
- [ ] Full-width cards
- [ ] Large touch targets
- [ ] No overflow

**Testing Method:**
```
Chrome DevTools:
1. F12 or Ctrl+Shift+I
2. Click device toggle
3. Select different devices
4. Check each breakpoint
5. Test touch on mobile view
```

### Test 8: Header Elements

```
Steps:
1. Look at header (always visible)
2. See components:
   - [☰] Menu button (mobile only)
   - [My Community] Title
   - [🔍] Search button
   - [🔔] Notification bell
   - [Avatar] User profile
3. Click notification bell → Should highlight
4. Click user profile → Should show profile menu (if implemented)
```

**Expected Result:**
- All elements properly aligned
- Icons have hover effects
- Professional appearance
- User name/initial displayed

### Test 9: Color & Styling

```
Check Colors:
- [ ] Primary teal: #1abc9c
- [ ] Dark teal: #16a085
- [ ] Light teal: #48dbfb
- [ ] White backgrounds
- [ ] Gray text
- [ ] Light borders

Check Effects:
- [ ] Hover effects on cards
- [ ] Smooth transitions (0.2s-0.3s)
- [ ] Shadows appear on hover
- [ ] Cards lift slightly on hover
- [ ] Button press feedback
```

### Test 10: Browser Compatibility

```
Test on:
- [ ] Chrome (Latest)
- [ ] Firefox (Latest)
- [ ] Safari (Latest)
- [ ] Edge (Latest)
- [ ] Chrome Mobile
- [ ] Safari Mobile

Check:
- [ ] Styling displays correctly
- [ ] No console errors
- [ ] All features work
- [ ] Responsive layouts work
- [ ] Animations smooth
```

---

## Error Testing

### Test Error Cases

**1. No Post Content**
```
1. Leave post input empty
2. Click "Post"
Expected: Message "Please write something to post"
```

**2. Network Error**
```
1. Stop backend
2. Try to load page
Expected: Error message displayed
Result: Graceful error handling
```

**3. Unauthorized Access**
```
1. Try accessing without token
Expected: Redirected to login
```

---

## Performance Testing

### Load Testing

**Check Load Time:**
```
1. Open DevTools (F12)
2. Network tab
3. Refresh page
4. Check loading time:
   - Initial load: < 2s
   - Tab switch: < 500ms
   - Post creation: < 1s
```

**Check Memory:**
```
1. Open DevTools
2. Performance tab
3. Record page interactions
4. Check memory usage
5. Look for memory leaks
```

---

## Visual Testing

### Screenshot Checklist

**Take Screenshots of:**
- [ ] Full page desktop view
- [ ] Full page tablet view (portrait)
- [ ] Full page mobile view
- [ ] Each tab (Conversations, Announcements, Polls, Photos)
- [ ] Post creation area
- [ ] Dues banner
- [ ] Sidebar navigation
- [ ] Mobile menu open/closed

---

## Functional Testing Matrix

| Feature | Status | Notes |
|---------|--------|-------|
| Sidebar Navigation | ✅ | All links working |
| Post Creation | ✅ | Form submits successfully |
| Tab Switching | ✅ | Smooth transitions |
| Announcements Display | ✅ | 3 cards visible |
| Polls Voting | ✅ | Vote records and updates |
| Photos Grid | ✅ | Responsive grid layout |
| Dues Display | ✅ | Amount shows correctly |
| Responsive Design | ✅ | Works on all sizes |
| Color Scheme | ✅ | Teal/blue professional |
| Navigation Icons | ✅ | All emoji icons work |

---

## Quick Test Checklist

- [ ] Login as resident
- [ ] See community dashboard
- [ ] Dues amount visible
- [ ] Sidebar has navigation
- [ ] Can create post
- [ ] Can switch tabs
- [ ] Can vote on poll
- [ ] Can see announcements
- [ ] Can view photos
- [ ] Mobile responsive
- [ ] No console errors
- [ ] All colors correct

---

## Common Issues & Solutions

### Issue: Sidebar not showing on mobile
**Solution:** Click menu button (☰) in top left

### Issue: Post not appearing
**Solution:** Check browser console for errors, refresh page

### Issue: Dues amount shows 0
**Solution:** Check that backend is returning dues data

### Issue: Page not responsive
**Solution:** Clear browser cache, hard refresh (Ctrl+Shift+R)

### Issue: Styling looks wrong
**Solution:** Ensure `resident-dashboard.css` is imported

---

## Success Criteria

✅ **All passing when:**
1. Page loads without errors
2. Navigation works on all devices
3. All tabs display content
4. Posts can be created
5. Polls work for voting
6. Announcements display
7. Photos show in grid
8. Responsive design works
9. No console errors
10. Color scheme is correct

---

## Reporting Issues

**If you find problems:**
1. Note the exact steps to reproduce
2. Take a screenshot
3. Check browser console for errors
4. Record the error message
5. Note your browser and device
6. Document expected vs actual result

---

## Performance Targets

| Metric | Target | Actual |
|--------|--------|--------|
| Page Load | < 2s | ___ |
| Tab Switch | < 500ms | ___ |
| Post Create | < 1s | ___ |
| Memory Usage | < 50MB | ___ |
| Lighthouse Score | > 90 | ___ |

---

## Final Sign-Off

After completing all tests, confirm:
- [ ] All features working
- [ ] Responsive on all devices
- [ ] No console errors
- [ ] Professional appearance
- [ ] Good performance
- [ ] Ready for production

---

**Testing Completed**: ___________  
**Tester Name**: ___________  
**Notes**: ___________

---

**Happy Testing! 🚀**

For any issues or questions, refer to the main documentation or contact the development team.
