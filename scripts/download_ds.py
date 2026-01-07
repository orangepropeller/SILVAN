import os
import shutil
import urllib.request
import gzip
import tarfile
import zipfile
import pandas as pd

directed_graphs_links = [
"http://snap.stanford.edu/data/p2p-Gnutella31.txt.gz",
"http://snap.stanford.edu/data/cit-HepTh.txt.gz",
"http://snap.stanford.edu/data/soc-Epinions1.txt.gz",
"http://snap.stanford.edu/data/wiki-Vote.txt.gz",
"http://snap.stanford.edu/data/cit-HepPh.txt.gz",
"http://snap.stanford.edu/data/wiki-topcats.txt.gz",
"http://konect.cc/files/download.tsv.wikipedia_link_en.tar.bz2", # http://konect.cc/networks/wikipedia_link_en/
"http://snap.stanford.edu/data/email-EuAll.txt.gz", # http://snap.stanford.edu/data/email-EuAll.html
"http://snap.stanford.edu/data/wiki-Talk.txt.gz", # http://snap.stanford.edu/data/wiki-Talk.html
"http://snap.stanford.edu/data/soc-LiveJournal1.txt.gz", # http://snap.stanford.edu/data/soc-LiveJournal1.html
"http://snap.stanford.edu/data/soc-pokec-relationships.txt.gz" # http://snap.stanford.edu/data/soc-Pokec.html
]

undirected_graphs_links = [
"http://snap.stanford.edu/data/bigdata/communities/com-amazon.ungraph.txt.gz",
"http://snap.stanford.edu/data/email-Enron.txt.gz",
"http://snap.stanford.edu/data/ca-GrQc.txt.gz",
"http://snap.stanford.edu/data/bigdata/communities/com-youtube.ungraph.txt.gz",
"http://konect.cc/files/download.tsv.actor-collaboration.tar.bz2", # http://konect.cc/networks/actor-collaboration/
"http://snap.stanford.edu/data/bigdata/communities/com-dblp.ungraph.txt.gz", # http://snap.stanford.edu/data/com-DBLP.html
"http://snap.stanford.edu/data/ca-AstroPh.txt.gz" # http://snap.stanford.edu/data/ca-AstroPh.html
]

all_links = directed_graphs_links + undirected_graphs_links

# Determine paths relative to the script location
script_dir = os.path.dirname(os.path.abspath(__file__))
# Assuming script is in scripts/, put datasets in the parent directory
project_root = os.path.dirname(script_dir)
datasets_dir = os.path.join(project_root, "datasets")
graph_experiments_paths = os.path.join(script_dir, "graphs_experiments.csv")

if not os.path.exists(datasets_dir):
    os.makedirs(datasets_dir)

filepaths = []

with open(graph_experiments_paths, "w") as graphs_list_file:
    graphs_list_file.write("graph_name;directed\n")
    for link in all_links:
        filepath = link.rfind("/")
        filepath = link[filepath+1:]
        print(filepath)
        filepaths.append(filepath)
        
        name = filepath
        name = name.replace(".gz","")
        name = name.replace(".zip","")
        name = name.replace(".tar","")
        name = name.replace(".bz2","")
        name = name.replace("download.tsv.","")
        
        if ".txt" not in name:
            name = name + ".txt"
            
        if link in undirected_graphs_links:
            graphs_list_file.write(name+";U\n")
        else:
            graphs_list_file.write(name+";D\n")

print(f"\nDownloading datasets to {datasets_dir}...")

# Create a custom opener to avoid 403 Forbidden errors on some sites
opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib.request.install_opener(opener)

for link in all_links:
    filename = link.split("/")[-1]
    dest_path = os.path.join(datasets_dir, filename)
    
    if not os.path.exists(dest_path):
        print(f"Downloading {filename}...")
        try:
            urllib.request.urlretrieve(link, dest_path)
        except Exception as e:
            print(f"Failed to download {link}: {e}")
    else:
        print(f"{filename} already exists. Skipping.")

print("\nExtracting datasets...")
for filepath in filepaths:
    full_path = os.path.join(datasets_dir, filepath)
    
    if not os.path.exists(full_path):
        continue

    if ".zip" in filepath:
        print(f"Unzipping {filepath}...")
        try:
            with zipfile.ZipFile(full_path, 'r') as zip_ref:
                zip_ref.extractall(datasets_dir)
        except Exception as e:
            print(f"Error unzipping {filepath}: {e}")

    if ".gz" in filepath and ".tar" not in filepath:
        print(f"Decompressing {filepath}...")
        out_path = os.path.join(datasets_dir, filepath.replace(".gz", ""))
        try:
            with gzip.open(full_path, 'rb') as f_in:
                with open(out_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        except Exception as e:
            print(f"Error decompressing {filepath}: {e}")

    if ".tar.bz2" in filepath:
        print(f"Extracting {filepath}...")
        try:
            with tarfile.open(full_path, "r:bz2") as tar:
                tar.extractall(datasets_dir)
        except Exception as e:
             print(f"Error extracting {filepath}: {e}")

    if "download.tsv." in filepath:
        filepath_ = filepath.replace("download.tsv.","")
        filepath_ = filepath_.replace(".tar.bz2","")
        
        src_file = os.path.join(datasets_dir, filepath_, "out." + filepath_)
        dest_file = os.path.join(datasets_dir, filepath_ + ".txt")
        
        if os.path.exists(src_file):
            print(f"Copying {src_file} to {dest_file}")
            shutil.copy(src_file, dest_file)
        
print("\nVerifying graph files...")
try:
    graphs = pd.read_csv(graph_experiments_paths, sep=";")
    graphs_list = graphs["graph_name"].values
    for graph_filename in graphs_list:
        if not os.path.isfile(os.path.join(datasets_dir, graph_filename)):
            print("Graph file for ", graph_filename, " not found!")
    print("Verification complete.")
except Exception as e:
    print(f"Error verifying graphs: {e}")
