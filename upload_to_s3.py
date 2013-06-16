from boto.s3.connection import S3Connection
from boto.s3.key import Key
import json
import os
#~/.ec2/s3_credentials.json is a file containing {"AWS_ACCESS_KEY_ID":"AWS_SECRET_ACCESS_KEY"}
secret_key = json.loads(open(os.path.expanduser("~/.ec2/s3_credentials.json")).read())

conn = S3Connection(*secret_key.items()[0])
bucket = conn.get_bucket("citibikedata-www")
# In [4]: ab = os.walk('site_root')

# In [5]: bc = ab.next()

# In [6]: bc
# Out[6]: ('site_root', ['plots', 'stations'], ['index.html'])

# In [7]: 


walk_obj = os.walk('site_root')
for dir_path, unused, filenames in walk_obj:
    for fname in filenames:
        full_path = os.path.join(dir_path, fname)
        k = Key(bucket)
        k.key = full_path[10:]  #strip off the site_root/
        print full_path
        k.set_contents_from_filename(full_path)
        k.set_acl('public-read')
