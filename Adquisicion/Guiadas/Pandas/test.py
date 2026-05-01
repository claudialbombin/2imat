import ssl
import certifi
import urllib.request
import pandas as pd

url = "https://raw.githubusercontent.com/justmarkham/DAT8/master/data/chipotle.tsv"

# Forzar a usar el bundle de certifi
ssl_context = ssl.create_default_context(cafile=certifi.where())

with urllib.request.urlopen(url, context=ssl_context) as f:
    data = pd.read_csv(f, sep="\t")

print(data.head())
