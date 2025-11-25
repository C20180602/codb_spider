import os
import json
import numpy as np
import pandas as pd

species_name = "29413"
os.chdir(species_name)

# 正常情况只需要整理CyanoOmicsDB数据就可以了
pid_list = set()
pg_dict = {}
pgo_dict= {}
for file in os.listdir("codb_data"):
    if file.endswith(".txt"):
        kgid = file.split('_data')[0]
        with open(f"codb_data/{file}", "r") as f:
            gids = f.readline().strip()
            pids = f.readline().strip()
            go_ids = f.readline().strip()
            if pids != "." and len(pids)<=14:
                for pid in pids.split(" "):
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
# df = pd.read_excel('Protein_information_table.xlsx')
# pid_column = df.iloc[:, 0].tolist()
# gid_column = df.iloc[:, 3].tolist()
# sp_column = df.iloc[:, 4].tolist()
# for pid,gids,sp in zip(pid_column,gid_column,sp_column):
#     if sp == "Nostoc sp. (strain PCC 7120 / SAG 25.82 / UTEX 2576)":
#         if pid not in pid_list:
#             pid_list.add(pid)
#             pg_dict[pid] = set()
#             pgo_dict[pid] = set()
#         if isinstance(gids,float) and np.isnan(gids):
#             continue
#         for gid in gids.split(' '):
#             if gid != "":
#                 pg_dict[pid].add(gid)
# with open("cmdb_go.tsv","r") as f:
#     line = f.readline()
#     line = f.readline()
#     while line:
#         pid,_,go_ids = line.split("\t")
#         # 这里面数据有些是其他物种的，只筛选出已经在并集中的蛋白质
#         if pid not in pid_list:
#             line = f.readline()
#             continue
#         if go_ids.strip() != "":
#             for gid in go_ids.strip().split("; "):
#                 pgo_dict[pid].add(gid)
#         line = f.readline()
                
with open("pid_list.json", 'w') as f:
    json.dump(list(pid_list), f, indent=4)
with open("pg_dict.json", 'w') as f:
    json.dump({k:list(v) for k,v in pg_dict.items()}, f, indent=4)
with open("pgo_dict.json", 'w') as f:
    json.dump({k:list(v) for k,v in pgo_dict.items()}, f, indent=4)

# PPI数据整理
gid2pid_map = {}
for pid,gids in pg_dict.items():
    for gid in gids:
        if gid not in gid2pid_map:
            gid2pid_map[gid]=[]
        gid2pid_map[gid].append(pid)
stid2pid_map = {}
with open("string_protein.txt", "r") as f:
    line = f.readline()
    line = f.readline()
    while line:
        stid = line.split("\t")[0]
        gid = line.split("\t")[1]
        if len(gid) != 7:
            descs = line.split("\t")[3]
            for desc in descs.split("; "):
                if desc.startswith("ORF_ID:"):
                    gid = desc.split(":")[1]
                    break
            if len(gid) != 7:
                gid = gid.split("-")[0]
        if gid in gid2pid_map:
            stid2pid_map[stid] = gid2pid_map[gid][0]
        line = f.readline()

ppi_list = set()
with open("string_ppi.txt", "r") as f:
    line = f.readline()
    line = f.readline()
    while line:
        stid1 = line.split(" ")[0]
        stid2 = line.split(" ")[1]
        score = int(line.split(" ")[2])
        if stid1 in stid2pid_map and stid2 in stid2pid_map and score >= 600:
            ppi_list.add((stid2pid_map[stid1], stid2pid_map[stid2]))
        line = f.readline()
        
# df = pd.read_excel('PPI_information_table.xlsx')
# pid1_list = df.iloc[:, 0].tolist()
# pid2_list = df.iloc[:, 1].tolist()
# sp_column = df.iloc[:, 6].tolist()
# for pid1, pid2, sp in zip(pid1_list, pid2_list, sp_column):
#     if sp == "Nostoc sp. (strain PCC 7120 / SAG 25.82 / UTEX 2576)":
#         if pid1 in pid_list and pid2 in pid_list:
#             ppi_list.add((pid1,pid2))

with open("ppi_list.json", "w") as f:
    json.dump(list(ppi_list), f, indent=4)