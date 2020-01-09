from _lib import gen_data_from_csvlist
import sys, os, configparser

CONFIG_FILENAME = os.path.join("config", "collections.ini")

if __name__ == '__main__':
	config_parser = configparser.ConfigParser()
	
	if len(sys.argv) == 1:
		config_parser.read(CONFIG_FILENAME, encoding='utf8')
	else:
		try:
			config_parser.read(os.path.join("config", sys.argv[1]), encoding='utf8')
		except Exception:
			config_parser.read(CONFIG_FILENAME, encoding='utf8')
	try:
		filename = config_parser.get('file', 'filename')
	except Exception:
		filename = "alh_ald.csv"
	try:
		indices = [int(i) for i in config_parser.get('file', 'indices').split(',')]
	except Exception:
		indices = []
	
	count = 0
	print("Generating data list from", filename)
	count = gen_data_from_csvlist(filename, indices)
	print("Generated", count, "data items for", len(indices), "collections")