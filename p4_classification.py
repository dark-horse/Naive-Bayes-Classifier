import sys
import os
import math
import p4_preprocessing as pp

def print_confusion_matrix(confusion_matrix):
	"""
	prints the confusion matrix as per https://en.wikipedia.org/wiki/Confusion_matrix
	columns represent the instances in the predicted class. It is Y / N / O
		If a word in the test sample is not in the training sample
		and there is no smoothing, then a word in the test sample not present in the training sample would be classified
		as Other (because P(word / Y) = 0 and P (word / N) is 0 too
	Rows represent actual instances in the test sample
	"""
	
	print "              |   Predicted      |"
	print "----------------------------------"
	print "              |   POS  |   NEG   |"
	print "----------------------------------"
	print "Actual  | POS |        |         |"
	print "----------------------------------"
	print "class   | NEG |        |         |"
	print "----------------------------------"
	
	return

def test_dict_and_trie(test_file_name, sw_dict, train_dict, sw_trie, train_trie, train_word_count_pos_reviews, train_word_count_neg_reviews, smoothing):
	
	if (train_trie.item_count != train_dict.__len__()):
		print "error for file {}.".format(test_file_name)
		print "\tTrain trie has {} items and train dict has {} items.".format(train_trie.item_count, train_dict.__len__())
		return
	
	test_file = open(test_file_name)

	c_pos_trie = float (0)
	c_neg_trie = float (0)
	
	c_pos_dict = float (0)
	c_neg_dict = float (0)
	
	for line in test_file:
		for c in line.split():
			# calculate prob_pos and prob_neg for this word
			# c_pos = log (Prob(c / positive))
			# c_neg = log (Prob(c / negative))
			in_trie = sw_trie.in_trie(c.lower(),0)
			in_dict = sw_dict.has_key(c.lower())
			if (in_trie != in_dict):
				print "error in sw file for word {}. sw_in_trie is {} and sw_in_dict is {}.".format(c.lower(), in_trie,in_dict)
			if (in_trie | in_dict):
				continue
					
			pos_trie, neg_trie = train_trie.pos_neg_counts(c.lower(),0)
			if (train_dict.has_key(c.lower())):
				if ((pos_trie == -1) | (neg_trie == -1)):
					print "error in file {}:".format(test_file_name)
					print "\t word {} is in train_dict but not in train_trie.".format(c.lower())
				
				pos_dict = train_dict[c.lower()].pos
				neg_dict = train_dict[c.lower()].neg
				
				if ((pos_dict != pos_trie) | (neg_dict != neg_trie)):
					print "error in file {}:".format(test_file_name)
					print "\t word {} has different positive / negative counts: pos_dict {}, neg_dict {}, pos_trie {}, neg_trie {}.".format(c.lower(), pos_dict, neg_dict, pos_trie, neg_trie)
					

				cond_pos_trie = float(pos_trie + smoothing) / (train_word_count_pos_reviews + smoothing * train_trie.item_count)
				cond_neg_trie = float(neg_trie + smoothing) / (train_word_count_neg_reviews + smoothing * train_trie.item_count)
				#TODO: 
				#     If smoothing is 0 and pos or neg is 0, we will have an error: log(0) is undefined.
				#     Think about this
				c_pos_trie += math.log (cond_pos_trie)
				c_neg_trie += math.log (cond_neg_trie)

				cond_pos_dict = float(pos_dict + smoothing) / (train_word_count_pos_reviews + smoothing * train_dict.__len__())
				cond_neg_dict = float(neg_dict + smoothing) / (train_word_count_neg_reviews + smoothing * train_dict.__len__())
				#TODO: 
				#     If smoothing is 0 and pos or neg is 0, we will have an error: log(0) is undefined.
				#     Think about this
				c_pos_dict += math.log (cond_pos_dict)
				c_neg_dict += math.log (cond_neg_dict)
				
				if ((cond_pos_trie != cond_pos_dict)):
					print "error in file {}.".format(test_file_name)
					print "trie cond pos is {} and dict cond pos is {}.".format(cond_pos_trie, cond_pos_dict)

				if ((cond_neg_trie != cond_neg_dict)):
					print "error in file {}.".format(test_file_name)
					print "trie cond neg is {} and dict cond neg is {}.".format(cond_neg_trie, cond_neg_dict)
			
				if ((c_pos_trie != c_pos_dict)):
					print "error in file {}.".format(test_file_name)
					print "c_pos_trie is {} and c_pos_dict is {}.".format(c_pos_trie, c_pos_dict)

				if ((c_neg_trie != c_neg_dict)):
					print "error in file {}.".format(test_file_name)
					print "c_neg_trie is {} and c_neg_dict is {}.".format(c_neg_trie, c_neg_dict)



			else:
				if ((pos_trie != -1) | (neg_trie != -1)):
					print "error in file {}:".format(test_file_name)
					print "\t word {} is NOT in train_dict but in train_trie.".format(c.lower())


	test_file.close()

	return
	

	
	
def process_test_file_trie(test_file_name, sw_trie, train_trie, train_word_count_pos_reviews, train_word_count_neg_reviews, smoothing):
	test_file = open(test_file_name)
	
	c_pos = float (0)
	c_neg = float (0)
	
	for line in test_file:
		for c in line.split():
			if (sw_trie.in_trie(c.lower(), 0)):
				continue
			
			pos, neg = train_trie.pos_neg_counts(c.lower(),0)
			if ((pos > -1) & (neg > -1)):
				cond_pos = float(pos + smoothing) / (train_word_count_pos_reviews + smoothing * train_trie.item_count)
				cond_neg = float(neg + smoothing) / (train_word_count_neg_reviews + smoothing * train_trie.item_count)
				#TODO: 
				#     If smoothing is 0 and pos or neg is 0, we will have an error: log(0) is undefined.
				#     Think about this
				c_pos += math.log (cond_pos)
				c_neg += math.log (cond_neg)
		
	test_file.close()

	return c_pos, c_neg
	
	

def process_test_file_dict(test_file_name, sw_dict, train_dict, train_word_count_pos_reviews, train_word_count_neg_reviews, smoothing):
	test_file = open(test_file_name)
	
	c_pos = float (0)
	c_neg = float (0)
	
	for line in test_file:
		for c in line.split():
			if (sw_dict.has_key(c.lower())):
				continue
			
			if (train_dict.has_key(c.lower())):
				pos = train_dict[c.lower()].pos
				neg = train_dict[c.lower()].neg
				cond_pos = float(pos + smoothing) / (train_word_count_pos_reviews + smoothing * train_dict.__len__())
				cond_neg = float(neg + smoothing) / (train_word_count_neg_reviews + smoothing * train_dict.__len__())
				#TODO: 
				#     If smoothing is 0 and pos or neg is 0, we will have an error: log(0) is undefined.
				#     Think about this
				c_pos += math.log (cond_pos)
				c_neg += math.log (cond_neg)
		
	test_file.close()

	return c_pos, c_neg
	
def classify(sw, train, train_pos_reviews, train_neg_reviews, train_word_count_pos_reviews, train_word_count_neg_reviews, smoothing, dict_or_trie):
	"""
	The classification exercise.
	This is similar to the algorithm from 6.10 Bayesian Learning chapter in the Mitchell book.On pages 180 - 184.
	Mitchell book algorithm skips words not in the training set and the smoothing factor is set to 1.
	sw and train are the dictionaries preprocessed at the earlier stage.
	smoothing is the Laplace smoothing factor.
	Returns the confusion matrix and the accuracy of the classifier.
	"""

	test_folder = "C:\\Users\\dherling\\My Stuff\\Personal\\Machine Learning\\CMU 701 Course - Fall 2016\\Problem Sets\\HW1\\Problem 4 - IMDB DataSet\\hw1_dataset_nb\\test"
	
	# probability positive = # positive Reviews / (# positive Reviews + # negative Reviews)
	prob_pos = float(train_pos_reviews) / (train_pos_reviews + train_neg_reviews)
	prob_neg = float(1.0) - prob_pos
	
	#first, test the positive reviews
	act_pos_reviews = 0
	predicted_pos_reviews = 0
	pos_review_folder = test_folder + "\\pos"
	for pos_file_name in os.listdir(pos_review_folder):
		act_pos_reviews += 1
		pos_file_name = pos_review_folder + "\\" + pos_file_name
		
		if (dict_or_trie):
			#dict
			c_pos, c_neg = process_test_file_dict(pos_file_name, sw, train, train_word_count_pos_reviews, train_word_count_neg_reviews, smoothing)
		else:
			#trie
			c_pos, c_neg = process_test_file_trie(pos_file_name, sw, train, train_word_count_pos_reviews, train_word_count_neg_reviews, smoothing)

		#adjust for the total Positive / Negative Reviews in the training data
		c_pos += math.log (prob_pos)
		c_neg += math.log (prob_neg)
		
		if (c_pos > c_neg):
			predicted_pos_reviews += 1

	#now, test the negative reviews
	act_neg_reviews = 0
	predicted_neg_reviews = 0
	neg_review_folder = test_folder + "\\neg"
	for neg_file_name in os.listdir(neg_review_folder):
		act_neg_reviews += 1
		neg_file_name = neg_review_folder + "\\" + neg_file_name

		if (dict_or_trie):
			#dict
			c_pos, c_neg = process_test_file_dict(neg_file_name, sw, train, train_word_count_pos_reviews, train_word_count_neg_reviews, smoothing)
		else:
			#trie
			c_pos, c_neg = process_test_file_trie(neg_file_name, sw, train, train_word_count_pos_reviews, train_word_count_neg_reviews, smoothing)

		#adjust for the total Positive / Negative Reviews in the training data
		c_pos += math.log (prob_pos)
		c_neg += math.log (prob_neg)

		if (c_neg > c_pos):
			predicted_neg_reviews += 1	

	#build the confusion matrix
	cm = [[0]*2]*2
	cm [0] = [predicted_pos_reviews, act_pos_reviews - predicted_pos_reviews]
	cm [1] = [predicted_neg_reviews, act_neg_reviews - predicted_neg_reviews]
	
	# and classification accuracy
	class_acc = float (predicted_pos_reviews + predicted_neg_reviews) / (act_pos_reviews + act_neg_reviews)
	return cm, class_acc
