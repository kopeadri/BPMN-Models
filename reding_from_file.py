import os
import pandas as pd
from opyenxes.data_in.XUniversalParser import XUniversalParser


################### Reading data from file ###################

def get_log_matrix_from_file(file):
  name, extension = os.path.splitext(file)
  if extension == '.csv':
    return get_log_matrix_from_csv(file)
  elif extension == '.xes':
    return get_log_matrix_from_xes(file)
  else:
    print("Wrong type of file.")

def get_log_matrix_from_csv(file):
  df = pd.read_csv(file, delimiter=',')
  temp_log_matrix = []
  for i in range(df['Case ID'].min(),df['Case ID'].max()+1):
    temp_log_matrix.append(list(df.loc[df['Case ID'] == i]['Activity']))
  return temp_log_matrix

def get_log_matrix_from_xes(file):
  with open(file) as log_file:
    log = XUniversalParser().parse(log_file)[0]
    temp_log_matrix = []
    for trace in log:
      events_names = []
      for event in trace[0:]:
          event_name = event.get_attributes()['Activity'].get_value()
          events_names.append(event_name)
      temp_log_matrix.append(events_names)
  return temp_log_matrix