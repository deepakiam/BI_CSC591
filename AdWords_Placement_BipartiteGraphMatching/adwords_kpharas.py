import sys
import csv
import math
import numpy as np
from collections import OrderedDict


if len(sys.argv)!=2:
	print "python adwords.py <greedy|balance|msvv>"
	exit(1)
method = sys.argv[1]

def get_bidder_dictionary(bidder, bidder_dict):
	firstline = True
	for row in bidder:
		if firstline:
			firstline = False
			continue
		bidder_id = row[0]
		if bidder_id not in bidder_dict:
			bidder_dict[bidder_id] = row[3]

def get_query_dictionary(bidder, query_dict):
	firstline = True
	for r in bidder:
		bidder1 = csv.reader(open('bidder_dataset.csv', 'r'))
		if firstline:
			firstline = False
			continue
		query = r[1]
		if query not in query_dict:
			temp_dict = OrderedDict()
			for row in bidder1:
				if(row[1]==query):
					temp_dict[row[0]] = row[2]
			query_dict[query] = temp_dict

def main():

	bidder = csv.reader(open('bidder_dataset.csv', 'r'))
	bidder_dict = {}
	query_dict = {}

	get_bidder_dictionary(bidder, bidder_dict)
	msvv_bidder_dict = dict(bidder_dict)

	budget_sum = 0
	for k,v in bidder_dict.iteritems():
		budget_sum = budget_sum + int(v)

	bidder = csv.reader(open('bidder_dataset.csv', 'r'))
	get_query_dictionary(bidder, query_dict)

	f = open("queries.txt")
	
	query_list = []
	for q in f:
		query_list.append(q.strip())

	if method == 'greedy':
		revenue_sum = 0
		
		for i in range(100):
			revenue = 0
			random_query = np.random.permutation(query_list)
			bidder_dict_temp = dict(bidder_dict)
			for line in random_query:
				if line in query_dict:
					temp_dict = query_dict[line]
					max1 = -1
					for key, values in temp_dict.iteritems():
							if (float(bidder_dict_temp[key])-float(values) >= 0 and values>max1):
								max1 = values
								temp_key = key
							else:
								continue
				if max1 != -1:
					bidder_dict_temp[temp_key] = float(bidder_dict_temp[temp_key])-float(max1)
					revenue = float(revenue) + float(max1)
			revenue_sum = float(revenue_sum) + float(revenue)

		ALG = float(revenue_sum/100)
		print "Greedy"
		print "Revenue :" + str(ALG)
		print "Competitive ratio :" + str(ALG/budget_sum)

	if method == 'balance':
		revenue_sum = 0
		
		for i in range(100):
			revenue = 0
			random_query = np.random.permutation(query_list)
			bidder_dict_temp = dict(bidder_dict)
			for line in random_query:
				if line in query_dict:
					temp_dict = query_dict[line]
					max1 = -1
					max2 = -1
					for key, values in temp_dict.iteritems():
							if (float(bidder_dict_temp[key])-float(values) >= 0 and float(bidder_dict_temp[key])>max2):
								max2 = float(bidder_dict_temp[key])
								max1 = values
								temp_key = key
							else:
								continue
				if max1 != -1:
					bidder_dict_temp[temp_key] = float(bidder_dict_temp[temp_key])-float(max1)
					revenue = float(revenue) + float(max1)
			revenue_sum = float(revenue_sum) + float(revenue)

		ALG = float(revenue_sum/100)
		print "Balance"
		print "Revenue :" + str(ALG)
		print "Competitive ratio :" + str(ALG/budget_sum)

	if method == 'msvv':
		revenue_sum = 0
		
		for i in range(100):
			revenue = 0
			random_query = np.random.permutation(query_list)
			bidder_dict_temp = dict(bidder_dict)
			for line in random_query:
				if line in query_dict:
					temp_dict = query_dict[line]
					max1 = -1
					max2 = -1
					for key, values in temp_dict.iteritems():
							x_u = (float(msvv_bidder_dict[key])-float(bidder_dict_temp[key]))/float(msvv_bidder_dict[key])
							fi_x = 1 - math.exp(x_u-1)
							temp_values = float(values) * float(fi_x)
							if (float(bidder_dict_temp[key])-float(values) >= 0 and temp_values>max2):
								max2 = temp_values
								max1 = values
								temp_key = key
							else:
								continue
				if max1 != -1:
					bidder_dict_temp[temp_key] = float(bidder_dict_temp[temp_key])-float(max1)
					revenue = float(revenue) + float(max1)
			revenue_sum = float(revenue_sum) + float(revenue)

		ALG = float(revenue_sum/100)
		print "MSVV"
		print "Revenue :" + str(ALG)
		print "Competitive ratio :" + str(ALG/budget_sum)

if __name__=="__main__":
	main()