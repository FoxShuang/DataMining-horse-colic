#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy
import random
from scipy.stats import mode
from matplotlib import pyplot

#28 attributes:
attr_info = [['surgery','nominal'],
			['age','nominal'],
			['hospital_number','nominal'],
			['rectal_temperature','numeric'],
			['pulse','numeric'],
			['respiratory_rate','numeric'],
			['temperature_of_extremities','nominal'],
			['peripheral_pulse','nominal'],
			['mucous_membranes','nominal'],
			['capillary_refill_time','nominal'],
			['pain','nominal'],
			['peristalsis','nominal'],
			['abdominal_distension','nominal'],
			['nasogastric_tube','nominal'],
			['nasogastric_reflux','nominal'],
			['nasogastric_reflux_PH','numeric'],
			['rectal_examination','nominal'],
			['abdomen','nominal'],
			['packed_cell_volume','numeric'],
			['total_protein','numeric'],
			['abdominocentesis_appearance','nominal'],
			['abdomcentesis_total_protein','numeric'],
			['outcome','nominal'],
			['surgical_lesion','nominal'],
			['type_of_lesion_1','nominal'],
			['type_of_lesion_2','nominal'],
			['type_of_lesion_3','nominal'],
			['cp_data_list','nominal']]
K_of_k_means = range(10)



def data_distance(line1, line2):
	l1 = []
	l2 = []
	l1 = list2int_or_float(line1)
	l2 = list2int_or_float(line2)
	vector1 = [x for x in l1 if x != '?' and l2[l1.index(x)] != '?']
	vector2 = [x for x in l2 if x != '?' and l1[l2.index(x)] != '?']
	# sqDiffVector = vector1-vector2  
	sqDiffVector = list(map(lambda x: x[0]-x[1], zip(vector1, vector2)))
	sqDiffVector = [a*b for a, b in zip(sqDiffVector,sqDiffVector)]
	# sqDiffVector = map(lambda (a,b):a*b, zip(sqDiffVector,sqDiffVector))
    # sqDiffVector=sqDiffVector**2  
	sqDistances = sum(sqDiffVector)
	distance = sqDistances**0.5  
	return distance  

def list2int_or_float(line):
	ans = line
	for i in range(len(attr_info)):
		if attr_info[i][1] == 'nominal':
			if line[i] != '?':
				ans[i] = (int(line[i]))
		elif attr_info[i][1] == 'numeric':
			if line[i] != '?':
				ans[i] = (float(line[i]))
		else:
			return 'error'
	return ans

def data_cov(completed_data):
	numeric_data = []
	for i in range(len(completed_data)):
		numeric_data.append(list2int_or_float(completed_data[i]))
	# list2int_or_float(line1)
	# list2int_or_float(line2)
	matrix = numpy.array(numeric_data).T
	#计算两组数的相关系数
	#返回结果为矩阵，第i行第j列的数据表示第i组数与第j组数的相关系数。对角线为1
	corrcoef_matrix = numpy.corrcoef(matrix)
	return corrcoef_matrix

def list2str(sample_list):
	sample_str = ''
	for item in sample_list:
		sample_str = sample_str + str(item) + ' '
	# sample_str = str(sample_list)
	# sample_str = sample_str.replace('[','')
	# sample_str = sample_str.replace(']','') 
	# sample_str = sample_str.replace(',',' ')
	sample_str = sample_str + '\n'
	return sample_str



def data_preprocessing(case_name, attr_list, horse_colic_list):
	if case_name == 'erase':
		pass
	
	elif case_name == 'max_frequency':
		global max_frequency_attr_list 
		global max_frequency_list
		max_frequency_attr_list = [] 
		max_frequency_list = []
		max_frequency_file = open('/media/gs/study/gushuang/data/DataMining/horse-colic/max_frequency_horse-colic.data','w')
		
		for attr in range(len(attr_info)):
			temp_list1 = []
			temp_list2 = []
			erase_attr_list = []
			erase_attr_set = []
			max_frequency = 0
			frequency = 0

			temp_list1 = attr_list[attr]
			erase_attr_list = [x for x in temp_list1 if x != '?']

			#mode
			erase_attr_set = set(erase_attr_list)
			for item in erase_attr_set:
				frequency = erase_attr_list.count(item)
				if frequency > max_frequency:
					max_frequency = frequency
					attr_replace = item
			# attr_replace = mode(erase_attr_list)
			temp_list2 = [attr_replace if x=='?' else x for x in temp_list1]
			max_frequency_attr_list.append(temp_list2)
		max_frequency_list = numpy.transpose(max_frequency_attr_list).tolist()
		for item in max_frequency_list:
			max_frequency_str = list2str(item)
			max_frequency_file.write(max_frequency_str)
		max_frequency_file.close()
	
	elif case_name == 'hotdeck':
		global hotdeck_attr_list 
		global hotdeck_list
		hotdeck_list = []
		hotdeck_attr_list = []

		hotdeck_file = open('/media/gs/study/gushuang/data/DataMining/horse-colic/hotdeck_horse-colic.data','w')
		
		corrcoef_matrix = []
		corrcoef_list = []
		attr_map = []
		each_attr_map = []

		completed_data = []
		completed_attr_data = []

		#random two completed data
		for l in horse_colic_list:
			if '?' not in l:
				completed_data.append(l)
		completed_attr_data = numpy.transpose(completed_data)
		# random_list = random.sample(completed_data,2)
		# corrcoef_matrix = data_cov(random_list[0],random_list[1])
		corrcoef_matrix = data_cov(completed_data)

		# (corrcoef_matrix:28*28)
		for n in range(len(attr_info)):
			#corrcoef_list for each attr
			corrcoef_list = corrcoef_matrix[n]	
			corrcoef_list[n] = float('-Inf')
			corrcoef_list[numpy.isnan(corrcoef_list)] = float('-Inf')
			# corrcoef_list = [float('-Inf') for x in corrcoef_list if numpy.isnan(x)]
			#sort by decrease dependent on corrcoef
			attr_map.append(sorted(enumerate(corrcoef_list),key = lambda x:x[1], reverse=True))
		
		for i in range(len(horse_colic_list)):
			temp_list = []
			minimun_corr_attr = []
			uncompleted_data_index = []
			temp_list = horse_colic_list[i]
			# hotdeck_list.append(horse_colic_list[i])
			uncompleted_data_index = [x for x in range(len(attr_info)) if temp_list[x] == '?']
			#find the most relative  known attr
			for uncomplete_index in uncompleted_data_index:
				each_attr_map = attr_map[uncomplete_index]
				for m in each_attr_map:
					if m[0] not in uncompleted_data_index:
						corr_attr = m[0]
						break
				
				minimun_corr_attr = completed_attr_data[corr_attr].tolist()
				if attr_info[corr_attr][1] == 'nominal':
					minimun_corr_attr = [abs(int(x)-int(temp_list[corr_attr])) for x in minimun_corr_attr]
				elif attr_info[corr_attr][1] == 'numeric':
					minimun_corr_attr = [abs(float(x)-float(temp_list[corr_attr])) for x in minimun_corr_attr]
				else:
					print 'error'
				minimun_corr_attr_index = minimun_corr_attr.index(min(minimun_corr_attr))
				corr_list = completed_data[minimun_corr_attr_index]
				temp_list[uncomplete_index] = corr_list[uncomplete_index]
			hotdeck_list.append(temp_list)
			hotdeck_str = list2str(hotdeck_list[i])
			hotdeck_file.write(hotdeck_str)
		hotdeck_attr_list = numpy.transpose(hotdeck_list).tolist()
		hotdeck_file.close()
		
	elif case_name == 'k-means':
		global k_means_list
		global k_means_attr_list
		k_means_attr_list = []
		k_means_list = []
		k_means_file = open('/media/gs/study/gushuang/data/DataMining/horse-colic/k_means_horse-colic.data','w')
		attr_distance = [[0 for i in range(len(horse_colic_list))] for j in range(len(horse_colic_list))]
		for i in range(len(horse_colic_list)):
			for j in range(len(horse_colic_list)):
				if i == j:
					attr_distance[i][j] = float('Inf')

				if attr_distance[j][i] != 0:
					attr_distance[i][j] = attr_distance[j][i]
				else:
					temp_list1 = horse_colic_list[i]
					temp_list2 = horse_colic_list[j]
					attr_distance[i][j] = data_distance(temp_list1, temp_list2)
		# find k minimun distance
		sorted_distance = []
		minimun_k_distance = []
		minimun_k_list = []
		for i in range(len(horse_colic_list)):
			temp_list = []
			temp_list = horse_colic_list[i]
			sorted_distance = attr_distance[i]
			sorted_distance = sorted(enumerate(sorted_distance),key = lambda x:x[1])
			for attr in range(len(attr_info)):
				attr_replace = 0
				attr_replace_count = 0
				if temp_list[attr] == '?':
					for k in K_of_k_means:
						minimun_k_index = sorted_distance[k][0]
						minimun_k_list = horse_colic_list[minimun_k_index]
						if minimun_k_list[attr] == '?':
							continue
						else:
							attr_replace_count = attr_replace_count + 1
							attr_replace = attr_replace + minimun_k_list[attr]
					 
					if attr_replace_count == 0:
						temp_list[attr] = 0
					else:
						if attr_info[attr][1] == 'nominal':
							temp_list[attr] = int(attr_replace/attr_replace_count)
						elif attr_info[attr][1] == 'numeric':
							temp_list[attr] = attr_replace/attr_replace_count
						else:
							print 'error'

				else:
					continue
			k_means_list.append(temp_list)
			k_means_str = list2str(temp_list)
			k_means_file.write(k_means_str)
		k_means_file.close()
		k_means_attr_list = numpy.transpose(k_means_list).tolist()

	else:
		return 'error'

#data abstract-----1-nominal attr frequency/2-numeric attr max & min & mean & middle & 1/4 & missing
def data_abstract(each_attr_list, attr_flag, num):
	each_attr_set = []
	each_attr_abstract = []
	if attr_flag == 'nominal':
		each_attr_set = set(each_attr_list)
		for item in each_attr_set:
			each_attr_abstract.append({item: each_attr_list.count(item)})
		return each_attr_abstract

	elif attr_flag == 'numeric':
		#[missing, max, min, mean, middle, 1/4, 3/4]
		# missing_data = each_attr_list.count('?')
		each_attr_list = [float(x) for x in each_attr_list]
		each_attr_abstract.append(300 - len(each_attr_list))
		each_attr_abstract.append(max(each_attr_list))
		each_attr_abstract.append(min(each_attr_list))
		each_attr_abstract.append(numpy.mean(each_attr_list))
		each_attr_abstract.append(numpy.median(each_attr_list))
		each_attr_abstract.append(numpy.percentile(each_attr_list,25))
		each_attr_abstract.append(numpy.percentile(each_attr_list,75))

		pyplot.figure(1)
		pyplot.hist(each_attr_list, 100)
		pyplot.show()

		pyplot.figure(2)
		pyplot.boxplot(each_attr_list)
		pyplot.show()
		return each_attr_abstract

	else:
		return 'error'



#read horse-colic data
horse_colic_file = open('/media/gs/study/gushuang/data/DataMining/horse-colic/horse-colic.data')
try:
	horse_colic_lines = horse_colic_file.readlines()
	horse_colic_list = []
	attr_list = []
	
	for line in horse_colic_lines:
		temp_list = []
		line = line.replace(' \n','')
		line = line.replace('\n','')
		temp_list = line.split(' ')
		horse_colic_list.append(temp_list)

	attr_list = numpy.transpose(horse_colic_list)

except Exception as e:
	print "horse-colic.data file open failed!"
finally:
	horse_colic_file.close()

#data preprocessing---4 cases 'erase' 'max_frequency' 'hotdeck' 'k-means'

# casename = 'erase'
# casename = 'max_frequency'
# casename = 'hotdeck'
casename = 'k-means'

data_preprocessing(casename, attr_list, horse_colic_list)


horse_colic_abstract = []
for n in range(len(attr_info)):
	if casename == 'erase':
		each_attr_list = [x for x in attr_list[n] if x != '?']
	elif casename == 'max_frequency':
		each_attr_list = max_frequency_attr_list[n]
	elif casename == 'hotdeck':
		each_attr_list = hotdeck_attr_list[n]
	elif casename == 'k-means':
		each_attr_list = k_means_attr_list[n]
	else:
		print 'error'
	horse_colic_abstract.append(data_abstract(each_attr_list, attr_info[n][1], n))
	# plot
