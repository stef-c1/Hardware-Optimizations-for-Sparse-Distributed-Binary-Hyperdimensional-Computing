###############################################
# PLEASE DO NOT CHANGE ANYTHING IN THIS CODE BLOCK!
###############################################

###############################################
# Import useful packages for convenience
###############################################
from matplotlib import image
import math                       # For useful math functions like log of 2
import matplotlib.pyplot as plt   # For plotting later
import requests                   # For extracting data saved on git
import random                     # Might be useful for randomization
import numpy as np                # Hooray numpy!
import numpy.linalg as lin
import scipy.special as ss

###############################################
# We made these for you! Use it wisely :)
###############################################

###############################################
# Such an inefficient way of converting binary text
# into a list. Sorry this is just us being lazy. But you
# get the idea :P
###############################################
def convert_to_list(raw_img):
  converted_list = []
  temp_row = []
  for i in raw_img:
    if(i != '\n'):
      if(i == '0'):
        temp_row.append(0)
      else:
        temp_row.append(1)
    else:
      converted_list.append(temp_row)
      temp_row = []

  return converted_list

###############################################
# Displaying listed data as images
###############################################
def display_img(img_data):
  plt.imshow(img_data, cmap='Greys',  interpolation='nearest')
  plt.axis('off')
  return

###############################################
# Adding noise to the system
###############################################
def add_noise(data,noise_prob):

  # Initialize noisy data
  noisy_data = []

  # Sanity checker
  if(noise_prob < 0 or noise_prob > 1):
    print("Error! Noise probability isn't correct")
    return

  # Get total length per row
  col_length = len(data[0])

  # Generate fixed length
  shuffle_list = [x for x in range(col_length)]
  cutoff_idx = round(col_length * noise_prob)

  # Iterate per row
  for row in data:

    # Do random indexing
    random.shuffle(shuffle_list)
    temp_row = []

    # Start flipping bits
    for i in range(col_length):
      if(shuffle_list[i] < cutoff_idx):
        if(row[i] == 0):
          temp_row.append(1)
        else:
          temp_row.append(0)
      else:
        temp_row.append(row[i])

    noisy_data.append(temp_row)

  return noisy_data

###############################################
# This just displays a clean set of letters
###############################################
def show_set(clean_letters):

  fig, axs = plt.subplots(6, 5, figsize=(20, 20))

  counter = 0
  for i in range(5):
    for j in range(5):
      axs[i,j].imshow(1-np.reshape(clean_letters[i*5+j],(7,5)), cmap='Greys',  interpolation='nearest')

  axs[5,0].axis('off')
  axs[5,1].axis('off')

  axs[5,2].imshow(1-np.reshape(clean_letters[25],(7,5)), cmap='Greys',  interpolation='nearest')

  axs[5,3].axis('off')
  axs[5,4].axis('off')

  plt.show()

###############################################
# Displays a single letter
###############################################
def show_letter(letter):
  plt.imshow(1-np.reshape(letter,(7,5)), cmap='Greys',  interpolation='nearest')

###############################################
# Magnitude counter
###############################################
def get_mag(A):
  return np.sum(A)

###############################################
# Importing data
###############################################
# This data set contains all the letter from A to Z
# Each row is a vectorized version of the letter
# Each letter image has 7x5 pixel dimensions
# The data set is arranged such that A is the first row and Z is the last
# We made them into arrays too for simplicity
clean_letters = convert_to_list(list(requests.get('https://raw.githubusercontent.com/rgantonio/CoE161---FileDump/main/letters.txt').text))
clean_letters = np.array(clean_letters)


D    = 1000
mean = D*0.5
var  = D*0.5*0.5
std  = np.sqrt(var)
p = 0.5
p_sparse = 0.02
max_p_sparse_bundle = 0.80


def u_gen_rand_hv(D):

    # Sanity checker
    if (D % 2 != 0):
        print("Error - D needs to be divisible by 2")
        return 0
    
    #use long index list, generate range and then permute them and set all numbers < p*D to 1 to get better density !! (random indexing also faster)
    hv = [*range(D)]
    np.random.shuffle(hv)
    for i in range(len(hv)):
        if hv[i] < p*D:
          hv[i] = 1
        else:
          hv[i] = 0
    return hv


def u_gen_rand_hv_sparse(D):

    # Sanity checker
    if (D % 2 != 0):
        print("Error - D needs to be divisible by 2")
        return 0
    
    #use long index list, generate range and then permute them and set all numbers < p*D to 1 to get better density !! (random indexing also faster)
    hv = [*range(D)]
    np.random.shuffle(hv)
    for i in range(len(hv)):
        if hv[i] < p_sparse*D:
          hv[i] = 1
        else:
          hv[i] = 0
    return hv



def distance(A,B):
    # Insert nice code here
    return sum(np.logical_xor(A,B))



def similarity_sparse(A,B):
   similarity = 0
   for i in range(D):
      if (A[i] == 1 & B[i] == 1):
        similarity += 1
   return similarity/D
      


def bundle(block):

  # sanity checker
  if((len(block) % 2) == 0):
    print("Error! Block size should be odd.")
    return

  # insert nice code in here
  sums = np.sum(block, axis = 0)
  for x in range(len(sums)):
    if sums[x] <= (len(block))/2:
      sums[x] = 0
    else:
      sums[x] = 1
  return sums



def bundle_sparse(block):

  # sanity checker
  if((len(block) % 2) == 0):
    print("Error! Block size should be odd.")
    return

  # insert nice code in here
  output = [0]*D
  for i in range(len(block)):
    part_block = block[i]
    for j in range(D):
        if (part_block[j] == 1):
            output[j] = 1
  #need to reduce the bundled hv to much higher treshold max_p_sparse_bundle density to keep the information and not get filled up completly either.
  #not really necessary for char recog here as low amount of (35) vectors to bundle together? for p_sparse of 5% needed
  nb_1s_in_output = 0 
  for i in range(D):
    if (output[i]):
      nb_1s_in_output += 1
  while (nb_1s_in_output > max_p_sparse_bundle*D):
    temp = random.randint(0, D-1)
    if (output[temp] == 1):
        output[temp] = 0
        nb_1s_in_output -= 1
  return output



def perm(A,N):
  # insert nice code here
  return np.roll(A,N)



def create_item_mem(N,D):
  # insert nice code here
  item_mem = {}
  for n in range(N):
    #item_mem.__setitem__(n, u_gen_rand_hv(D))
    item_mem[n] = u_gen_rand_hv(D)
  return item_mem


def create_item_mem_sparse(N,D):
  # insert nice code here
  item_mem = {}
  for n in range(N):
    #item_mem.__setitem__(n, u_gen_rand_hv(D))
    item_mem[n] = u_gen_rand_hv_sparse(D)
  return item_mem

###############################################
# Create the item memory for CHAR application
###############################################
letter_im = create_item_mem(35,D)
letter_im_sparse = create_item_mem_sparse(35,D)


def hdc_encode(letter, letter_im, D):
  # Insert nice code here
  block = []
  for x in range(len(letter)):
    if letter[x] == 0:
        block.append(perm(letter_im[x],1))
    else:
      block.append(letter_im[x])
  return bundle(block)


def hdc_encode_sparse(letter, letter_im_sparse, D):
  # Insert nice code here
  block = []
  for x in range(len(letter)):
    if letter[x] == 0:
        block.append(perm(letter_im_sparse[x],1))
    else:
      block.append(letter_im_sparse[x])
  return bundle_sparse(block)


###############################################
# Create the associative memory for CHAR application
###############################################
keys = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

letter_am = dict()
for i in range(len(keys)):
  letter_am[keys[i]] = hdc_encode(clean_letters[i],letter_im,D)

letter_am_sparse = dict()
for i in range(len(keys)):
  letter_am_sparse[keys[i]] = hdc_encode_sparse(clean_letters[i],letter_im_sparse,D)



def similarity_search(letter,letter_im,letter_am,D):
  # insert nice code here
  who_can_it_beeeee_now = hdc_encode(letter, letter_im, D)
  lowest_distance_yet = D
  closest_letter_yet = '0'
  for letter_key in letter_am:
    if distance(who_can_it_beeeee_now, letter_am[letter_key]) < lowest_distance_yet:
      lowest_distance_yet = distance(who_can_it_beeeee_now, letter_am[letter_key])
      closest_letter_yet = letter_key

  return (closest_letter_yet,lowest_distance_yet)


def similarity_search_sparse(letter,letter_im_sparse,letter_am_sparse,D):
  # insert nice code here
  who_can_it_beeeee_now = hdc_encode_sparse(letter, letter_im_sparse, D)
  highest_similarity_yet = 0
  closest_letter_yet = '0'
  for letter_key in letter_am_sparse:
    if similarity_sparse(who_can_it_beeeee_now, letter_am_sparse[letter_key]) > highest_similarity_yet:
      highest_similarity_yet = similarity_sparse(who_can_it_beeeee_now, letter_am_sparse[letter_key])
      closest_letter_yet = letter_key

  return (closest_letter_yet,highest_similarity_yet)


###############################################
# Model testing function
###############################################
def test_model(test_data,correct_values,letter_im,letter_am,D,print_flag):

  # Simply iterate through all elements in the clean_letters set
  score = 0
  test_len = len(test_data)
  for i in range(test_len):

    sim_letter, sim_score = similarity_search(test_data[i],letter_im,letter_am,D)


    if sim_letter == correct_values[i]:
      score += 1
      if(print_flag):
        print("CORRECT prediction! sim_letter: " + sim_letter + " sim_score: " + str(sim_score))
    else:
      if(print_flag):
        print("WRONG prediction! sim_letter: " + sim_letter + " sim_score: " + str(sim_score))

  print("Final accuracy is: %f" % (score/test_len*100))


def test_model_sparse(test_data,correct_values,letter_im_sparse,letter_am_sparse,D,print_flag):

  # Simply iterate through all elements in the clean_letters set
  score = 0
  test_len = len(test_data)
  for i in range(test_len):

    sim_letter, sim_score = similarity_search_sparse(test_data[i],letter_im_sparse,letter_am_sparse,D)


    if sim_letter == correct_values[i]:
      score += 1
      if(print_flag):
        print("CORRECT prediction! sim_letter: " + sim_letter + " sim_score: " + str(sim_score))
    else:
      if(print_flag):
        print("WRONG prediction! sim_letter: " + sim_letter + " sim_score: " + str(sim_score))

  print("Final accuracy is: %f" % (score/test_len*100))


###############################################
# Distoring images - AKA adding controlled noise
###############################################
def distort_img(image,N):

  # Since we know we have 35 pixels only
  # We can do random indexing for this part
  rand_idx = [x for x in range(35)]
  random.shuffle(rand_idx)

  # Initialize some empty image to avoid referencing issues
  ret_img = np.zeros(35)

  for i in range(35):

    # if the random idx is in the distortion list
    # let's flip bits
    if(rand_idx[i] < N):
      if(image[i] == 0):
        ret_img[i] = 1
      else:
        ret_img[i] = 0
    else:
      ret_img[i] = image[i]

  return ret_img



###############################################
# Variations and testing
###############################################

def create_test_set(clean_letters, M, N):

  labels = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

  # Initialize empty lists
  test_data = []
  test_answers = []

  for i in range(len(clean_letters)):
    for j in range(M):
      test_data.append(distort_img(clean_letters[i],N))
      test_answers.append(labels[i])

  return test_data, test_answers


###############################################
# Testing out distortions
###############################################

# Tunable parameters
N_distortions = 4
M_repetitions = 50
display_log   = False


# First create the test data
test_data, test_answers = create_test_set(clean_letters, M_repetitions, N_distortions)

# Test using our model earlier
test_model_sparse(test_data, test_answers, letter_im_sparse, letter_am_sparse, D, display_log)
test_model(test_data, test_answers, letter_im, letter_am, D, display_log)


#Sparse (50 repetitions, 0.02 p_sparse, 0.80 max_p_sparse_bundle):
#100 for 0 distortions
#98.69 for 1 distortion
#97.23 for 2 distortions
#93.54 for 4 distortions
#87.15 for 6 distortions
#72.77 for 8 distortions
#63.08 for 9 distortions
#54.46 for 10 distortions



#Dense (50 repetitions): 
#100 for 0 distortions
#98.62 for 1 distortion
#97.77 for 2 distortions
#92.85 for 4 distortions
#83.23 for 6 distortions
#69.08 for 8 distortions
#57.31 for 9 distortions
#50.54 for 10 distortions