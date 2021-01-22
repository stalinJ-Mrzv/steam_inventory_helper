import requests

import steam.webauth as wa

from getpass import getpass

from services.main_controller import MainController

def main():
	username = input('Username: ')
	password = getpass()
	
	# Or type username and password here
	# username = 'USERNAME_HERE'
	# password = 'PASSWORD_HERE'

	try:
		user = wa.WebAuth(username)
		session = user.cli_login(password)

		if session:
			controller = MainController()
			controller.set_user_data(user, session)
			controller.start()

		else:
			print('something gone wrong')

	except wa.WebAuthException as e:
		print(e)


if __name__ == '__main__':
	main()