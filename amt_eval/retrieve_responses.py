'''Processes the results from all of the HITs that have been run so far.'''

import xmltodict
import argparse
import re
import codecs
import pickle
import os
import utils

if not 'DEBUG' in vars() and not 'DEBUG' in globals():
  DEBUG = False

parser = argparse.ArgumentParser(description='Processes the AMT HIT results for all of the provided HIT ids.')
parser.add_argument('-d', '--hit_list_path',
                    help='Path to a .txt file with one HIT ID per line',
                    required=True)
parser.add_argument('-b', '--sandbox',
                    default=False, action='store_true',
                    help='Set to true to run in the sandbox.')
parser.add_argument('-p', '--pay',
                    default=False, action='store_true',
                    help='Set to true to pay the workers.')
                    
args = parser.parse_args()

if __name__ == '__main__':
  mturk = utils.create_mturk_client(args.sandbox)
  worker_results_list = []

  print('Reading HIT ids from: ' + args.hit_list_path)
  if DEBUG:
    import pdb; pdb.set_trace()
  with open(args.hit_list_path, 'r') as f_in:
    for hit_id in f_in:
      hit_id = hit_id.strip()
      print('Processing: ' + hit_id)

      try:
        worker_results = mturk.list_assignments_for_hit(
            HITId=hit_id, AssignmentStatuses=['Submitted', 'Approved'])
      except Error as e:
        print('Could not find results for HIT: ' + hit_id)
        continue
      for assignment in worker_results['Assignments']:
        assignment_id = assignment['AssignmentId']
        if args.pay == True:
          if assignment['AssignmentStatus'] == 'Submitted':
            print('Approving Assignment {}'.format(assignment_id))
            mturk.approve_assignment(
              AssignmentId=assignment_id,
              RequesterFeedback='good',
              OverrideRejection=False,
            )


      worker_results_list.append(worker_results)

  out_file_name = os.path.join(os.path.dirname(args.hit_list_path), 'amt_hit_responses.pkl') 
  pickle.dump(worker_results_list, open(out_file_name, "wb"))
