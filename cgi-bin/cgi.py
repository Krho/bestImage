/mnt/nfs/labstore-secondary-tools-project/best-image/python/bin/python
import site
site.addsitedir("/data/project/best-image/python/lib/python2.7/site-packages")

from wsgiref.handlers import CGIHandler
from app import app
import os

os.environ['SCRIPT_NAME'] = '/best-image'
CGIHandler().run(app)
