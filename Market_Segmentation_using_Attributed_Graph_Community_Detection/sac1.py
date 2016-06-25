from __future__ import division
import sys
import collections
import math
import operator
import pandas as pd
import numpy as np
from igraph import *

if len(sys.argv) != 2:
    print "python sac1.py <value_of_alpha = 0/0.5/1>"
    exit(1)
alpha = float(sys.argv[1])


# Computing Similarity
def similarity(node1, node2):
	x_sq = 0
	y_sq = 0
	x_y = 0

	for i in range(len(node1)):
		x = node1[i]
		y = node2[i]
		x_sq = x_sq + (x * x)
		y_sq = y_sq + (y * y)
		x_y = x_y + (x * y)
# Computing consine similarity
	res = x_y/math.sqrt(x_sq*y_sq)
	return res

# Computing Cosine Similarity for pair and Obtaining a Similarity Matrix
def consine_similarity(graph_nw, num_vertices):
	sim_matrix = [[0 for x in range(num_vertices)] for x in range(num_vertices)]

	for i in range(num_vertices):
		for j in range(num_vertices):
			sim_matrix[i][j] = similarity(graph_nw.vs[i].attributes().values(),graph_nw.vs[j].attributes().values())
	return sim_matrix

def main():
# Loading the data
	graph_nw = open('data/fb_caltech_small_edgelist.txt','r')
	node_attributes = pd.read_csv("data/fb_caltech_small_attrlist.csv")
# Creating iGraph
	main_graph = Graph()
	main_graph = create_graph(graph_nw,node_attributes)
	final_count_comm = 0
	final_comm_dict = {}
# Calling SAC Algorithm
	for i in range(15):

		temp_comm_list = []
		num_vertices = len(main_graph.vs)
		#Getting a list of all nodes in the graph
		for j in range(num_vertices):
			temp_comm_list.append(j)
		#Calling similarity matrix function
		sim_matrix = consine_similarity(main_graph,num_vertices)
		# Calling Phase 1 and 2 of SAC
		phase1_comm_dict, temp_comm_list = sac_phase1(main_graph, temp_comm_list, sim_matrix, alpha)
		final_comm_dict, main_graph = sac_phase2(main_graph, temp_comm_list, sim_matrix, alpha, final_comm_dict, i, phase1_comm_dict)

# If Algorithm reaches convergence Break
		if len(final_comm_dict.keys()) == final_count_comm:
			break
# Obtain final number of communities
		final_count_comm = len(final_comm_dict.keys())
# Writing to the file
	writefile_comm(final_comm_dict,float(alpha))

# Function to write to file
def writefile_comm(final_comm_dict,alpha):
	with open('communities.txt','w') as f:
		for comm,mem in final_comm_dict.iteritems():
			first = True
			for m in mem:
				if(first):
					f.write(str(m))
					first = False
				else:
					f.write(','+str(m))
			f.write('\n')

# Function to calculate Newman Modularity
def newman_mod_func(temp_comm_list, comm_list, main_graph):
	return main_graph.modularity(temp_comm_list) - main_graph.modularity(comm_list)

# Function to calculate Attribute Modularity
def attribute_mod_func(curr_comm_list, sim_matrix, comm_list,i):
	attr_partial = 0
	len_curr_comm = len(curr_comm_list)
	for mem in curr_comm_list:
		attr_partial = attr_partial + sim_matrix[i][mem]
	main_comm = len(set(comm_list))
	attribute_mod = attr_partial/(len_curr_comm*len_curr_comm*main_comm*main_comm) 

	return attribute_mod

# Phase 1 Computation
def sac_phase1(main_graph, comm_list, sim_matrix, alpha):
	phase1_comm_list = list(comm_list)
	flag = False # flag to check if value changes or not
	count = 0 # Keeping Track of number of iterations
	num_vertices = len(main_graph.vs)

	while not flag and count<15: # Running till there is no gain or number of iteration does not cross 15
		for i in range(num_vertices):
			curr_maxgain = 0 # Initializing gain to 0
			curr_comm = i # Current community of node
			for j in range(num_vertices):
				temp_comm_list = list(comm_list)
				# Placing one node/vertex into j's community
				temp_comm_list[i] = temp_comm_list[j]
				# Calling Newmon Modularity
				newman_mod = newman_mod_func(temp_comm_list, comm_list, main_graph)

				# Getting all nodes in same community as j
				curr_comm_list = []
				for mem, comm in enumerate(comm_list):
					if comm == comm_list[j]:
						curr_comm_list.append(mem) 

				# Calling attribute Modularity function
				attribute_mod = attribute_mod_func(curr_comm_list, sim_matrix, comm_list,i)
				# obtaining current gain
				gain_mod_new = alpha * newman_mod + (1 - alpha) * attribute_mod

				# gain obtained is more than prev then change community of current node
				if gain_mod_new > curr_maxgain:
					curr_maxgain = gain_mod_new
					curr_comm = j

			if (curr_maxgain > 0):
				comm_list[i] = comm_list[curr_comm]
			else:
				flag = True # if flag is set to True loop breaks -- no gain

		if comm_list == phase1_comm_list:
			flag =True
		else:
			phase1_comm_list = list(comm_list)

		count = count + 1

	# Initializing the current community dictionary (change in community of vertices) based on the changes of 
	# Phase 1	
	new_comm_dict ={}

	for i in range(num_vertices):
		new_comm_dict[i] = []

	for mem,comm in enumerate(comm_list):
		new_comm_dict.get(comm).append(mem)

	return new_comm_dict, comm_list

# Calling Phase 2
def sac_phase2(main_graph, temp_comm_list, sim_matrix, alpha, final_comm_dict, itr, comm_dict):
	unique_comm = list(set(temp_comm_list))

# Used to adjust the indexes of the vertices based on 0 based indexing
	for i,e in enumerate(unique_comm):
		for mem,comm in enumerate(temp_comm_list):
			if comm == e:
				temp_comm_list[mem] = i

# Checking for first iteration
	if ((itr+1) == 1):
		v = 0
		for key,value in comm_dict.iteritems():
			if value:
				final_comm_dict[v] = value
				v = v + 1
	else:
# Checking for other iterations - Merging communities of different nodes
		temp_final_comm_dict = {}
		vx = 0
		for key,value in comm_dict.iteritems():
			merged_comm = []
# If some value is blank then skip
			if value:
				for v in value:
# Merge nodes and make new community
					merged_comm = merged_comm + final_comm_dict.get(v)
				temp_final_comm_dict[vx]=merged_comm
				vx = vx + 1
		final_comm_dict = dict(temp_final_comm_dict)

# Contracting vertices while merging nodes 
	main_graph.contract_vertices(temp_comm_list,combine_attrs=mean)
	return final_comm_dict, main_graph


def create_graph(graph_nw,node_attributes):
	temp_g = Graph()
# Adding edges and nodes/vertices to iGraph
	edge_list = []
	node_unique_ids = []
	for conn in graph_nw:
		e1,e2 = conn.strip().split()
		edge_list.append((e1,e2))
		node_unique_ids.append(e1)
		node_unique_ids.append(e2)

	temp_g.add_vertices(len(set(node_unique_ids)))

# Adding Edges
	for e1,e2 in edge_list:
		temp_g.add_edges((int(e1),int(e2)))

# attr is the list of attributes in the file
	attr = ["year0","year1968","year1976","year1979","year1984","year1993","year1996","year1999","year2001","year2002","year2003","year2004","year2005","year2006","year2007","year2008","year2009","year2010","dorm0","dorm165","dorm166","dorm167","dorm168","dorm169","dorm170","dorm171","dorm172","gender0","gender1","gender2","student_fac1","student_fac2","student_fac5","student_fac6","major0","major190","major192","major194","major195","major196","major197","major198","major199","major200","major201","major202","major204","major205","major206","major207","major208","major209","major211","major212","major213","major217","major220","major221","major222","major223","major224","major226","major227","major228","major229"]

	i = 0

	for e in temp_g.es:
		temp_g.es[i]['weight']=1
		i += 1

# Adding attribute values related to each vertex
	for index,r in node_attributes.iterrows():
		j=0
		for i in r:
			temp_g.vs[index][attr[j]]=i
			j = j+1

	return temp_g


if __name__ == "__main__":
    main()