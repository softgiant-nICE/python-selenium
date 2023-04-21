import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import numpy as np
import time, random, threading
sqrt3 = np.sqrt(3)
sqrt5 = np.sqrt(5)


CONCURRENT_SELENIUM_WINDOWS = 1
PROXY_FILE = 'selenium_proxy.txt'

def wind_mouse(start_x, start_y, dest_x, dest_y, G_0=3, W_0=4, M_0=10, D_0=20, move_mouse=lambda x,y: None):
	'''
	WindMouse algorithm. Calls the move_mouse kwarg with each new step.
	Released under the terms of the GPLv3 license.
	G_0 - magnitude of the gravitational fornce
	W_0 - magnitude of the wind force fluctuations
	M_0 - maximum step size (velocity clip threshold)
	D_0 - distance where wind behavior changes from random to damped
	'''
	if G_0 == None:
		G_0 = abs(start_x - dest_x) // 10
	if W_0 == None:
		W_0 = abs(start_x - dest_x) // 33
	if M_0 == None:
		M_0 = abs(start_x - dest_x) // 7
	if D_0 == None:
		D_0 = abs(start_x - dest_x) // 9
	current_x,current_y = start_x,start_y
	v_x = v_y = W_x = W_y = 0
	while (dist:=np.hypot(dest_x-start_x,dest_y-start_y)) >= 1:
		W_mag = min(W_0, dist)
		if dist >= D_0:
			W_x = W_x/sqrt3 + (2*np.random.random()-1)*W_mag/sqrt5
			W_y = W_y/sqrt3 + (2*np.random.random()-1)*W_mag/sqrt5
		else:
			W_x /= sqrt3
			W_y /= sqrt3
			if M_0 < 3:
				M_0 = np.random.random()*3 + 3
			else:
				M_0 /= sqrt5
		v_x += W_x + G_0*(dest_x-start_x)/dist
		v_y += W_y + G_0*(dest_y-start_y)/dist
		v_mag = np.hypot(v_x, v_y)
		if v_mag > M_0:
			v_clip = M_0/2 + np.random.random()*M_0/2
			v_x = (v_x/v_mag) * v_clip
			v_y = (v_y/v_mag) * v_clip
		start_x += v_x
		start_y += v_y
		move_x = int(np.round(start_x))
		move_y = int(np.round(start_y))
		if current_x != move_x or current_y != move_y:
			#This should wait for the mouse polling interval
			move_mouse(current_x:=move_x,current_y:=move_y)
	return current_x,current_y

capLock = threading.Lock()
solvedCaptchas = []
CAPTCHA_VALID_FOR = 90
MAXIMUM_TOKENS = 50

def removeExpiredCaptchas():
	global solvedCaptchas
	with capLock:
		solvedCaptchas = [x for x in solvedCaptchas if x['time'] + CAPTCHA_VALID_FOR >= time.time()]

def addSolvedCaptcha(generatedAt, response):
	global solvedCaptchas
	with capLock:
		solvedCaptchas = [x for x in solvedCaptchas if x['time'] + CAPTCHA_VALID_FOR >= time.time()]
		solvedCaptchas.append({'time': generatedAt, 'captcha': response})

def getCaptcha():
	global solvedCaptchas
	while True:
		if len(solvedCaptchas) != 0:
			with capLock:
				return solvedCaptchas.pop(0)
		time.sleep(0.1)

def setCookie(driver, url, name, value):
	driver.execute_cdp_cmd('Network.setCookie', {'name': name, 'value': value, 'url': url})

def setProxy(driver, host, port, user, pw):
	driver.execute_script("chrome.runtime.sendMessage('iglplagiedbbdhmnnhejknmiglccjcka', {modifyProxy: ['" + host + "', " + port + ", '" + user + "', '" + pw + "']}, function(response) {});");

def startDriver():
	options = uc.ChromeOptions()
	performanceOptions = ["--disable-background-timer-throttling", "--disable-backgrounding-occluded-windows", "--disable-breakpad", "--disable-component-extensions-with-background-pages", "--disable-dev-shm-usage"]
	options.add_argument(''.join(performanceOptions))
	options.add_argument('--window-size=1920,1080')
	options.add_extension('./proxy.crx')
	options.add_experimental_option("mobileEmulation", { "deviceName": "Pixel 2" })
	options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
	return uc.Chrome(chrome_options=options)

def runCaptcha(driver, host, port, user, pw):
	try:
		driver.set_page_load_timeout(60)
		domainList = ['stake.bet', 'stake.games', 'stake.bz', 'staketr.com', 'staketr2.com', 'staketr3.com', 'staketr4.com']
		selectedDomain = random.choice(domainList)
		driver.get(f'https://{selectedDomain}/_app/assets/index-b4fa1b2e.css')
		#setCookie(driver, f'https://{selectedDomain}/', 'session', '62356d99d1f38e33fb3e2bf8460049a04094176e7e86af64c24392fb22ffdab03530bcfb26ce40261441746a0a9123e9')
		setProxy(driver, host, port, user, pw)

		delayBetweenPages = 0
		time.sleep(delayBetweenPages)

		maxRetries = 0

		while True:
			print('Started')
			#driver.get(f'https://{selectedDomain}/settings/offers?type=drop&code=43342&modal=redeemBonus&currency=btc')
			# driver.get(f'https://{selectedDomain}/notifications/overview?tab=login&modal=auth')
			driver.execute_script("window.open('https://{selectedDomain}/notifications/overview?tab=login&modal=auth','_blank')")
			#driver.execute_script("document.querySelectorAll('.variant-success.lineHeight-base.size-medium.spacing-normal.weight-semibold.align-center.square.svelte-1x36jdy')[1].scrollIntoView(false)")


			pageLoadsDelay = 0
			time.sleep(pageLoadsDelay)
			#print('Search')
			timeout = 5
			wait = WebDriverWait(driver, timeout)
			try:
				wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="h-captcha"]/iframe')))
				#wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="svelte"]/div[1]/div[2]/div[2]/div/div/form/button')))
				
				driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="h-captcha"]/iframe'))
				start = time.time()
				while time.time() < start + timeout:
					if len(driver.execute_script('return window.performance.getEntriesByType("resource")')) < 2:
						time.sleep(0.25)
						continue
					#print('Found')
					break
				if len(driver.execute_script('return window.performance.getEntriesByType("resource")')) < 2:
					print(len(driver.execute_script('return window.performance.getEntriesByType("resource")')))
					raise ValueError("hcaptcha not loaded")
			except:
				print('Button or hcaptcha not loaded')
				if (maxRetries == 0):
					break
				maxRetries -= 1
				continue
			#print('Found')

			driver.switch_to.default_content()
			
			time.sleep(3)
			driver.find_element(By.XPATH, '//*[@id="svelte"]/div[1]/div[2]/div[2]/div/div/div[1]/div/form/label[1]/div/div[1]/input').send_keys('FDo8o7cUj')
			time.sleep(3)
			driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[2]/div[2]/div/div/div/div/form/label[2]/div/div[1]/input').send_keys('KJbDI2rRuZMs')
			time.sleep(3)
			
			# startButton = driver.find_element(By.XPATH, '//*[@id="scrollable"]/div/div/div/div/div[2]/div/div/div/div[2]/div[2]/div/div/section[2]/div[3]/button')
			# buttonToClick = driver.find_element(By.XPATH, '//*[@id="svelte"]/div[1]/div[2]/div[2]/div/div/form/button')

			# startPos = {'x': random.randint(startButton.location['x'] + 15, startButton.location['x'] + startButton.size['width'] - 15), 'y': random.randint(startButton.location['y'] + 15, startButton.location['y'] + startButton.size['height'] - 15)}
			# endPos = {'x': random.randint(buttonToClick.location['x'] + 15, buttonToClick.location['x'] + buttonToClick.size['width'] - 15), 'y': random.randint(buttonToClick.location['y'] + 15, buttonToClick.location['y'] + buttonToClick.size['height'] - 15)}

			# print('Setting to start')
			# action = ActionChains(driver, 0)
			# action.move_by_offset(startPos['x'], startPos['y'])
			# action.perform()

			# percentX = abs(endPos['x'] - startPos['x']) // 7
			# percentY = abs(endPos['y'] - startPos['y']) // 4

			# borderPoints = [[startPos['x'], startPos['y']], [random.randint(startPos['x'] - 2*percentX, startPos['x'] - percentX), random.randint(startPos['y'] - 2*percentY, startPos['y'] - percentY)], [random.randint(endPos['x'] - 2*percentX, endPos['x'] - percentX), random.randint(endPos['y'] - 2*percentY, endPos['y'] - percentY)], [random.randint(endPos['x'] + percentX//2, endPos['x'] + percentX), random.randint(endPos['y'] + percentY//2, endPos['y'] + percentY)], [endPos['x'], endPos['y']]]
			# lastXPos = borderPoints[0][0]
			# lastYPos = borderPoints[0][1]
			
			# print('Moving mouse')
			# for i in range(len(borderPoints) - 1):
			# 	#print('##########')
			# 	points = []
			# 	wind_mouse(borderPoints[i][0], borderPoints[i][1], borderPoints[i + 1][0], borderPoints[i + 1][1], move_mouse=lambda x,y: points.append([x,y]))

			# 	for point in points:
			# 		#print(point[0], point[1])
			# 		action.move_by_offset(point[0] - lastXPos, point[1] - lastYPos)
			# 		action.perform()
			# 		mousemovementDelay = 0.012
			# 		time.sleep(mousemovementDelay)
			# 		lastXPos = point[0]
			# 		lastYPos = point[1]

			# 	action.move_by_offset(lastXPos - borderPoints[i + 1][0], lastYPos - borderPoints[i + 1][1])
			# 	action.perform()
			# 	time.sleep(0.148)
			# 	lastXPos = borderPoints[i + 1][0]
			# 	lastYPos = borderPoints[i + 1][1]

			delayBetweenGeneration = 1
			captchaTriggered = driver.execute_script("return window.captchaTriggered")

			while captchaTriggered != True:
				print('Clicking')
				captchaGenTime = time.time()
				driver.find_element(By.XPATH, '//*[@id="svelte"]/div[1]/div[2]/div[2]/div/div/div[1]/div/form/button').click()
				# action.click()
				# action.perform()
				start = time.time()
				while time.time() < start + timeout:
					captchaTriggered = driver.execute_script("return window.captchaTriggered")
					if captchaTriggered == None:
						time.sleep(0.25)
						continue
					break

				if time.time() >= start + timeout:
					break

				if captchaTriggered == False:
					addSolvedCaptcha(captchaGenTime, driver.execute_script("return window.solvedCaptchas")[-1])
					print("Tokens Available:", len(solvedCaptchas))
					driver.execute_script("window.captchaTriggered = undefined")
				time.sleep(delayBetweenGeneration)
			# action.move_to_element_with_offset(startButton, -startButton.location['x'], -startButton.location['y'])
			# action.perform()
			break
		print("Exiting")
	except Exception as e:
		print("Run Captcha")
		print(e)

active = True
driverList = []

def closeAll():
	for i in range(CONCURRENT_SELENIUM_WINDOWS):
		try:
			driverList[i].quit()
		except:
			pass

def run():
	global active, driverList
	active = True

	driverList = []
	thread_list = []
	for i in range(CONCURRENT_SELENIUM_WINDOWS):
		driverList.append(startDriver())
		arg = None
		with open(PROXY_FILE, 'r+') as f:
			arg = f.readline().rstrip()
			data = f.read()
			f.seek(0)
			f.write(data)
			f.truncate()
		if (arg == ""):
			break
		arg = arg.split(':')
		print('Setting proxy')
		thread = threading.Thread(target=runCaptcha, args=(driverList[i], arg[0],arg[1],arg[2],arg[3],))
		thread_list.append(thread)
		thread.start()


	while True:
		if not active:
			for driver in driverList:
				try:
					driver.quit()
				except:
					pass
			return
		arg = None
		with open(PROXY_FILE, 'r+') as f:
			arg = f.readline().rstrip()
			data = f.read()
			f.seek(0)
			f.write(data)
			f.truncate()
		if (arg == ""):
			break
		arg = arg.split(':')
		print('Changing proxy')
		ranThread = False
		while not ranThread and active:
			for i in range(len(thread_list)):
				thread = thread_list[i]
				if not thread.is_alive():
					while len(solvedCaptchas) >= MAXIMUM_TOKENS:
						removeExpiredCaptchas()
						time.sleep(0.1)
					try:
						driverList[i].title
					except:
						if not active:
							return
						driverList[i] = startDriver()
					thread_list[i] = threading.Thread(target=runCaptcha, args=(driverList[i], arg[0],arg[1],arg[2],arg[3],))
					thread_list[i].start()
					ranThread = True
				time.sleep(0.01)

	for thread in thread_list:
		thread.join()
	time.sleep(1500)