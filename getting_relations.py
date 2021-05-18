import copy

################### Getting relations ###################

######## start and end events ########
def get_start_and_ends_events(in_log_matrix):
  start_set = []
  end_set = []
  for log_array in in_log_matrix:
    if log_array[0] not in start_set:
      start_set.append(log_array[0])
    if log_array[-1] not in end_set:
      end_set.append(log_array[-1])
  return start_set,end_set


######## dicrect successors with counter ########
def check_consecutive(dictionary, key, element):
  add_new_key_succ(dictionary, key)
  if element:
    add_new_element_succ(dictionary, key, element)

def add_new_key_succ(dictionary, key):
  if key not in dictionary.keys():
    dictionary[key]={'successors':[],'counter':[]}
  return 0

def add_new_element_succ(dictionary, key, element):
  if element not in dictionary[key]['successors']:
    dictionary[key]['successors'].append(element)
    dictionary[key]['counter'].append(1)
  else:
    idx = dictionary[key]['successors'].index(element)
    dictionary[key]['counter'][idx] += 1
  return 0

def sort_dict(dictionary):
  dictionary_items = dictionary.items()
  sorted_items = sorted(dictionary_items)
  return sorted_items

def get_direct_successors(in_log_matrix):
  dictionary = {}
  for log_array in in_log_matrix:
    for i in range(len(log_array)):
      if i == len(log_array) - 1:
        if i not in dictionary:
          check_consecutive(dictionary, log_array[i], None)
      else:
        check_consecutive(dictionary, log_array[i], log_array[i+1])
  sorted_dict = sort_dict(dictionary)
  return dict(sorted_dict)


######## causality ########
def add_new_key(dictionary, key):
  if key not in dictionary.keys():
    dictionary[key]=[]
  return 0

def add_new_element(dictionary, key, element):
  if element not in dictionary[key]:
    dictionary[key].append(element)
  return 0

def get_causality_and_parallel(direct_successors_dict):
  causality_dict = {}
  parallel_dict = {}
  for key in direct_successors_dict:
    successor_key = key
    successor_elements = direct_successors_dict[key]['successors']
    for element in successor_elements:
      reverse_consecution = is_reverse_consecution(direct_successors_dict, successor_key, element) #sprawdz czy jest relacja odwrotna
      if not reverse_consecution:
        add_new_key(causality_dict, successor_key)
        add_new_element(causality_dict, successor_key, element)
      else:
        add_new_key(parallel_dict, successor_key)
        add_new_element(parallel_dict, successor_key, element)
  return causality_dict, parallel_dict

def is_reverse_consecution(dictionary, old_key, old_element):
  if not is_a_key(dictionary, old_element): #check if element is a key in old dict
    return False
  else:
    elements_from_reverse = dictionary[old_element]['successors']
    if old_key in elements_from_reverse:
      return True
    else:
      return False

def is_a_key(dictionary, key):
  if key not in dictionary.keys():
    return False
  else:
    return True

def get_inv_causality(causality):
    inv_causality = dict()
    causality_val_len_1 = { key: next(iter(value))
                            for key, value in causality.items()
                            if len(value) == 1 }
    for k, v in causality_val_len_1.items():
        inv_causality.setdefault(v[0], set()).add(k)
    return inv_causality


######## counter for events ########
def get_events_counter(direct_successors_dict,log_matrix):
  events = list(direct_successors_dict.keys())
  events_counter = {}
  for e in events:
    counter = 0
    for log_array in log_matrix:
      counter += log_array.count(e)
    events_counter[e] = counter
  return events_counter



################### Getting additional relations ###################

######## significance dependency matrix ########
def get_frequency_matrix(direct_successors): #directly-follows frequency matrix
  events = [event for event in direct_successors]
  frequency_matrix = []
  for event in events:
    frequency_list = []
    for event1 in events:
      successors = direct_successors[event]['successors']
      if event1 in successors:
        idx = successors.index(event1)
        frequency_list.append(direct_successors[event]['counter'][idx])
      else:
        frequency_list.append('')
    frequency_matrix.append(frequency_list)
  return frequency_matrix

def get_significance_dependency_matrix(direct_successors):
  frequency_matrix = get_frequency_matrix(direct_successors)
  sig_dependency_matrix = copy.deepcopy(frequency_matrix)
  for i in range(0,len(frequency_matrix)):
    for j in range(0,len(frequency_matrix)):
      t1t2 = frequency_matrix[i][j]
      t2t1 = frequency_matrix[j][i]
      if not (t1t2 == '' and t2t1 == ''):
        if t1t2 != '':
          if t2t1 == '':
            t2t1 = 0
        else:
          if t2t1 != '':
            t1t2 = 0
        sig_dependency_matrix[i][j] = round((t1t2-t2t1)/(t1t2+t2t1+1),2)
  return sig_dependency_matrix


######## loops ########
def get_one_loop_matrix(direct_successors):
  frequency_matrix = get_frequency_matrix(direct_successors)
  loop_matrix = copy.deepcopy(frequency_matrix)
  for i in range(0,len(frequency_matrix)):
    for j in range(0,len(frequency_matrix)):
      if i == j:
        if frequency_matrix[i][j] != '':
          loop_matrix[i][j] = frequency_matrix[i][j]/(frequency_matrix[i][j]+1)
        else:
          loop_matrix[i][j] = 0
      else:
        loop_matrix[i][j] = ''
  return loop_matrix

def get_two_loop_frequency_matrix(in_log_matrix, direct_successors):
  events = [event for event in direct_successors]
  frequency_matrix = [[0] * len(events) for i in range(len(events))]
  for i in range(len(events)):
    for j in range(len(events)):
      for log in in_log_matrix:
        for k in range(len(log)-2):
          if log[k] == events[i] and log[k+1] == events[j] and log[k+2]==events[i]:
            frequency_matrix[i][j] += 1
  return frequency_matrix

def get_two_loop_matrix(in_log_matrix, direct_successors):
  frequency_matrix = get_two_loop_frequency_matrix(in_log_matrix, direct_successors)
  dependency_matrix = copy.deepcopy(frequency_matrix)
  for i in range(0,len(frequency_matrix)):
    for j in range(0,len(frequency_matrix)):
      t1t2 = frequency_matrix[i][j]
      t2t1 = frequency_matrix[j][i]
      if not (t1t2 == 0 and t2t1 == 0):
        dependency_matrix[i][j] = round((t1t2+t2t1)/(t1t2+t2t1+1),2)
  return dependency_matrix


######## indirect successors with counter ########
def get_indirect_successors(log_matrix):
    direct_successors_dict = get_direct_successors(log_matrix)
    events = list(direct_successors_dict.keys())
    dictionary = {}

    for i in range(len(events)):
        for j in range(i + 1, len(events)):
            for log_array in log_matrix:
                flag = True
                for k in range(len(log_array)):
                    if log_array[k] == events[i] and flag:
                        cnt_i = 1
                        for l in range(k + 1, len(log_array)):
                            if log_array[l] == events[i]:
                                cnt_i += 1
                            elif log_array[l] == events[j]:
                                key = events[i]
                                element = events[j]
                                if key not in dictionary.keys():
                                    dictionary[key] = {'successors': [], 'counter': []}
                                if element not in dictionary[key]['successors']:
                                    dictionary[key]['successors'].append(element)
                                    dictionary[key]['counter'].append(cnt_i)
                                else:
                                    id = dictionary[key]['successors'].index(element)
                                    dictionary[key]['counter'][id] += cnt_i
                                flag = False
                                break
    dictionary[events[-1]] = {'successors': [], 'counter': []}

    return dict(sorted(dictionary.items()))
