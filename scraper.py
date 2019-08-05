# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

# use this if you have desktop
# from multiprocessing import Pool

# use this if you have laptop
from multiprocessing.dummy import Pool

import multiprocessing as mp
import itertools,requests,csv,json

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
		
		scripts = soup.findAll('script')
		for script in scripts:
			if 'dataLayer = ' in script.text:
				temp=script.text.split("countryCode' : '")[1].split("',")[0].title()
				if(len(temp)>0):
					country = temp
				temp = script.text.split("stateCode' : '")[1].split("',")[0].title()
				if(len(temp)>0):
					state = temp
			if '$(function()' in script.text:
				x,y = script.text.split("fetchWeather(")[1].split(");")[0].split(" , ")
				weather_url = "https://www.holidify.com/rest/utility/getWeather.hdfy?latitude="+x+"&longitude="+y
				try:
					response = requests.get(weather_url, timeout=10)
				except:
					pass
				else:
					data = response.json()
					weather = str(round(((data['curTemperature']-32)*5/9),2)) + " deg C"

		events_url = url+"best-time-to-visit.html"
		try:
			page_response = requests.get(events_url, timeout=10)
		except:
			pass
		else:
			soup3 = BeautifulSoup(page_response.content, "lxml")
			hs = soup3.findAll('h4',attrs={'class':"headingForMiddleSection"})
			if (len(hs)>0):
				for h in hs[1:]:
					events += h.contents[0].strip()+","
					events = events.replace(not_applicable,"").strip()
		
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
		try:
			page_response = requests.get(reach_url, timeout=10)
		except:
			pass
		else:
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
		try:
			page_response = requests.get(visit_url, timeout=10)
		except:
			pass
		else:
			soup2 = BeautifulSoup(page_response.content, "lxml")
			hs = soup2.findAll('h2',attrs={'class':"ptvObjective"})
			for h in hs:
				visit += h.contents[0].split(".")[1].strip()+","
				visit = visit.replace(not_applicable,"").strip()


	data = [city,visit,state,country,weather,best_time,duration,about,airport,events,more_about,reach]
	# print(city,state,country,weather,events)
	print("Getting data for",city,"                                  \r\r",end='')
	return (data)

def get_places(url):
	places = []
	url="https://www.holidify.com"+url
	try:
		page_response = requests.get(url, timeout=10)
		soup = BeautifulSoup(page_response.content, "html.parser")
		links = soup.findAll('a',attrs={'class':"holidify-color readMore btn btn-primary"})
	except:
		print("Could not connect, check your internet !")
		return
	else:
		for link in links:
			if("places" in str(link) and "openLink" in str(link)):
				print(link['onclick'].split("places/")[1].split("/\")")[0].title().strip(),"                        \r\r",end=' ')
				places.append(link['onclick'].split("openLink(\"")[1].split("\")")[0])
				# print(link)
	return places

def list_places(places,url):

	print("Generating list of places ...")
	url+="/places/goa"
	place = []
	urls=[]
	try:
		page_response = requests.get(url, timeout=10)
		soup = BeautifulSoup(page_response.content, "html.parser")
	except:
		# raise
		print("Could not connect, check your internet !")
		return
	else:
		
		words = {"collections","country","state"}
		spans = soup.findAll('span',attrs={'class':"clickable"})
		for span in spans:
			if "onclick" in str(span) and any(word in words for word in span['onclick'].split("/")):
				if "collections" in str(span) and (len(span['onclick'].split("openLink(\"/collections/")[1])<3):
					continue
				urls.append(span['onclick'].split("openLink(\"")[1].split("\")")[0])
			elif "onclick" in str(span) and "openLink" in str(span) and "places" in span['onclick'].split("/") :
				print(span['onclick'].split("places/")[1].split("/")[0].title().strip(),"                        \r\r",end=' ')
				place.append('/'+'/'.join(span['onclick'].split("/")[1:3])+'/')
	
	with Pool(processes=len(urls)) as pool:
		place1 = (pool.map(get_places, urls))
	place1 = [j for sub in place1 for j in sub]
	place += place1
	places += list(set(place))
	print("Done!",len(places),"Places found.")


def main():
	url = "https://www.holidify.com"
	schema = ["City Name", "Places to Visit in the city", "State","Country","Weather","Best time","Ideal duration","About","Nearest Airport", "Upcoming events", "More on City", "How to reach"]
	places = []
	list_places(places,url)

	batch_size = 2*mp.cpu_count()-1
	print("Number of operable threads:",batch_size+1)

	with Pool(processes=batch_size) as pool:
		csv_data = (pool.starmap(get_content, zip(places , itertools.repeat(url))))
	# print(csv_data)
	with open('holidify.csv', 'w', newline='', encoding="utf-8") as csvFile:
	    writer = csv.writer(csvFile)
	    writer.writerow([x for x in schema])
	    writer.writerows(csv_data)
	print("'holidify.csv' Saved!                                    ")


if __name__ == '__main__':
	main()