import os
import json
import numpy as np
import pandas as pd

# 正常情况只需要整理CyanoOmicsDB数据就可以了
kg2pid_map = {}
pid_list = set()
pg_dict = {}
pgo_dict= {}
for file in os.listdir("codb_data"):
    if file.endswith(".txt"):
        kgid = file.split('_')[0]
        with open(f"codb_data/{file}", "r") as f:
            gids = f.readline().strip()
            pids = f.readline().strip()
            go_ids = f.readline().strip()
            if pids != "." and len(pids)<=14:
                for pid in pids.split(" "):
                    # 为避免后续处理过于复杂，这里只取一个pid作为kgid的对应值
                    kg2pid_map[kgid] = pid
                    if pid not in pid_list:
                        pid_list.add(pid)
                        pg_dict[pid] = set()
                        pgo_dict[pid] = set()
                    pg_dict[pid].add(kgid)
                    if gids != ".":
                        for gid in gids.split(";"):
                            pg_dict[pid].add(gid)
                    if go_ids != ".":
                        for go_id in go_ids.split("  "):
                            if len(go_id) % 7 == 0:
                                for i in range(len(go_id)//7):
                                    pgo_dict[pid].add("GO:"+go_id[0+i*7:7+i*7])
                                    
# 这里合并了uniprot数据库的数据，格式为蛋白质ID、基因编号、GO标签
with open("uni_gid_go.tsv","r") as f:
    line = f.readline()
    line = f.readline()
    while line:
        pid,gids,go_ids = line.split("\t")
        if pid not in pid_list:
            pid_list.add(pid)
            pg_dict[pid] = set()
            pgo_dict[pid] = set()
        if gids != "":
            for gid in gids.split(" "):
                pg_dict[pid].add(gid)
        if go_ids.strip() != "":
            for gid in go_ids.strip().split("; "):
                pgo_dict[pid].add(gid)
        line = f.readline()
                
# 合并CMDB数据
df = pd.read_excel('Protein_information_table.xlsx')
pid_column = df.iloc[:, 0].tolist()
gid_column = df.iloc[:, 3].tolist()
sp_column = df.iloc[:, 4].tolist()
for pid,gids,sp in zip(pid_column,gid_column,sp_column):
    if sp == "Nostoc sp. (strain PCC 7120 / SAG 25.82 / UTEX 2576)":
        if pid not in pid_list:
            pid_list.add(pid)
            pg_dict[pid] = set()
            pgo_dict[pid] = set()
        if isinstance(gids,float) and np.isnan(gids):
            continue
        for gid in gids.split(' '):
            if gid != "":
                pg_dict[pid].add(gid)
with open("cmdb_go.tsv","r") as f:
    line = f.readline()
    line = f.readline()
    while line:
        pid,_,go_ids = line.split("\t")
        # 这里面数据有些是其他物种的，只筛选出已经在并集中的蛋白质
        if pid not in pid_list:
            line = f.readline()
            continue
        if go_ids.strip() != "":
            for gid in go_ids.strip().split("; "):
                pgo_dict[pid].add(gid)
        line = f.readline()
                
with open("pid_list.json", 'w') as f:
    json.dump(list(pid_list), f, indent=4)
with open("pg_dict.json", 'w') as f:
    json.dump({k:list(v) for k,v in pg_dict.items()}, f, indent=4)
with open("pgo_dict.json", 'w') as f:
    json.dump({k:list(v) for k,v in pgo_dict.items()}, f, indent=4)
    
# PPI数据整理
