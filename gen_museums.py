from _lib import gen_all_museums
import sys


if __name__ == '__main__':
	count = 0
	if len(sys.argv) > 1:
		print("Generating museum list to", sys.argv[1])
		count = gen_all_museums(sys.argv[1])
	else:
		print("Generating museum list to all-museums.csv")
		count = gen_all_museums()
	print("Found and wrote data for", count, "museums")