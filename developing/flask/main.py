
from flask import Flask
from flask import render_template

import os
import json
import threading
from _client_robot import ClientRobot
import time
import Pyro4
#import cv2
import urllib.request, urllib.parse, urllib.error
import numpy as np
from PIL import Image
import io
import socket
import struct
import time

bot = {}

def getMethods(bot):
	elems = []
	for elem in bot.__dict__:
		print(elem)
		try:
			print(elem.__docstring__())
			print(elem.__expose__())

			elems.append(elem)
		except Exception as e:
			print(e)
	print(elems)
	return elems


app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.do')


@app.route('/')
def index():
	return render_template('need_robot.html')

@app.route('/<name>')
def init(name=None):
	if name != None:
		try:
			global bot
			bot = ClientRobot(name)
			methods = getMethods(bot)
			print(bot.__dict__)
			#print bot.milaser.__docstring__()
			#print bot.suelo.__docstring__()
			#print bot.milaser.__exposed__()
			return render_template('index.html', name=name, bot = bot )

		except Exception as e:
			print(e)
			print(Exception)
			return render_template('error.html',error=name)



@app.route('/<name>/<var>/<var2>')
def getter(name=None,var=None,var2=None):
	global bot
	if name == bot.name:
		try:
			global bot
			aux2 = eval("bot."+var+"."+var2+"()")
			return str(json.dumps(aux2))
		except Exception as e:
			print(e)
			print(Exception)



@app.route('/<name>/<var>/<var2>/<var3>')
def setter(name=None,var=None,var2=None,var3=None):
	global bot
	if name == bot.name:
		try:
			aux2 = eval("bot."+var+"."+var2+"("+var3.replace("-",",")+")")
			return str(json.dumps(aux2))
		except Exception as e:
			print(e)
			print(Exception)
