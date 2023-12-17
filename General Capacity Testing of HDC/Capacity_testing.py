from matplotlib import image
import math                       # For useful math functions like log of 2
import matplotlib.pyplot as plt   # For plotting later
import requests                   # For extracting data saved on git
import random                     # Might be useful for randomization
import numpy as np                # Hooray numpy!
import numpy.linalg as lin
import scipy.special as ss

D = 500
p = 0.5
p_sparse = 0.01
max_p_sparse_bundle = 0.5


def u_gen_rand_hv(D):
    # Sanity checker
    if (D % 2):
        print("Error - D can't be an odd number")
        return 0

    p = 0.5
    hv = [0] * D
    nb_1s = 0
    while nb_1s < D * p:
        temp = random.randint(0, D - 1)
        if hv[temp] != 1:
            hv[temp] = 1
            nb_1s += 1
    return hv


def distance(A, B):
    return sum(np.logical_xor(A, B))


def bundle(block):
    # sanity checker
    if ((len(block) % 2) == 0):
        print("Error! Block size should be odd.")
        return

    sums = np.sum(block, axis=0)
    for x in range(len(sums)):
        if sums[x] <= (len(block)) / 2:
            sums[x] = 0
        else:
            sums[x] = 1
    return sums


def bind(A, B):
    return np.logical_xor(A, B)


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


def similarity_sparse_new(A,B):
   similarity = 0
   for i in range(D):
      if (A[i] == B[i]):
        similarity += 1
   return similarity/D


def bundle_sparse(block):
    sum = [0]*D
    for el in block:
      for i in range(len(el)):
         sum[i] += el[i]
    nb_ones = 0
    output = [0]*D
    while (nb_ones/D < max_p_sparse_bundle):
      output[sum.index(max(sum))] = 1
      sum[sum.index(max(sum))] = 0
      nb_ones += 1
    return output
      
  
def bind_segmented_shift(A, B, D):
   nb_segments = math.floor(D*p_sparse)
   length_of_segment = math.floor(D/nb_segments)
   for i in range(nb_segments-2):
      segment = A[i*length_of_segment:(i+1)*length_of_segment]
      if 1 in segment:
        #print(segment) #really odd issue, sometimes segment is not a normal list ??? solved, not understood
        shift = list(segment).index(1)
        B[i*length_of_segment:(i+1)*length_of_segment] = perm(B[i*length_of_segment:(i+1)*length_of_segment], shift)
   return B

def unbind_left_segmented_shift(Binded_hv, A, D):
    print("Error: WIP.")

def unbind_right_segmented_shift(Binded_hv, B, D):
    print("Error: WIP.")


def perm(A, N):
    return np.roll(A, N)



def create_item_mem(N, D):
    item_mem = {}
    for n in range(N):
        item_mem[n] = u_gen_rand_hv(D)
    return item_mem


def create_item_mem_sparse(N,D):
  # insert nice code here
  item_mem = {}
  for n in range(N):
    #item_mem.__setitem__(n, u_gen_rand_hv(D))
    item_mem[n] = u_gen_rand_hv_sparse(D)
  return item_mem



def similarity_search(hv_to_search_with, associative_mem_dictionary, D):
    lowest_distance_yet = D
    closest_thing_yet = '/'
    for letter_key in associative_mem_dictionary:
        if distance(hv_to_search_with, associative_mem_dictionary[letter_key]) < lowest_distance_yet:
             lowest_distance_yet = distance(hv_to_search_with, associative_mem_dictionary[letter_key])
             closest_thing_yet = letter_key

    return (closest_thing_yet, D-lowest_distance_yet)


def similarity_search_sparse(hv_to_search_with, associative_mem_dictionary, D):
    highest_similarity_yet = 0
    closest_thing_yet = '/'
    for letter_key in associative_mem_dictionary:
        if similarity_sparse_new(associative_mem_dictionary[letter_key], hv_to_search_with) > highest_similarity_yet:
             highest_similarity_yet = similarity_sparse_new(associative_mem_dictionary[letter_key], hv_to_search_with)
             closest_thing_yet = letter_key

    return (closest_thing_yet, highest_similarity_yet)



def similarity_search2(bundled_hv, item_mem, D, nb_bundled):
    closest_ones = {}
    for n in range(nb_bundled):
        lowest_distance_yet = D
        closest_thing_yet = "/"
        for hv_name in item_mem:
            if hv_name not in list(closest_ones.values()):
                if distance(bundled_hv, item_mem[hv_name]) < lowest_distance_yet:
                    lowest_distance_yet = distance(bundled_hv, item_mem[hv_name])
                    closest_thing_yet = hv_name
        closest_ones[n] = closest_thing_yet
    return closest_ones


def similarity_search2_sparse(bundled_hv, item_mem, D, nb_bundled):
    closest_ones = {}
    for n in range(nb_bundled):
        highest_similarity_yet = 0
        closest_thing_yet = "/"
        for hv_name in item_mem:
            if hv_name not in list(closest_ones.values()):
                if similarity_sparse_new(item_mem[hv_name], bundled_hv) > highest_similarity_yet:
                    highest_similarity_yet = similarity_sparse_new(item_mem[hv_name], bundled_hv)
                    closest_thing_yet = hv_name
        closest_ones[n] = closest_thing_yet
    return closest_ones



def get_nb_same_elem_in_2_lists(list1, list2):
    nb_of_same_elem = 0
    for elem in list1:
        if elem in list2:
            nb_of_same_elem += 1
    return nb_of_same_elem


#Bundle 3 then 5 then 7 HV ... up to k random hv together that are in the item_mem
#then see if all parts can be extracted by using similarity_search2 and see how many of the closest hv are the ones used in the bundle
#accuracy is the number of correct ones/number of bundled ones.
def bundle_capacity_test(k, N, D): #k should be odd
    #fill item_mem with 5*k hv
    item_mem = create_item_mem(N, D) #also functions as associative memory with numbers as keys
    size_item_mem = N
    results = {}
    for l in range(3, k, 2):
        bundled_ones = []
        block = []
        for n in range(l):
            hv_id_nb = random.randint(0, size_item_mem-1)
            bundled_ones.append(hv_id_nb)
            block.append(item_mem[hv_id_nb])
        bundled_hv = bundle(block)
        found_ones = similarity_search2(bundled_hv, item_mem, D, l)
        accuracy = get_nb_same_elem_in_2_lists(bundled_ones, list(found_ones.values()))/len(bundled_ones)
        results[l] = accuracy
    #plot results on y-axis and l on x-axis
    x = list(results.keys())
    y = list(results.values())
    plt.plot(x, y)
    plt.xlabel('k')
    plt.ylabel('Accuracy')
    plt.show()
    print(results)



#Bundle 3 then 5 then 7 HV ... up to k random hv together that are in the item_mem
#then see if all parts can be extracted by using similarity_search2 and see how many of the closest hv are the ones used in the bundle
#accuracy is the number of correct ones/number of bundled ones.
def bundle_capacity_test_sparse(k, N, D): #k should be odd
    #fill item_mem with 5*k hv
    item_mem = create_item_mem_sparse(N, D) #also functions as associative memory with numbers as keys
    size_item_mem = N
    results = {}
    for l in range(3, k, 2):
        bundled_ones = []
        block = []
        for n in range(l):
            hv_id_nb = random.randint(0, size_item_mem-1)
            bundled_ones.append(hv_id_nb)
            block.append(item_mem[hv_id_nb])
        bundled_hv = bundle_sparse(block)
        found_ones = similarity_search2_sparse(bundled_hv, item_mem, D, l)
        accuracy = get_nb_same_elem_in_2_lists(bundled_ones, list(found_ones.values()))/len(bundled_ones)
        results[l] = accuracy
    #plot results on y-axis and l on x-axis
    x = list(results.keys())
    y = list(results.values())
    plt.plot(x, y)
    plt.xlabel('k')
    plt.ylabel('Accuracy')
    plt.show()
    print(results)


#k is max number of bundled pairs to test extraction accuracy for, in each test l bundled pairs will be tested:
#take 2*l hv, bind in pairs and bundle these pairs into 1 hv
#for each pair, test if the right-binded hv of the pair can be found from the unbinding of the big_hv with the left-binded hv of the pair.
#Plot accuracy.
def unbinding_pairs_test(k, N, D):
    item_mem = create_item_mem(N, D) #also functions as associative memory with numbers as keys
    size_item_mem = N
    results = {}
    for l in range(3, k, 2):
        #bind l pairs and bundle these pairs
        left_parts_of_pairs = []
        right_parts_of_pairs = []
        block = []
        for n in range(l):
            hv_id_nb_left = random.randint(0, size_item_mem-1)
            hv_id_nb_right = random.randint(0, size_item_mem-1)
            left_parts_of_pairs.append(hv_id_nb_left)
            right_parts_of_pairs.append(hv_id_nb_right)
            block.append(bind(item_mem[hv_id_nb_left],item_mem[hv_id_nb_right]))
        bundled_hv = bundle(block)
        accuracy = 0
        for n in range(l):  
            hv_left_after_unbinding = bind(item_mem[left_parts_of_pairs[n]], bundled_hv)
            (closest_hv_found,x) = similarity_search(hv_left_after_unbinding, item_mem, D)
            if right_parts_of_pairs[n] == closest_hv_found:
                accuracy += 1
        results[l] = accuracy/l
        accuracy = 0
    #plot results on y-axis and l on x-axis
    x = list(results.keys())
    y = list(results.values())
    plt.plot(x, y)
    plt.xlabel('k')
    plt.ylabel('Accuracy')
    plt.show()
    print(results)


#k is max number of bundled pairs to test extraction accuracy for, in each test l bundled pairs will be tested:
#take 2*l hv, bind in pairs and bundle these pairs into 1 hv
#for each pair, test if the right-binded hv of the pair can be found from the unbinding of the big_hv with the left-binded hv of the pair.
#Plot accuracy.
def unbinding_pairs_test_sparse(k, N, D):
    item_mem = create_item_mem_sparse(N, D) #also functions as associative memory with numbers as keys
    size_item_mem = N
    results = {}
    for l in range(3, k, 2):
        #bind l pairs and bundle these pairs
        left_parts_of_pairs = []
        right_parts_of_pairs = []
        block = []
        hash_bind_list_of_tupples = []
        for n in range(l):
            hv_id_nb_left = random.randint(0, size_item_mem-1)
            hv_id_nb_right = random.randint(0, size_item_mem-1)
            left_parts_of_pairs.append(hv_id_nb_left)
            right_parts_of_pairs.append(hv_id_nb_right)
            block.append(bind_segmented_shift(item_mem[hv_id_nb_left], item_mem[hv_id_nb_right], D))
        bundled_hv = bundle_sparse(block)
        accuracy = 0
        for n in range(l):  
            hv_left_after_unbinding = unbind_left_segmented_shift(bundled_hv, item_mem[left_parts_of_pairs[n]], D)
            (closest_hv_found,x) = similarity_search_sparse(hv_left_after_unbinding, item_mem, D)
            if right_parts_of_pairs[n] == closest_hv_found:
                accuracy += 1
        results[l] = accuracy/l
        accuracy = 0
    #plot results on y-axis and l on x-axis
    x = list(results.keys())
    y = list(results.values())
    plt.plot(x, y)
    plt.xlabel('k')
    plt.ylabel('Accuracy')
    plt.show()
    print(results)



bundle_capacity_test_sparse(51, 1000, D)
#unbinding_pairs_test_sparse(55,250,1000)


