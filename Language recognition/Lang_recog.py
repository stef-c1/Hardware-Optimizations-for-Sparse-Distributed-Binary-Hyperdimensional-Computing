import numpy as np
import random
import math

D = 1000
N = 3
p = 0.5 
p_sparse = 0.01
max_p_sparse_bundle = 0.50
hash_bind_list_of_tupples = []

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

def distance(A,B):
    # Insert nice code here
    return sum(np.logical_xor(A,B))

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

def bind(A,B):
  # insert nice code here
  return np.logical_xor(A,B)


####SPARSE#####
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
      if (A[i] == 1 & B[i] == 1):
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
      

def bind_sparse_hash_table_shift(A,B,hash_bind_list_of_tupples):
  #turn A into a hash that will be used to shift B
  (is_hv_in_hash_list_bool, hash_value_of_A) = is_hv_in_hash_list(A, hash_bind_list_of_tupples)
  if (is_hv_in_hash_list_bool):
    return perm(B, hash_value_of_A)
  else:
    hash_value_of_A = put_hv_in_hash_list(A,hash_bind_list_of_tupples)
    return perm(B, hash_value_of_A)
  

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
   


def random_permutation_list(K):
   result = []
   i = 0
   while (i < K):
      rand_int = random.randint(1,5*K)
      if rand_int not in result:
         result.append(rand_int)
         i += 1
   return result

#K = 1/(p_sparse*len(bundle_to_bind)**2), for n=4, p_sparse=0.02 -> K=3
def bind_CDT(bundle_to_bind):
  
  Z_hv = [0]*D
  for hv in bundle_to_bind:
     Z_hv = np.logical_or(hv,Z_hv)
  Z_hv_ORed = [0]*D
  for permut in random_perm_list:
     Z_hv_ORed = np.logical_or(Z_hv_ORed, perm(Z_hv, permut))
  return np.logical_and(Z_hv, Z_hv_ORed)



def is_hv_in_hash_list(hv, hash_list_of_tupples):
  for el in hash_list_of_tupples:
    if (similarity_sparse_new(el[0], hv) == 1.0): #so they are the same 
      return (True, el[1])
  return (False, 0)


def put_hv_in_hash_list(hv, hash_list_of_tupples):
  dont_stop = 1
  while(dont_stop):
    hash_value = random.randint(1,D-1)
    already_used = 0
    for el in hash_list_of_tupples:
      if (el[1] == hash_value):
        already_used = 1
        break
    if (already_used == 0): 
      dont_stop = 0

  hash_list_of_tupples.append((hv, hash_value))
  return hash_value
  


def perm(A,N):
  # insert nice code here
  return np.roll(A,N)



def build_IM(D):
    letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',' ']
    IM = {}
    for letter in letters:
        hv = u_gen_rand_hv(D)
        IM[letter] = hv
    return IM

def build_IM_sparse(D):
    letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',' ']
    IM = {}
    for letter in letters:
        hv = u_gen_rand_hv_sparse(D)
        IM[letter] = hv
    return IM


def build_language_AM(D, N, IM):
    languages = ['bul','ces','dan','deu','ell','eng','est','fin','fra','hun','ita','lav','lit','nld','pol','por','ron','slk','slv','spa','swe']
    language_AM = {}
    for lang in languages:
        file = open("Language txt files\\"+ lang +".txt", "r")
        content = file.read()
        hv = make_hv_from_txt(content, D, N, IM)
        language_AM[lang] = hv
    return language_AM

def build_language_AM_sparse(D, N, IM):
    languages = ['bul','ces','dan','deu','ell','eng','est','fin','fra','hun','ita','lav','lit','nld','pol','por','ron','slk','slv','spa','swe']
    language_AM = {}
    for lang in languages:
        file = open("Language txt files\\"+ lang +".txt", "r")
        content = file.read()
        hv = make_hv_from_txt_sparse(content[1:15000], D, N, IM)
        language_AM[lang] = hv
    return language_AM


def make_hv_from_txt(txt, D, N, IM):
    i = 0
    bundle_of_hv = []
    while (i < len(txt)-(N+1)):
        Ngram = txt[i:i+N]
        Ngram_hv = IM[Ngram[0]]
        for j in range(1,N):
            Ngram_hv = bind(Ngram_hv, perm(IM[Ngram[j]],j))
        bundle_of_hv.append(Ngram_hv)
        i += 1
    if (len(bundle_of_hv) % 2 == 0):
       bundle_of_hv.pop()
    total_hv = bundle(bundle_of_hv)
    return total_hv

def make_hv_from_txt_sparse(txt, D, N, IM):
    i = 0
    bundle_of_hv = []
    while (i < len(txt)-(N+1)):
        Ngram = txt[i:i+N]
        Ngram_hv = IM[Ngram[0]]
        for j in range(1,N):
            Ngram_hv = bind_segmented_shift(Ngram_hv, perm(IM[Ngram[j]], j), D)
        bundle_of_hv.append(Ngram_hv)
        i += 1
    if (len(bundle_of_hv) % 2 == 0):
       bundle_of_hv.pop()
    total_hv = bundle_sparse(bundle_of_hv)
    return total_hv

def make_hv_from_txt_sparse_CDT(txt, D, N, IM):
    i = 0
    bundle_of_hv = []
    while (i < len(txt)-(N+1)):
        Ngram = txt[i:i+N]
        bundle_to_bind = [IM[Ngram[0]]]
        for j in range(1,N):
          bundle_to_bind.append(perm(IM[Ngram[j]],j))  
        Ngram_hv = bind_CDT(bundle_to_bind)
        bundle_of_hv.append(Ngram_hv)
        i += 1
    if (len(bundle_of_hv) % 2 == 0):
       bundle_of_hv.pop()
    total_hv = bundle_sparse(bundle_of_hv)
    return total_hv



def similarity_search(hv, AM, D):
    lowest_distance_yet = D
    closest_language_yet = '0'
    for language in AM:
        if distance(hv, AM[language]) < lowest_distance_yet:
           lowest_distance_yet = distance(hv, AM[language])
           closest_language_yet = language

    return (closest_language_yet, lowest_distance_yet)

def similarity_search_sparse(hv, AM, D):
    highest_similarity_yet = 0
    closest_language_yet = '0'
    for language in AM:
        if similarity_sparse_new(hv, AM[language]) > highest_similarity_yet:
           highest_similarity_yet = similarity_sparse_new(hv, AM[language])
           closest_language_yet = language

    return (closest_language_yet, highest_similarity_yet)


def test_language_recognition(IM, AM, D, N,tests):
   score = 0
   repeatings = 3
   print_flag = True
   for test in tests:
      file = open("Language txt files\\testing_texts\\"+test+".txt", "r")
      content = file.read()
      for i in range(repeatings):
        test_hv = make_hv_from_txt(content, D, N, IM)
        (found_language, distance) = similarity_search(test_hv, AM, D)
        if found_language == tests[test]:
            score += 1
            if(print_flag):
                print("CORRECT prediction! Found language: " + found_language + " similarity_score: " + str((D-distance)/D))
        else:
            if(print_flag):
                print("WRONG prediction! Found language: " + found_language + " similarity_score: " + str((D-distance)/D))
   test_len = len(tests)*repeatings
   print("Final accuracy is: %f" % (score/test_len*100))


def test_language_recognition_sparse(IM, AM, D, N,tests):
   score = 0
   repeatings = 1
   print_flag = True
   for test in tests:
      file = open("Language txt files\\testing_texts\\"+test+".txt", "r")
      content = file.read()
      for i in range(repeatings):
        print(test)
        test_hv = make_hv_from_txt_sparse(content, D, N, IM)
        (found_language, similarity) = similarity_search_sparse(test_hv, AM, D)
        if found_language == tests[test]:
            score += 1
            if(print_flag):
                print("CORRECT prediction! Found language: " + found_language + " similarity_score: " + str(similarity))
        else:
            if(print_flag):
                print("WRONG prediction! Found language: " + found_language + " similarity_score: " + str(similarity))
   test_len = len(tests)*repeatings
   print("Final accuracy is: %f" % (score/test_len*100))
   return score/test_len*100



random_perm_list = random_permutation_list(11) #for p_sparse = 0.01, N = 3 (as we bind N letters together, N from N-gram)

lang = {'pl':'pol','nl':'nld','it':'ita','fr':'fra','fi':'fin','et':'est','es':'spa','en':'eng','el':'ell','de':'deu','da':'dan','cs':'ces','bg':'bul','hu':'hun','lt':'lit','lv':'lav','pt':'por','ro':'ron','sk':'slk','sl':'slv','sv':'swe'}
tests = {}
for l in lang:
    for i in range(2,250): #max range(2,1000)
        tests[l+"_"+str(i)+"_p"] = lang[l]


mean_list = []
i = 0
while (i < 10):
  IM = build_IM_sparse(D)
  AM = build_language_AM_sparse(D,N,IM)
  mean_list.append(test_language_recognition_sparse(IM,AM,D,N,tests))
  i += 1
mean = sum(mean_list)/len(mean_list)
print("Mean: " + str(mean) + "%")


#sparse got 75% (for improved functions) on the first 50 tests and with 10,000 char of the learning sets (hash table binding)
#sparse got 78% with segmented shifting (D=1000, p_sparse=0.05)
#sparse with CDT could not get to work as all AM language vectors are very alike because CDT binding still resembles its constituent parts, 
#so we get a bunch of language vectors all made from the same 27 initial vectors these language vectors then are all similar to the 27 IM vectors
#so all these language vectors look a lot like each other and the similarity search has a hard time distinguishing them.


####Getting Accuracy as in Paper####
#Test: segmented shift binding, full training set, first 250 tests, p_sparse 0.01, max_p_sparse_bundle 0.50 -> 87.48% (mean after 10 runs)
