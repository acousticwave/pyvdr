import glob

# Name of a merged data
outfile = "vdr_merged.log"


# Merge files with names "./temp/VDR- ... log"
# 1) Start condition
path = "./temp/VDR-*"
# 2) End condition
end_condition = ".log"


# File list 
file_list = glob.glob(path)
file_list = [file for file in file_list if file.endswith(end_condition)]


# Sort the files in "file_list"
file_list = sorted(file_list)


print("Files to be merged:", file_list)


# Merge the files in the "file_list"
with open(outfile, "wb") as outfile:
    for f in file_list:
        with open(f, "rb") as infile:
            outfile.write(infile.read())