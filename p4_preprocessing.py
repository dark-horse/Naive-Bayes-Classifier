import sys
import os

class word_trie (object):
	"""
	A structure to keep track of words we have read so far.
	Words are made of characters (lower case and upper case characters are different)
	Each node contains:
		number of words under the node
		current character
		an indicator whether or not this is the end of the word (to distinguish between "fast"/"faster"/"fastest" for example
		if this is the end of the word, then also include 
			positive_count (how many times this word was in a positive review) 
			negative_count (how many times this word was in a negative review) 
		a list of further nodes.
		As an example, the trie that contains "fast", "faster", "fastest" looks like this
				'f', END = False ->'a', END = False ->'s', END = False->'t', END = True->'e', END = False->'r', END = True
				                                                                                         ->'s', END = False->'t', END = True
	"""
	def __init__(self, head_trie, ch):
		self.head_trie = head_trie
		self.curr_ch = ch
		self.item_count = 0
		self.end_word = False
		self.pos_count = 0
		self.neg_count = 0
		self.nodes_occupied = 0
		self.nodes = [word_trie] * 0
		return
		
	def in_trie(self, input_word, depth):
		"""
		return true if word_trie contains input_word
		"""
		curr_node = self
		for i in range(depth, input_word.__len__()):
			ch = input_word[depth]
			for i in range(0, self.nodes_occupied):
				curr_node = self.nodes[i]
				if (ch == curr_node.curr_ch):
					if (input_word.__len__() - depth == 1):
						return curr_node.end_word
					
					return curr_node.in_trie(input_word, depth+1)
				
		#if we got here, we searched all the nodes and did not find anything
		return False
	
	def pos_neg_counts(self, input_word, depth):
		"""
		returns the positive / negative counts for the input word if the input word is in the trie
		otherwise returns -1 / -1
		"""
		curr_node = self
		for i in range(depth, input_word.__len__()):
			ch = input_word[depth]
			for i in range(0, self.nodes_occupied):
				curr_node = self.nodes[i]
				if (ch == curr_node.curr_ch):
					if (input_word.__len__() - depth == 1):
						if (curr_node.end_word):
							return curr_node.pos_count, curr_node.neg_count
						else:
							return -1, -1
				
					return curr_node.pos_neg_counts(input_word, depth+1)
		
		#not found
		return -1, -1


	def add_word (self, new_word, positive_review, depth):
		"""
		adds a word to the trie.
		If this word is not in the trie return 1 otherwise return 0.
		"""
		ch = new_word[depth]
		
		for i in range(0, self.nodes_occupied):
			curr_node = self.nodes[i]
			if (ch == curr_node.curr_ch):
				add = 0
				if (new_word.__len__() - depth == 1):
					# this is the last character in the node
					if (curr_node.end_word == False):
						# new word
						add = 1
						self.item_count += 1
					curr_node.end_word = True
					if (positive_review):
						curr_node.pos_count += 1
					else :
						curr_node.neg_count += 1
				else:
					add = curr_node.add_word(new_word,positive_review, depth + 1)
					self.item_count += add
				return add
		
		# so we did not find a word in the trie that start with new_word[0]
		new_node = word_trie (False, ch)
		if (self.nodes_occupied == self.nodes.__len__()):
			#grow the nodes
			new_len = self.nodes.__len__()
			if (new_len == 0):
				new_len = 1
			else:
				new_len += new_len
			new_nodes = [word_trie]*new_len
			for i in range(0,self.nodes_occupied):
				new_nodes[i] = self.nodes[i]
			self.nodes = new_nodes
		
		self.nodes[self.nodes_occupied] = new_node	
		self.nodes_occupied += 1
		self.item_count += 1
		
		if (new_word.__len__() - depth == 1):
			new_node.end_word = True
			if (positive_review):
				new_node.pos_count += 1
			else:
				new_node.neg_count += 1
		else:
			new_node.add_word(new_word,positive_review, depth + 1)
		
		return 1;

	def print_word_trie(self, print_out):
		if (not self.head_trie):
			print_out += self.curr_ch
		if (self.end_word):
			print "TRIE has\t\t\t\t\t{} with {} positives and {} negatives".format(print_out, self.pos_count, self.neg_count)
		for i in range(0, self.nodes_occupied):
			node = self.nodes[i]
			node.print_word_trie(print_out)
		return
	
	def items_count(self):
		items_count = 0
		for i in range (0, self.nodes_occupied):
			items_count += self.nodes[i].items_count()
		
		if (self.end_word):
			items_count += 1
		
		return items_count
	
	#end Word_trie class

class pos_neg_tuple:
	def __init__(self, pos, neg):
		self.pos = pos
		self.neg = neg
	#end pos_neg_tuple class

	
def preprocess():
	"""
	This method will:
	1. Read all the words in the training data set
	2. skip all the words in the sw.txt file 
	2. Count how many time each word is in a positive review / how many times it is in a negative review
	3. Output this results to a pre_processing file that can be read by another program
	"""
	train_folder = "C:\\Users\\dherling\\My Stuff\\Personal\\Machine Learning\\CMU 701 Course - Fall 2016\\Problem Sets\\HW1\\Problem 4 - IMDB DataSet\\hw1_dataset_nb\\train"
	sw_file_path = "C:\\Users\\dherling\\My Stuff\\Personal\\Machine Learning\\CMU 701 Course - Fall 2016\\Problem Sets\\HW1\\Problem 4 - IMDB DataSet\\hw1_dataset_nb\\sw.txt"
	
	# create the sw trie
	sw_trie = word_trie(True, 'A')
	sw_file = open(sw_file_path)
	for line in sw_file:
		new_word = line.__getslice__(0, line.__len__()-1)
		sw_trie.add_word(new_word.lower(), True, 0)
	sw_file.close()
	
	#TO DO: make all word lower case
	
	train_trie = word_trie(True, 'B')
	# train on the positive reviews
	# we need to count the positive reviews to calculate positive probability
	pos_reviews = 0
	word_count_pos_reviews = 0
	pos_review_folder = train_folder + "\\pos"
	for pos_file_name in os.listdir(pos_review_folder):
		pos_file = open(pos_review_folder + "\\" + pos_file_name)
		pos_reviews += 1
		for line in pos_file:
			for c in line.split():
				pos_count, neg_count = train_trie.pos_neg_counts(c.lower(),0)
				if (pos_count < 1):
					# we only count the distinct words in the positive reviews
					word_count_pos_reviews += 1
				train_trie.add_word(c.lower(), True, 0)
				
		pos_file.close()
	
	#train on the negative reviews
	# we need to count the negative reviews to calculate negative probability
	neg_reviews = 0
	word_count_neg_reviews = 0
	neg_review_folder = train_folder + "\\neg"
	for neg_file_name in os.listdir(neg_review_folder):
		neg_file = open(neg_review_folder + "\\" + neg_file_name)
		neg_reviews += 1
		for line in neg_file:
			for c in line.split():
				pos_count, neg_count = train_trie.pos_neg_counts(c.lower(),0)
				if (neg_count < 1):
					# we only count the distinct words in the negative reviews
					word_count_neg_reviews += 1
				train_trie.add_word(c.lower(), False, 0)
		neg_file.close()
		
	
	return sw_trie, train_trie, pos_reviews, neg_reviews, word_count_pos_reviews, word_count_neg_reviews
	
def preprocess_dict():
	"""
	check if using the Python dictionary is more efficient than our trie.
	sw and train tries take 420 megs of memory and 1 minute to load the sw and train data set	
	it looks like a dictionary sw and train take only 60 megs of memory and takes 15 seconds to load .... Why?????
	"""
	train_folder = "C:\\Users\\dherling\\My Stuff\\Personal\\Machine Learning\\CMU 701 Course - Fall 2016\\Problem Sets\\HW1\\Problem 4 - IMDB DataSet\\hw1_dataset_nb\\train"
	sw_file_path = "C:\\Users\\dherling\\My Stuff\\Personal\\Machine Learning\\CMU 701 Course - Fall 2016\\Problem Sets\\HW1\\Problem 4 - IMDB DataSet\\hw1_dataset_nb\\sw.txt"

	sw = {}
	sw_file = open(sw_file_path)
	for line in sw_file:
		new_word = line.__getslice__(0, line.__len__()-1)
		sw[new_word.lower()] = True
	sw_file.close()
	
	train = {}
	# we need to count the positive reviews to calculate positive probability
	pos_reviews = 0
	word_count_pos_reviews = 0
	pos_review_folder = train_folder + "\\pos"
	for pos_file_name in os.listdir(pos_review_folder):
		pos_file = open(pos_review_folder + "\\" + pos_file_name)
		pos_reviews += 1
		for line in pos_file:
			for c in line.split():
				c = c.lower()
				if train.__contains__(c):
					if (train[c].pos == 0):
						# we only count the distinct words in the positive reviews
						word_count_pos_reviews += 1
					train[c].pos += 1
				else:
					pos = pos_neg_tuple(1,0)
					train[c] = pos
					# we only count the distinct words in the positive reviews
					word_count_pos_reviews += 1
		pos_file.close()
	
	#train on the negative reviews
	# we need to count the negative reviews to calculate negative probability
	neg_reviews = 0
	word_count_neg_reviews = 0
	neg_review_folder = train_folder + "\\neg"
	for neg_file_name in os.listdir(neg_review_folder):
		neg_file = open(neg_review_folder + "\\" + neg_file_name)
		neg_reviews += 1
		for line in neg_file:
			for c in line.split():
				c = c.lower()
				if train.__contains__(c):
					if (train[c].neg == 0):
						# we only count the distinct words in the negative reviews
						word_count_neg_reviews += 1
					train[c].neg += 1
				else:
					pos = pos_neg_tuple(0,1)
					train[c] = pos
					# we only count the distinct words in negative reviews
					word_count_neg_reviews += 1
		neg_file.close()
		

	return sw, train, pos_reviews, neg_reviews, word_count_pos_reviews, word_count_neg_reviews