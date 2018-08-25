class LED:
	index = -1;
	def __init__(self,index):
		self.index = index
	def on(self):
		print("Turing on " + str(self.index))
	def off(self):
		print("Turning off " + str(self.index))


