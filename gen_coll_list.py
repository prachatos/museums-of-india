from _lib import gen_coll_from_csvlist
import sys, os, configparser

CONFIG_FILENAME = os.path.join("config", "museums.ini")

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
		filename = "all-museums.csv"
	try:
		indices = [int(i) for i in config_parser.get('file', 'indices').split(',')]
	except Exception:
		indices = []
	
	count = 0
	print("Generating collections list from", filename)
	count = gen_coll_from_csvlist(filename, indices)
	indices_str = "all" if len(indices) == 0 else str(len(indices))
	print("Generated", count, "collections for", indices_str, "museums")
