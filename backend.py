from sys import argv
from time import time
from time import sleep
from threading import Thread
from flask import Flask
from flask_restful import Resource, Api, request
import json

if "debug" in argv[1]:
	from mockzero import LED
elif "deploy" in argv[1]:
	from gpiozero import LED
else:
	print("No mode selected, quitting... ")
	exit(1)

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
	def isAvailable(self):
		for t in self.queue:
			if t.isAlive():
				return False
		return True
	def __del__(self):
		self.waitForRemaining()

fluidPool = FluidPool()

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

def blocking(func):
	def wrapper(*args,**kwargs):
		global fluidPool
		if fluidPool.isAvailable():
			func(*args,**kwargs)
		else:
			print("Currently busy, skipping job!")
	return wrapper

@threadable
@timeable
def flowForSeconds(index,seconds):
	LED(index).on()
	sleep(seconds)
	LED(index).off()

def fetchLiquidIndex(ingredient):
	with open("liquidIndex.json") as f:
		result = json.load(f)
		for key in result:
			if ingredient == key:
				return result[key]
	return -1

def parseRecipe(recipe):
	print(recipe)
	result = json.loads(recipe)
	ingredientList = []
	for ingredient in result["ingredients"]:
		ingredientList.append(DrinkIngredient(ingredient["name"],ingredient["amount"]))
	return ingredientList


def rumAndCokeJson():
	with open("recipe.json") as f:
		result = json.load(f)
		return json.dumps(result[0])

def getAllRecipe():
	with open("recipe.json") as f:
		return json.load(f)

@blocking
def pourDrinkFromJson(jsonRecipe):
	recipe = parseRecipe(jsonRecipe)
	for ingredient in recipe:
		fluidPool.openIngredient(ingredient)

class DrinkIngredient:
	name = ""
	cl = -1
	def __init__(self,name,cl):
		self.name = name
		self.cl = cl

class CocktailApi(Resource):
	def get(self):
		return getAllRecipe()
	def post(self):
		pourDrinkFromJson(request.data)
	
app = Flask(__name__)
api = Api(app)
api.add_resource(CocktailApi,"/cocktail")

if __name__ == '__main__':
	app.run(debug = True)

