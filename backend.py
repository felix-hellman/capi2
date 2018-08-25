from sys import argv
from time import time
from time import sleep
from threading import Thread
import json

if "debug" in argv[1]:
	from mockzero import LED
elif "deploy" in argv[1]:
	from gpiozero import LED
else:
	print("No mode selected, quitting... ")
	exit(1)

def timeable(func):
	def wrapper(*args, **kwargs):
		start = time()
		result = func(*args,**kwargs)
		print(func.__name__ + " executed in " + str(time() - start))
	return wrapper

def threadable(func):
	def wrapper(*args, **kwargs):
		thread = Thread(None,func,None, args ,**kwargs)
		thread.start()
		return thread
	return wrapper

@threadable
@timeable
def flowForSeconds(index,seconds):
	LED(index).on()
	sleep(seconds)
	LED(index).off()

class FluidPool:
	queue = []
	def __init__(self):
		pass
	def openFor(self,index,seconds):
		self.queue.append(flowForSeconds(index,seconds))
	def openIngredientFor(self,ingredient,seconds):
		self.queue.append(flowForSeconds(fetchLiquidIndex(ingredient),seconds))
	def openIngredient(self,drinkIngredient):
		self.queue.append(flowForSeconds(fetchLiquidIndex(drinkIngredient.name),drinkIngredient.cl))
	def waitForRemaining(self):
		for t in self.queue:
			t.join()

def fetchLiquidIndex(ingredient):
	with open("liquidIndex.json") as f:
		result = json.load(f)
		for key in result:
			if ingredient == key:
				return result[key]
	return -1

class DrinkIngredient:
	name = ""
	cl = -1
	def __init__(self,name,cl):
		self.name = name
		self.cl = cl

vodka = DrinkIngredient("Vodka",10)
water = DrinkIngredient("Water",5)

fp = FluidPool()
fp.openIngredient(vodka)
fp.openIngredient(water)
fp.waitForRemaining()
