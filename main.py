
#couldn't import openpyxl for some reason, this should fix that problem from now on. 
#add/remove required libraries as needed
import subprocess
import sys

# Ensure required libraries are installed
for lib in ['pandas', 'networkx', 'matplotlib', 'openpyxl', 'scipy']:
    try:
        __import__(lib)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

#=====================================
#Task 1: Tier counts and network edges
#=====================================

#numba 1: load supplier files, calculate unique counts
supplier1_df = pd.read_csv('Supplier1.csv')
supplier2_df = pd.read_csv('Supplier2.csv')
supplier3_df = pd.read_csv('Supplier3.csv')

#convert cols to sets. this'll let us find the unique suppliers
tier1_suppliers = set(supplier1_df['Tier 1 Supplier Name'].dropna().unique())
tier2_suppliers = set(supplier2_df['Tier 2 Supplier Name'].dropna().unique())
tier3_suppliers = set(supplier3_df['Tier 3 Supplier Name'].dropna().unique())

#load edges dataset and count the total shipment relationships
edges_df = pd.read_csv('Network_Edges.csv')
total_network_edges = len(edges_df)

#numba 2: load the customer file, caluclate the unique count
customers_df = pd.read_excel('Customers.xlsx')
tier1_customers = set(customers_df['Customer Name'].dropna().unique())

#display results
print("\n=== Task 1 ===")
print(f"Unique Tier 1 suppliers: {len(tier1_suppliers)}")
print(f"Unique Tier 2 suppliers: {len(tier2_suppliers)}")
print(f"Unique Tier 3 suppliers: {len(tier3_suppliers)}")
print(f"Total network edges: {total_network_edges}")
print(f"Unique Tier 1 customers: {len(tier1_customers)}")

#END TASK 1 lets goooooo

#=======================================
#Task 2: Construct and visualize network
#=======================================

#numba 3: construct graph from the edge list
G = nx.from_pandas_edgelist(
        edges_df,
        source = 'Source',
        target = 'Target',
        create_using = nx.DiGraph()
)

print("\n=== Task 2 ===")
print(f"Total nodes in constructed graph: {G.number_of_nodes()}")
print(f"Total edges in constructed graph: {G.number_of_edges()}")

#numba 4: visualize the network. use matplotlib library for this part
plt.figure(figsize = (12, 10))

#initialize the node_colors list. chatGPT was required for me to figure out I needed to do this. embarassing tbh
node_colors = []

#assign colors based on tier/role
for node in G.nodes():
    if node == 'CATL':
        node_colors.append('red') #central hub will be this color
    elif node in tier1_suppliers:
        node_colors.append('lightgreen') #tier 1 suppliers
    elif node in tier2_suppliers:
        node_colors.append('skyblue') #tier 2 suppliers
    elif node in tier3_suppliers:
        node_colors.append('gold') #tier 3 suppliers
    elif node in tier1_customers:
        node_colors.append('pink') #tier 1 customers
    else:
        node_colors.append('lightgray') #whatever else/undefined

#calculate positioning. spring layout gives us the cleanest structure in my humble opinion
pos = nx.spring_layout(G, seed = 42, k = 0.15)

#draw elements
nx.draw_networkx_nodes(G, pos, node_size = 30, node_color =  node_colors, alpha = 0.8)
nx.draw_networkx_edges(G, pos, edge_color = 'gray', arrows = True, arrowsize = 5, alpha = 0.2)

#highlight central CATL label for the node.
if 'CATL' in G:
    nx.draw_networkx_labels(G, pos, labels = {'CATL': 'CATL'}, font_size = 12, font_weight = 'bold', font_color = 'black')

plt.title("CATL Multi-Tier Supply Chain Network Diagram", fontsize = 14, fontweight = 'bold')
plt.axis('off')
plt.tight_layout()

#saves to file. not necessary right now, but be sure to UNCOMMENT IF NECESSARY::
#plt.savefig('network_diagram.png', dpi = 300, bbox_inches = 'tight')
#plt.show()

#END TASK 2 WHATTTT

#========================================================
#Task 3: we're gonna identify suppliers in multiple tiers
#========================================================

#numba 5: identify tghe combos of multi-tier suppliers/tiers

#set the intersections for two-tier combos. **Excludes combos in all three
t1_t2 = (tier1_suppliers & tier2_suppliers) - tier3_suppliers
t2_t3 = (tier2_suppliers & tier3_suppliers) - tier1_suppliers
t1_t3 = (tier1_suppliers & tier3_suppliers) - tier2_suppliers

#all three intersecting
t1_t2_t3 = tier1_suppliers & tier2_suppliers & tier3_suppliers

#total unique multi-tier suppliers
tot_multi_tier_suppliers = (tier1_suppliers & tier2_suppliers) | \
                        (tier2_suppliers & tier3_suppliers) | \
                        (tier1_suppliers & tier3_suppliers)

#display the counts for task 3
print("\n=== Task 3 ===")
print(f"Suppliers in tiers 1 and 2: {len(t1_t2)}")
print(f"Suppliers in tiers 2 and 3: {len(t2_t3)}")
print(f"Suppliers in tiers 1 and 3: {len(t1_t3)}")
print(f"Suppliers in all three tiers: {len(t1_t2_t3)}")
print(f"Total unique multi-tier suppliers: {len(tot_multi_tier_suppliers)}")

#numba 6: produce the table
multi_tier_list = []

for supplier in sorted(tot_multi_tier_suppliers):
    multi_tier_list.append({
        'Supplier Name': supplier,
        'Tier 1': 'Yes' if supplier in tier1_suppliers else 'No',
        'Tier 2': 'Yes' if supplier in tier2_suppliers else 'No',
        'Tier 3': 'Yes' if supplier in tier3_suppliers else 'No'
    })

#convert list to dataframe
multi_tier_df = pd.DataFrame(multi_tier_list)

#shift index -> instead of 0-9, displays as 1-10
multi_tier_df.index = range(1, len(multi_tier_df) + 1)

#export to csv
multi_tier_df.to_csv('multi_tier_suppliers.csv', index = False)

#how many rows?
row_count = 10

#output
print("\nMulti-Tier Supplier summary table (first " + str(row_count) + " rows):")
print(multi_tier_df.head(row_count))
print(f"\nSaved full table ({len(multi_tier_df)} rows) to multi_tier_suppliers.csv")

#END TASK 3 OH YEAH

#I think thats the end of the assignment?
