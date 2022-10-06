#!/usr/bin/python3

import meraki
import copy
import asyncio
import os
from time import *

from meraki import aio
import tqdm.asyncio
#import time
import get_keys as g
import datetime
import random

log_dir = os.path.join(os.getcwd(), "Logs/")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

ASYNC = True

ans = input("Do you want to use AsyncIO? (YES/no): ")
if "no" in ans.lower():
    ASYNC = False

def getDateIntervals(days = 31, slices = 2):
    results = []
    current_time = datetime.datetime.utcnow()
    print(f"Current time is {current_time}")
    start_time = current_time - datetime.timedelta(days)
    current_timestamp = current_time.timestamp()
    start_timestamp = start_time.timestamp()
    delta_time = current_timestamp - start_timestamp
    slice_interval = delta_time / (days * slices)
    last_used = start_timestamp
    all_times = []
    for day in range(1, (days * slices) + 1 ):
        t0 = last_used
        t1 = t0 + slice_interval
        last_used = t1
        start_date_slice = datetime.datetime.fromtimestamp(t0)
        end_date_slice = datetime.datetime.fromtimestamp(t1)
        #if end_date_slice > current_time:
        #    end_date_slice = current_time
        #    print(f"LAST ONE!!")
        if start_date_slice < end_date_slice:
            results.append([start_date_slice.isoformat(), end_date_slice.isoformat()])
    return results

async def getAPI(aio, org_id, start_date, end_date):
    print(f"Loading API queries for org[{org_id}] ")
    try:
        dataset =  await aio.organizations.getOrganizationApiRequests(org_id, perPage=1000, total_pages='all', t0=start_date, t1=end_date)
    except:
        print("Something went wrong here.....")
        return org_id, []
    return org_id, dataset

async def main():
    async with meraki.aio.AsyncDashboardAPI(
            api_key=g.get_api_key(),
            base_url="https://api.meraki.com/api/v1",
            output_log=True,
            log_file_prefix=os.path.basename(__file__)[:-3],
            log_path='Logs/',
            maximum_concurrent_requests=10,
            maximum_retries= 100,
            wait_on_rate_limit=True,
            print_console=False,
            
    ) as aiomeraki:
    

        orgs = await aiomeraki.organizations.getOrganizations()
        orgs_whitelist = [] 

        for o in orgs:
            if o['api']['enabled'] == True:
                orgs_whitelist.append(o['id'])
        print(orgs_whitelist)

        file_whitelist = 'org_whitelist.txt'
        orgs_wl = []
        if os.path.exists(file_whitelist):
            f = open(file_whitelist)
            wl_orgs = f.readlines()
            for o in wl_orgs:
                if len(o.strip()) > 0:
                    orgs_wl.append(o.strip())
        if len(orgs_wl) > 0:
            orgs_whitelist = orgs_wl
    
        date_ranges = getDateIntervals(31,2) #this returns a list of tuples [ []]

        for dr in date_ranges:
            if dr[0] > dr[1]:
                print(dr) #this shouldn't happen

        start_timer = time()

        master_list = {}
        actionList = []
        for date_range in date_ranges:
            for oid in orgs_whitelist:
                if ASYNC:
                    actionList.append(getAPI(aiomeraki,oid,date_range[0],date_range[1])) #THIS IS THE FAST ONE ... free for all
                else: 
                    actionList.append(await getAPI(aiomeraki,oid,date_range[0],date_range[1])) #THIS IS THE SLOW ONE...force sequencial execution of queries
        
        if not type(actionList[0]) == tuple: #if its an async future object
            for task in tqdm.tqdm(asyncio.as_completed(actionList),total = len(actionList), colour='blue'):
                oid, result = await task
                print(f"Organization[{oid}] returned {len(result)}")
                if not oid in master_list:
                    master_list[oid] = []
                master_list[oid] += result
        else: #just a regular list, not using async
            for task in actionList:
                oid, result = task
                print(f"Organization[{oid}] returned {len(result)}")
                if not oid in master_list:
                    master_list[oid] = []
                master_list[oid] += result
            
        end_timer = time()
        elapsedTime = round(end_timer-start_timer,2)
        allCount = 0
        for oid in master_list:
            print(f"Organizaiton[{oid}] total records [{len(master_list[oid])}]")
            allCount += len(master_list[oid])
        print(f"Total record count of {allCount}")
        print()
        print()
        print(f"Took a total of {elapsedTime} seconds")

    return master_list


  

if __name__ == '__main__':
    asyncio.run(main())
