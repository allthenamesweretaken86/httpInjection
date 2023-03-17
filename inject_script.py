from mitmproxy import ctx
import dataframing
from bs4 import BeautifulSoup   # nice representation of the DOM
import pandas as pd
data = {'bodys':'','urls':''}
hlist = []
urls = []
bodys = []


def saveData(data):
	#data['html'] = hlist
	df = pd.DataFrame()
	df = df.from_dict(data)
	df.to_pickle('./html')#,index=False)
	ctx.log.info("saved")

	
def response(flow):
	ctx.script = "./js/alert.js"
	if flow.request.host in ctx.script:
		return  # Make sure JS isn't injected to itself
	html = BeautifulSoup(flow.response.content, features = "html.parser")
	if html.body and ("text/html" in flow.response.headers["content-type"]):     # inject only for HTML resources
		# delete CORS header if present
		if "Content-Security-Policy" in flow.response.headers:
			del flow.response.headers["Content-Security-Policy"]
		# inject SocketIO library from CDN
		cdn = html.new_tag("script", type="text/javascript", src="//cdnjs.cloudflare.com/ajax/libs/socket.io/1.3.6/socket.io.min.js")
		html.body.insert(0, cdn)
		script = html.new_tag("script", type="application/javascript")
		script.insert(0, read_file(ctx.script))
		html.body.insert(1, script)
		flow.response.text = str(html)
		ctx.log.info("script injected")

		for item in flow.response.headers:
			ctx.log.info(f'Header: {str(item)}')
			
		###
		bodys.append(str(html.body))
		urls.append(str(flow.request.url))
		#data['urls'] = urls
		#data['bodys']=bodys

		ctx.log.info(str(data.urls))

		saveData(vars(flow.request))
		




		

def read_file(filename):
	with open(filename) as f:
		return f.read()
