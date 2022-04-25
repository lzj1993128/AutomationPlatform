import os

cur_path = os.path.dirname(os.path.realpath(__file__))
excel_path = os.path.join(cur_path, 'excel')
if not os.path.exists(excel_path): os.mkdir(excel_path)