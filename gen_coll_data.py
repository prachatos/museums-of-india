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
	try:
		nodesc = bool(int(config_parser.get('file', 'nodesc')))
	except Exception:
		nodesc = False
	
	count = 0
	print("Generating data list from", filename)
	count = gen_data_from_csvlist(filename, indices, nodesc)
	indices_str = "all" if len(indices) == 0 else str(len(indices))
	print("Generated", count, "data items for", indices_str, "collections")