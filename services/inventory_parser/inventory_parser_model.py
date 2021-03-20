from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QThread

import requests
import time
import threading

from services.inventory_parser.inventory_item import InventoryItem


class GetPriceThread(QThread):
	progress_signal = QtCore.pyqtSignal(int)

	def __init__(self, items, app_id):
		super().__init__()
		self.items = items
		self.step = 100 / len(self.items)
		self.pb_count = 0
		self.app_id = app_id

	def __get_format_price(self, price):
		return float('{:.2f}'.format(float(price[1:])))

	def __fill_item_data(self, json_response, item):
		if json_response.get('success'):
			item_data = item.get_data()

			lowest_price = json_response.get('lowest_price')
			median_price = json_response.get('median_price')
			volume = json_response.get('volume')

			item_price = 0

			if lowest_price:
				item_price = self.__get_format_price(lowest_price)
			elif median_price:
				item_price = self.__get_format_price(median_price)

			item_data['price'] = item_price

			if volume:
				item_data['volume'] = volume
			item.set_data(item_data)

		return item

	def run(self):
		BASE_PRICE_LINK = 'https://steamcommunity.com/market/priceoverview/?appid={0}&currency=1&market_hash_name='.format(self.app_id)
		
		for item in self.items:
			item_data = item.get_data()
			try:
				if not item_data.get('marketable'):
					continue

				time.sleep(3.4)
				r = requests.get(BASE_PRICE_LINK + item_data.get('market_hash_name'))

				if r.status_code == 200:
					json_response = r.json()
					print(str(json_response) + ' - ' + item_data.get('market_hash_name'))
					item = self.__fill_item_data(json_response, item)

			except ValueError as e:
				print(item_data.get('market_hash_name') + ':', e)

			except requests.exceptions.RequestException as e:
				print(item_data.get('market_hash_name') + ':', e)

			except Exception as e:
				print(item_data.get('market_hash_name') + ':', e)

			finally:
				time.sleep(0.1)
				self.pb_count += self.step
				self.progress_signal.emit(self.pb_count)


class InventoryLoaderThread(QThread):
	complete_signal = QtCore.pyqtSignal(dict)
	error_signal = QtCore.pyqtSignal(str, str)

	def __init__(self, steam_id, app_id, pb_progress, parent = None):
		super().__init__()
		self.steam_id = steam_id
		self.app_id = app_id
		self.pb_progress = pb_progress
		self.parent = parent

		self.items = []

		self.is_no_price = False

	def run(self):
		self.__load_inventory()

		if not self.is_no_price:
			self.__start_getting_price_thread()
			self.__calc_price_for_every_item()

		data = {
			'steam_id': self.steam_id,
			'app_id': self.app_id,
			'items': self.items,
		}
		self.complete_signal.emit(data)
	
	def __load_inventory(self):
		self.items = []
		link = 'https://steamcommunity.com/profiles/{0}/inventory/json/{1}/2'.format(self.steam_id, self.app_id)
		# https://steamcommunity.com/profiles/76561198129642590/inventory/json/730/2
		try:
			r = requests.get(link)
			json_response = r.json()
			if (json_response.get('success')):
				inventory_ids = json_response.get('rgInventory')
				inventory_descriptions = json_response.get('rgDescriptions')

				item_amount = self.__get_dict_with_count(inventory_ids, 'classid')
				for inventory_item in inventory_descriptions.values():
					data = self.__fill_item_data(inventory_item, item_amount)
					new_item = InventoryItem(data)
					self.items.append(new_item)
				
				self.__get_all_item_ids(inventory_ids)

			else:
				self.__send_error_message('Something gone wrong', str(json_response))
		
		except ValueError as e:
			self.__send_error_message('ValueError', str(e))

		except requests.exceptions.RequestException as e:
			self.__send_error_message('requests.exceptions.RequestException', str(e))

		except Exception as e:
			self.__send_error_message('Something gone wrong', 'Try again later.\n{}'.format(str(e)))

	def __start_getting_price_thread(self):
		thread1 = GetPriceThread(self.items, self.app_id)
		thread1.progress_signal.connect(self.__inc_progress)
		thread1.start()
		thread1.wait()

	def __calc_price_for_every_item(self):
		for item in self.items:
			item.calc_total_price()

	def set_no_price_flag(self, is_no_price):
		self.is_no_price = is_no_price

	@QtCore.pyqtSlot(int)
	def __inc_progress(self, value):
		self.pb_progress.setValue(value)

	def __get_dict_with_count(self, source_dict, key):
		item_amount = {}
		for item in source_dict.values(): 
			key_instance = item.get(key)
			if key_instance in item_amount:
				item_amount[key_instance] += 1
			else:
				item_amount[key_instance] = 1
		return item_amount

	def __fill_item_data(self, inventory_item, item_amount):
		data = {
			'name': inventory_item.get('name'),
			'market_hash_name': inventory_item.get('market_hash_name'),
			'amount': item_amount.get(inventory_item.get('classid')),
			'classid': inventory_item.get('classid'),
			'instanceid': inventory_item.get('instanceid'),
			'tradable': inventory_item.get('tradable'),
			'marketable': inventory_item.get('marketable'),
			'price': 0,
			'total_price': 0,
			'volume': 0,
			'ids': [],
		}
		return data

	def __get_all_item_ids(self, inventory_ids):
		for item in self.items:
			item_data = item.get_data()
			classid = item_data.get('classid')
			item_data['ids'] = self.__get_list_with_main_key_values(inventory_ids, 'id', 'classid', classid)
			item.set_data(item_data)

	def __get_list_with_main_key_values(self, source_dict, main_key, search_key, search_key_value):
		ids = []
		for item in source_dict.values():
			if item.get(search_key) == search_key_value:
				ids.append(item.get(main_key))
		return ids

	def __send_error_message(self, title, message):
		self.error_signal.emit(title, message)
	















