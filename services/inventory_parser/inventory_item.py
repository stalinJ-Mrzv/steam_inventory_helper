class InventoryItem:
	'''
		data:
		name: str
		market_hash_name: str
		amount: int
		classid: str
		instanceid: str
		tradable: bool
		marketable: bool
		price: float
		total_price: float
		volume: int
		ids: list
	'''

	def __init__(self, data):
		self.__data = data

	def set_data(self, data):
		self.__data = data

	def get_data(self):
		return self.__data

	def calc_total_price(self):
		price = self.__data.get('price')
		amount = self.__data.get('amount')
		if price and amount:
			self.__data['total_price'] = float('{:.2f}'.format(float(price) * amount))
