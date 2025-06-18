import requests
import argparse
from ds_store import DSStore
import urllib3
import base64
from datetime import datetime
import os
import shutil
import fnmatch

urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

found_urls = []
base_url = ""

DS_Store_Entries = []


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
        

def scan(url, download, output_path, base_url):
    try:
        url_b64 = base64.b64encode(url.encode()).decode()
        
        if not os.path.exists(output_path + "/DS_Store_Files"):
            os.makedirs(output_path + "/DS_Store_Files", exist_ok=True)
            
        print("Trying to download " + url + "/.DS_Store")
        r = requests.get(url + "/.DS_Store", verify=False, stream=True)
        r.raw.decode_content = True
        
        if download:
            output_folder = output_path + url.replace(base_url, "").replace("/.DS_Store", "")            
            os.makedirs(output_folder, exist_ok=True)

        if r.status_code == 200:
            with open(output_path + "/" + url_b64 + "_DS_Store", "wb") as f:
                for chunk in r.iter_content(chunk_size=1024):
                    f.write(chunk)
            with DSStore.open(output_path + "/" + url_b64 + "_DS_Store", "r") as d:
                # If it's a valid .DS_Store file we want to keep it separate
                shutil.copyfile(output_path + "/" + url_b64 + "_DS_Store", output_path + "/DS_Store_Files/" + url_b64 + "_DS_Store")
                for entry in d:
                    if entry.code.decode("utf-8") == "Iloc":
                        print("Found possible file or folder: " + entry.filename)
                        found_urls.append(url + "/" + entry.filename)
                        
                        if download:
                            try:
                               # Download the possible file
                               r_file = requests.get(url + "/" + entry.filename, verify=False, stream=True)
                               r_file.raw.decode_content = True
                               if r_file.status_code==200:
                                   content_length = r_file.headers.get('Content-Length')
                                   if content_length is not None:
                                       with open(output_folder + "/" + entry.filename, "wb") as f:
                                           for chunk in r_file.iter_content(chunk_size=1024):
                                               f.write(chunk)
                                           print("Downloaded file " + entry.filename + " to folder " + output_folder)
                            except:
                               print("Couldn't download!")
                        scan(url + "/" + entry.filename, download, output_path, base_url)
                        
        else:
            print("Got unexpected HTTP code " + str(r.status_code))
            
        
    except Exception as ex:
        print("Error while parsing DS files: " + str(ex) + " (Possibly deepest path reached?)")


def main():
    parser = argparse.ArgumentParser(description="Provide a URL as an argument.")
    parser.add_argument("--url", help="The URL to process", required=True)
    parser.add_argument("--download",  type=str2bool, required=True, help="Download found files")

    args = parser.parse_args()
    
    output_path = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.download:
        print("Creating output folder '" + output_path + "'")
        os.makedirs(output_path, exist_ok=True)
        
    scan(args.url, args.download, output_path, args.url)
    
    # Cleaning up
    pattern = "_DS_Store"
    for file_name in os.listdir(output_path):
        if file_name.endswith(pattern):
            file_path = os.path.join(output_path, file_name)
            os.remove(file_path)        

    print("Extracted data:\n")
    for url in found_urls:
        print(url)
        
    if args.download:
        print("All files have been written to " + output_path)

if __name__ == "__main__":
    main()

