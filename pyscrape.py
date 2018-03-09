import requests
import scrapy
import json
import re
import pprint


def main():

	#initial request
	url='http://goheels.com/roster.aspx?path=wsoc'
	r=requests.get(url,headers={'User-Agent':'UNC Journal Class'},)


	#get page's content and text
	page_content=r.content.decode('utf-8')
	#print(page_content)
	sel=scrapy.Selector(text=page_content)
	play_table=sel.css('.sidearm-table')[0]

	play_table.css('tr')[0].css('th').xpath('string()') 
	#pprint.pprint(play_table)
	#print(play_table.css('tr')[0].css('th').xpath('string()').extract() )
	columns=play_table.css('tr:nth-child(0) th').xpath('string()').extract()
	#pprint.pprint(columns)
	#print(columns)

	rows=play_table.css('tr')[1:]
	#pprint.pprint(rows)
	
	player_dict={}
	player_num_dict={}
	player_data=[]
	counter=0

	#iterates over each player on the page

	for x in rows:

		#each variable is a 
		player_num=x.css('td')[0].xpath('string()').extract()[0]
		player_name=x.css('td')[1].xpath('string()').extract()[0]
		print(player_num+' '+player_name)
		player_pos=x.css('td')[2].xpath('string()').extract()[0]
		player_hight=x.css('td')[3].xpath('string()').extract()[0]
		player_year=x.css('td')[4].xpath('string()').extract()[0]
		palyer_home=x.css('td')[5].xpath('string()').extract()[0]
		profile_link=x.css('td')[1]
		profile_link=profile_link.css('a')
		profile_link=profile_link.xpath('@href').extract()
		player_num_data=[]

		reqUrl='http://goheels.com'+profile_link[0]
		reqR=requests.get(reqUrl,headers={'User-Agent':'UNC Journal Class'})
		bio=getBio(reqR) #(profile_link[0])
		img=getImg(reqR) #(profile_link[0])
		#if counter==0:
		stats=getStats(profile_link[0])
		#print(stats)
		stats=pasrseStats(stats)

		counter=counter+1
		

		player_data={
			'name':player_name,
			'num':player_num,
			'position':player_pos,
			'height':player_hight,
			'year':player_year,
			'hometown':palyer_home,
			'href':profile_link[0],
			'img':img,
			'bio':bio,
			'stats':stats
		}
		player_num_dict[player_num]=player_data
		


	jsonStr=json.dumps(player_num_dict)   
	f=open("players.json","w")
	f.write(jsonStr)
	f.close




def getBio(bioR):
	# bioUrl='http://goheels.com'+s
	# bioR=requests.get(bioUrl,headers={'User-Agent':'UNC Journal Class'})
	content=bioR.content.decode('utf-8')
	sel=scrapy.Selector(text=content)
	player_bio = sel.css('#sidearm-roster-player-bio').xpath('string()').extract()[0]
	#print(player_bio)
	return player_bio

def getImg(imgR):
	# imgUrl='http://goheels.com'+s
	# imgR=requests.get(imgUrl,headers={'User-Agent':'UNC Journal Class'})
	content=imgR.content.decode('utf-8')
	sel=scrapy.Selector(text=content)
	player_image = sel.css('.sidearm-roster-player-image img').xpath("@src").extract()[0]
	#print(player_image)
	return player_image


def getStats(s):
	js_obj_rx = re.compile(r'.*?responsive-roster-bio\.ashx.*?({.*?})')
	statsUrl='http://goheels.com'+s
	statsR=requests.get(statsUrl,headers={'User-Agent':'UNC Journal Class'})
	content=statsR.content.decode('utf-8')
	parts = content.split('$.getJSON("/services/')[1:]
	#print(parts)
	captured = js_obj_rx.findall(''.join(parts))
	clean_objs=[]
	for obj_str in captured:
		if 'stats' not in obj_str:
			continue

		obj_str = obj_str.replace('{', '').replace('}', '')
		obj_str = obj_str.replace("'", '').replace('"', '')
		# Split apart on commas
		obj_pairs = obj_str.split(',')
		obj_pairs = [x.split(":") for x in obj_pairs]
		clean_pairs = []
		for pair in obj_pairs:
			clean_pairs.append(['"{}"'.format(p.strip()) for p in pair])

		colonized=[":".join(p) for p in clean_pairs]
		commas=','.join(colonized)

		json_str="{" + commas + "}"
		clean_objs.append(json.loads(json_str))
	
	stats_url = (
		"http://goheels.com/services/responsive-roster-bio.ashx?"
		"type={type}&rp_id={rp_id}&path={path}&year={year}"
		"&player_id={player_id}"
	).format(**clean_objs[0])

	resp = requests.get(stats_url, headers={'User-Agent':'UNC Journal Class'})

	txt=json.loads(resp.content.decode("utf-8"))
	#pprint.pprint(txt)
	player={}
	player['raw_stats']=txt
	#print(player['raw_stats']['career_stats'])
	#print(player['raw_stats'])
	return(player)#['raw_stats'])


def pasrseStats(player):
	if player['raw_stats']['career_stats'] == None:
		player['raw_stats']['career_stats']={}
		#return player
	#print(player)
	stats = {}
	#txt=player
	#sel = scrapy.Selector(text=txt)
	for raw_key, raw_val in player['raw_stats'].items():
		txt = player['raw_stats'][raw_key]

		if not txt:
			#print('Skipping {} for {}'.format(raw_key, player['Full Name']))
			continue

		sel = scrapy.Selector(text=txt)
		#count=0
		for section in sel.css('section'):
			title = section.css('h5').xpath('string()').extract()[0]
			#print(title)
			#print(section)
			cols = section.css('tr')[0].css('th').xpath('string()').extract()
			#print(cols)
			these_stats=[]
			for r in section.css('tr')[1:]: 
				#was 1
			 	#print('row', r.xpath('string()').extract()[0].replace('\r', '').replace('\n', '').strip())
			 	s={}
			 	#print(r)
			 	i=1
			 	for d in r.css('td'):
			 		# tmp=d.xpath('string()').extract()[0]
			 		# print(s)
			 		if i<len(r.css('td')):
			 			tmp=d.xpath('string()').extract()[0]
			 			s[cols[i].lower()]=tmp
			 			i+=1
			 			#print(s)
			 			
			 	yr = r.css('th').xpath('string()')
			 	#print(yr)
			 	if yr:
			 		yr = yr.extract()[0]
			 		if yr.lower() in ('total', 'season'):
			 		#	print('SKIPPING...')
			 			continue
			 		#print('THE YR IS', yr)
			 		s['year']=yr

			 	these_stats.append(s)

			#print(these_stats)
			#print('----------'+these_stats)
			existing = stats.get(raw_key, {})
			existing[title] = these_stats
			stats[raw_key] = existing
		#pprint.pprint(stats)
	#pprint.pprint(stats)
	#if len(stats)>0:
	if 'current_stats' in stats:
		del stats['current_stats']

	if 'gamehigh_stats' in stats:
		del stats['gamehigh_stats']

	#pprint.pprint(stats)
	if 'career_stats' in stats:
		player['stats']=stats['career_stats']

	else: 
		player['stats']=stats

	return player['stats']
		



if __name__ == '__main__':
	main()
