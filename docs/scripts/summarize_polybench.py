# -*- coding: utf-8 -*-

# Copyright (c) 2022 Synodic Month, Juni May
# yaTuner is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#          http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

# This script generate basic latex table for polybench result
# and further modification might be needed.

import logging
import pathlib
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from rich.logging import RichHandler

logging.basicConfig(
    format='[ %(name)s ] %(message)s',
    handlers=[RichHandler(level=logging.DEBUG, markup=True, show_path=False)])

logger = logging.getLogger('summary')
logger.setLevel(logging.DEBUG)

polybench_workspace = 'examples/polybench/workspace/'
db_dir_list = []
case_name_list = []

for db_dir in pathlib.Path(polybench_workspace).rglob('*.db'):
    db_dir_list.append(str(db_dir))
    case_name = str(db_dir).rsplit('/', 1)[1].split('.')[0]
    case_name_list.append(case_name)

logger.debug(db_dir_list)

is_first = True

res_dict = {}

headers = pd.read_csv(db_dir_list[0] + '/result.csv').columns.tolist()
headers.append(f'\Delta_{{HypoT}}')
headers.append(f'\Delta_{{LinUCB}}')

for i in range(len(db_dir_list)):
    pd_data = pd.read_csv(db_dir_list[i] + '/result.csv')
    res_list = pd_data.mean().to_list()
    res_list.append(
        f'{((res_list[1] - res_list[4]) / res_list[1] * 100):.2f}\\%')
    res_list.append(
        f'{((res_list[1] - res_list[5]) / res_list[1] * 100):.2f}\\%')
    res_dict[case_name_list[i]] = res_list

res_pd_data = pd.DataFrame(res_dict, index=headers)

table = f"""% -*- coding: utf-8 -*-
\\documentclass[landscape]{{report}}
\\usepackage[left=3.17cm, right=3.17cm, top=2.74cm, bottom=2.74cm]{{geometry}}
\\usepackage{{amsmath}}
\\usepackage{{booktabs}}
\\usepackage{{longtable}}
\\usepackage{{xcolor}}
"""

table += f'\\begin{{document}}\n\\begin{{longtable}}{{rrrrrrrr}}\n\\toprule\n'
result = res_pd_data.to_dict()

logger.debug(headers)

table += 'Case Name'

for header in headers:
    if header == 'Ofast':
        continue
    if header == 'Optimizers':
        table += f'\t& HypoT'
    elif header == 'parameters':
        table += f'\t& LinUCB'
    else:
        table += f'\t& {header}'

table += ' \\\\\n\\midrule\n'

for case_name in result:
    table += f'{case_name}'
    best_level = None
    best_res = None
    for level in result[case_name]:
        if 'Delta' in level:
            continue

        if level == 'Ofast':
            continue

        if best_level is None:
            best_level = level
            best_res = result[case_name][level]

        else:
            if result[case_name][level] < best_res:
                best_level = level
                best_res = result[case_name][level]

    result[case_name][
        best_level] = f'\\textcolor{{red}}{{\\textbf{{{result[case_name][best_level]/1000:.2f}}}}}'
    compare_level = 'O2'
    result[case_name][
        compare_level] = f'\\textcolor{{blue}}{{\\textbf{{{result[case_name][compare_level]/1000:.2f}}}}}'

    for level in result[case_name]:
        if level == 'Ofast':
            continue
        if 'Delta' in level or level in [best_level, compare_level]:
            table += f'\t& {result[case_name][level]}'
        else:
            table += f'\t& {result[case_name][level]/1000:.2f}'

    table += ' \\\\\n'

table += f'\\bottomrule\n\\end{{longtable}}\n\\end{{document}}'

with open('docs/polybench_summary.tex', 'w', encoding='utf-8') as file:
    file.write(table)

df = res_pd_data
df = df.drop([f'\Delta_{{HypoT}}', f'\Delta_{{LinUCB}}', 'Ofast'])
df = df.rename({'Optimizers': 'HypoT', 'parameters': 'LinUCB'})
print(df)
df_norm = df.apply(lambda x: x / np.max(x))
print(df_norm)
plt.clf()
fig = df_norm.T[0:9].plot.bar(figsize=(10,5), rot=1,
                               width=0.7,
                               color={
                                   'O1': 'blue',
                                   'O2': 'dodgerblue',
                                   'O3': 'royalblue',
                                   'HypoT': 'red',
                                   'LinUCB': 'coral'
                               })
plt.savefig('docs/polybench1.png', pad_inches=0, bbox_inches='tight')
plt.clf()
fig = df_norm.T[10:19].plot.bar(figsize=(10,5), rot=1,
                                 width=0.7,
                                 color={
                                     'O1': 'blue',
                                     'O2': 'dodgerblue',
                                     'O3': 'royalblue',
                                     'HypoT': 'red',
                                     'LinUCB': 'coral'
                                 })
plt.savefig('docs/polybench2.png', pad_inches=0, bbox_inches='tight')
plt.clf()
fig = df_norm.T[20:29].plot.bar(figsize=(10,5), rot=1,
                                 width=0.7,
                                 color={
                                     'O1': 'blue',
                                     'O2': 'dodgerblue',
                                     'O3': 'royalblue',
                                     'HypoT': 'red',
                                     'LinUCB': 'coral'
                                 })
plt.savefig('docs/polybench3.png', pad_inches=0, bbox_inches='tight')
