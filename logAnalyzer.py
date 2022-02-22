#!/usr/bin/ipython3

from cmath import log
import copy
import os
from time import *
from bcolors import bcolors as bc

import datetime

local_files = os.listdir('.')
log_files = []
for f in local_files:
    index = len(f)-4
    tail = f[index:]
    if '.log' == tail:
        #print(f)
        log_files.append(f)


logs = {}
for f in log_files:
    file = open(f)
    tmp_lines = file.readlines()
    lines = []
    for l in tmp_lines:
        if not "DEBUG" in l and ("GET" in l or "POST" in l):
            lines.append(l)
    logs[f] = lines

for l in logs:
    if len(logs[l]) == 0:
        continue
    start = logs[l][0].split(' ')
    start_time = start[0] + ' ' + start[1]
    start_dt = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    end = logs[l][len(logs[l])-1].split(' ')
    end_time = end[0] + ' ' + end[1]
    end_dt = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    delta = end_dt - start_dt
    totalSeconds = delta.total_seconds()
    if totalSeconds > 0:
        calls_per_second = round(len(logs[l]) / totalSeconds,2)
    else: calls_per_second = 0
    print(f"{bc.FAIL}{l}{bc.OKGREEN} has {bc.WARNING}{len(logs[l])}{bc.OKGREEN} api calls, or {bc.WARNING}{calls_per_second}{bc.OKGREEN} calls per second over {bc.WARNING}{totalSeconds}{bc.OKGREEN} seconds{bc.ENDC}")
    print()
    
