## Right now the script spams the login button untill hCaptcha pops and when hCaptcha pops it reloads page, this is what I want instead:

### - Make it open "/notifications/overview?tab=login&modal=auth" in a new tab instead
### - Use different random characters for login & password inputs
### - It will spam "Sign In" button 
### - When hCaptcha pops or no token returned after 3(X) seconds (I need to be able to edit this easy):
### - It will click "Register" button/tab ("Register Button-Tab.png")
### - Clear cookies
### - Add a 1 second delay (I need to be able to edit this easy)
### - Then click "Login" button/tab ("Login Button-Tab.png")
### - And start spam again the "Sign In" button

### - If page is not loaded after 10(X) seconds, it will reload the page (Or close the tab, open a new one and reload the page)
### - App will no longer remove proxies after use:
### - It will use proxies from top to bottom for each CONCURRENT_SELENIUM_WINDOWS
