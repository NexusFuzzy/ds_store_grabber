DS_Store Mapper is a Python-based reconnaissance tool designed to recursively scan web servers for exposed .DS_Store files. These files, often unintentionally left behind on macOS-based deployments, can leak sensitive information about the directory structure, including hidden or deleted files.

By parsing .DS_Store files discovered on a web server, the tool can reconstruct directory listings, discover hidden or unlinked files, and recursively expand its scan to subdirectories—allowing ethical hackers and security researchers to map the internal structure of a target web server.
