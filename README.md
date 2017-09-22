# bestImage
Retrieves the "best" image of a given Commons category

## Run with uWSGI
After installing `uWSGI` you can run the server this way:

```
uwsgi --http 0.0.0.0:4242 -p 5 --wsgi-file view_image.py --callable app --master
```
