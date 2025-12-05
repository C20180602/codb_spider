import json
import os

species_name = "7120"
os.chdir(species_name)
with open("pid_list.json","r") as f:
    pid_list = json.load(f)
with open("ppi_list.json","r") as f:
    ppi_list = json.load(f)

pid_set = set(pid_list)
pid_with_ppi = set()
for pids in ppi_list:
    pid1 = pids[0]
    pid2 = pids[1]
    pid_with_ppi.add(pid1)
    pid_with_ppi.add(pid2)

print("Protein without ppi",len(pid_set-pid_with_ppi))