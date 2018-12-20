import MySQLdb

def normalize(lst,rev = False):
	mini = min(lst)
	maxi = max(lst)

	nor = []
	
	if rev == False:
		nor = [float(mini)/max(elem,0.00001) for elem in lst]
	else:
		nor = [float(elem)/max(maxi,0.00001) for elem in lst]

	return nor

def getfreqloc(words):
	freq = {}
	locat = {}
	for word in words:
		comd = "SELECT * FROM WORDS WHERE WORD = "+'"'+word+'";'
		cur.execute(comd)
		loc = cur.fetchall()
		if(len(loc) != 0 ):
			wordid = int(loc[0][0])
			comdx = "SELECT * FROM WORD_POS WHERE WORDID = "+str(wordid)
			cur.execute(comdx)
			urls = cur.fetchall()
			for url in urls:
				freq.setdefault(str(url[0]),0)
				locat.setdefault(str(url[0]),1000000000)
				locat[str(url[0])]=min(locat[str(url[0])],int(url[2]))
				freq[str(url[0])]+=1
	if(len(freq)):
		nmf = normalize(freq.values(),True)
	if(len(locat)):	
		nml = normalize(locat.values())

	for i,url in enumerate(freq):
		freq[url] = nmf[i]
		
	for i,url in enumerate(locat):
		locat[url] = nml[i]

	return [freq,locat]

def getdist(words):
	
	found = {}

	for word in words:
		comd = "SELECT * FROM WORDS WHERE WORD = "+'"'+word+'";'
		cur.execute(comd)
		loc = cur.fetchall()
		if(len(loc) != 0 ):
			wordid = int(loc[0][0])
			comdx = "SELECT * FROM WORD_POS WHERE WORDID = "+str(wordid)
			cur.execute(comdx)
			urls = cur.fetchall()
			for url in urls:
				found.setdefault(str(url[0]),{})
				if word in found[str(url[0])]:
					found[str(url[0])][word]=min(found[str(url[0])][word],int(url[2]))
				else:
					found[str(url[0])][word]=int(url[2])
				
	
	dist = {}
	for url in found:
		curt = 0
		lst = [found[url][word] for word in found[url]]
		if(len(lst) <= 1):
			dist[url] = 100000000
		else:			
			for i in range(1,len(lst)):
				curt += abs(lst[i]-lst[i-1])
			dist[url] = curt
	if(len(dist) > 0):
		nm = normalize(dist.values())
    
	for i,url in enumerate(dist):
		dist[url] = nm[i]

	return dist		

def getlinks():
	linkstr = {}
	comd = "SELECT * FROM LINKS"
	cur.execute(comd)
	data = cur.fetchall()
	for link in data:
		linkstr.setdefault(str(link[1]),0)
		linkstr[str(link[1])]+=1
	if(len(linkstr) > 0):
		nm = normalize(linkstr.values(),True)
    
	for i,url in enumerate(linkstr):
		linkstr[url] = nm[i]

	return linkstr


def calpagerank(prank):
	cnt = {}
	inbnd = {}
	trank = {}
	comd = "SELECT * FROM LINKS"
	cur.execute(comd)
	data = cur.fetchall()
	
	for link in data:
		cnt.setdefault(str(link[0]),0)
		cnt[str(link[0])]+=1
		inbnd.setdefault(str(link[1]),{})
		inbnd[str(link[1])][str(link[0])]=1
	for x in range(100):
		if str(x) not in cnt:
			cnt[str(x)] = 0


	trank = {}
	
	for link in inbnd:
		if(cnt[str(link)] == 0):
			continue
		trank.setdefault(int(link),0.15)
		for i in inbnd[link]:
			trank[int(link)]+=(.85)*float(prank[str(i)])/cnt[str(i)]

	for i in range(100):
		if i not in trank:
			prank[str(i)] = 0
		else:
			prank[str(i)] = trank[i]

	return prank

def linkcnt(words):
	freq = {}
	for word in words:
		comd = "SELECT * FROM WORDS WHERE WORD = "+'"'+word+'";'
		cur.execute(comd)
		loc = cur.fetchall()
		if(len(loc) != 0 ):
			wordid = int(loc[0][0])
			comdx = "SELECT * FROM URLWORDS WHERE WORDID = "+str(wordid)
			cur.execute(comdx)
			urls = cur.fetchall()
			for url in urls:
				freq.setdefault(str(url[0]),0)
				freq[str(url[0])]+=1
			
	if len(freq):
		nmf = normalize(freq.values(),True)

		for i,url in enumerate(freq):
			freq[url] = nmf[i]

	return freq


db = MySQLdb.connect("localhost","root","spacebar","ir")
cur = db.cursor()
x = raw_input("ENTER SEARCH TERMS: ")
words = x.split()
wordloc = getfreqloc(words)
prank = dict([(str(i),0) for i in range(0,100)])
print("THE CONVERGENCE OF THE PAGE RANK SCORES CAN BE OBSERVED HERE")
for i in range(100):
	prank = calpagerank(prank)
	print([(prank[str(j)]) for j in range(96,100)])


print("THE FINAL PAGE RANK SCORES OF ALL THE PAGES ARE: ")

for i in range(100):
	print(i, prank[str(i)])

ranking = [wordloc[0],wordloc[1],getdist(words),getlinks(),prank,linkcnt(words)]
#print(ranking[0])
#print(ranking[1])
#print(ranking[2])
wts = [5.0,1.0,1.0,0.2,0.5,20]
urlrank = {}
for i,param in enumerate(ranking):
	for url in param:
		urlrank.setdefault(url,0)
		urlrank[url]+=wts[i]*param[url]
scores = [(urlrank[url],url) for url in urlrank]	
scores.sort()
scores.reverse()
print("THE RESULTS ARE:")
for i in range(min(10,len(scores))):
	comd = "SELECT * FROM URLS WHERE URLID ="+str(scores[i][1])
	cur.execute(comd)
	print(cur.fetchall()[0][1], scores[i][0])




