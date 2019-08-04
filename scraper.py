from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool
import multiprocessing as mp
import itertools,requests,csv

def get_content(place,url):
	url+=place
	not_applicable = "N/A"
	city = state = country = weather = best_time = duration = not_applicable
	about = visit = airport = events = more_about = reach = not_applicable
	city = place.split("/")[-2].title()
	try:
		page_response = requests.get(url, timeout=10)
		soup = BeautifulSoup(page_response.content, "lxml")
	except:
		# raise
		print("Could not connect, check your internet !")
		return
	else:
		links = soup.findAll('a',attrs={'class':"smallerText"})
		for link in links:
			if ("country" in link['href']):
				country = link['href'].split("/")[-2].title()
			elif ("state" in link['href']):
				state = link['href'].split("/")[-2].title()
		
		# spans = soup.find('span',attrs={'class':"currentWeather"})
		# print(spans.contents)
		# ps = soup.findAll('p',attrs={'class':"objText"})
		# for p in ps:
		# 	print(p,"\n------------------\n")		
		
		for br in soup.find_all('br'):
			br.extract()
		for em in soup.find_all('em'):
			em.extract()
		for img in soup.find_all('img'):
			img.extract()
		for span_tag in soup.findAll('span'):
			span_tag.unwrap()
		for a in soup.find_all('a'):
			a.extract()

		ps = soup.findAll('p',attrs={'class':"objText"})
		for p in ps:
			try:
				temp = ''.join(p)
			except:
				continue
			else:
				if ("Ideal duration" in temp):
					duration = temp.split("Ideal duration:")[1].strip()
				elif ("Best time:" in temp):
					best_time = temp.split("Best time:")[1].strip().split("\n")[0]
				elif ("Nearest Airport:" in temp):
					airport = temp.split("Nearest Airport:")[1].strip().split("\n")[0]

		
		ps = soup.findAll('p',attrs={'class':"textColor infoSpace"})
		for p in ps[:-2]:
			about += p.contents[0].replace("\xa0"," ")
			about = about.replace(not_applicable,"").strip()

		reach_url= url+"how-to-reach.html"
		page_response = requests.get(reach_url, timeout=10)
		soup1 = BeautifulSoup(page_response.content, "lxml")
		for span in soup1.find_all('span'):
			span.extract()
		for i in soup1.find_all('i'):
			i.extract()
		

		ps = soup1.findAll('p',attrs={'class':"textColor infoSpace"})
		for p in ps:
			try:
				reach += ''.join(p.contents).replace("\xa0"," ")
			except:
				continue
			else:
				reach = reach.replace(not_applicable,"").strip()

		divs = soup.findAll('div',attrs={'class':"textColor infoSpace"})
		for div in divs[:-1]:
			try:
				more_about += div.contents[0].replace("\xa0"," ")
			except:
				continue
			else:
				more_about = more_about.replace(not_applicable,"").strip()

		visit_url = url+"sightseeing-and-things-to-do.html"
		page_response = requests.get(visit_url, timeout=10)
		soup2 = BeautifulSoup(page_response.content, "lxml")
		
		hs = soup2.findAll('h2',attrs={'class':"ptvObjective"})
		for h in hs:
			visit += h.contents[0].split(".")[1].strip()+","
			visit = visit.replace(not_applicable,"").strip()


	data = [city,visit,state,country,weather,best_time,duration,about,airport,events,more_about,reach]
	# data = [city,state,country]
	print("Writing",city)
	return (data)


def get_places(places,url):

	print("Generating list of places ...")
	
	url+="/explore/"
	try:
		page_response = requests.get(url, timeout=10)
		soup = BeautifulSoup(page_response.content, "html.parser")
	except:
		# raise
		print("Could not connect, check your internet !")
		return
	else:
		divs = soup.findAll('div',attrs={'class':"result"})
		for div in divs:
			places.append(div.find('a')['href'])
		# print(links)
	print("Done!",len(places),"Found.")


def main():
	url = "https://www.holidify.com"
	schema = ["City Name", "Places to Visit in the city", "State","Country","Weather","Best time","Ideal duration","About","Nearest Airport", "Upcoming events", "More on City", "How to reach"]
	places = []
	get_places(places,url)
	# print(places)
	# get_content("/places/coorg/",url)

	batch_size = 2*mp.cpu_count()-1
	print("Number of operable threads: ",batch_size+1)

	with Pool(processes=batch_size) as pool:
		csv_data = (pool.starmap(get_content, zip(places , itertools.repeat(url))))
	# print(csv_data)
	with open('holidify.csv', 'w', newline='') as csvFile:
	    writer = csv.writer(csvFile)
	    writer.writerow([x for x in schema])
	    writer.writerows(csv_data)
	print("'holidify.csv' Saved!")



if __name__ == '__main__':
	main()