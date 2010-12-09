from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class Image(db.Model): 
    blob_key = db.StringProperty()
    
class MainPage(webapp.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload')
        self.response.out.write("""<html><head><title>High Performance Image Tester</title></head>""");
        self.response.out.write("""<body>""");
        self.response.out.write("""
                <form action="%s" enctype="multipart/form-data" method="post">
                <div><label>ISBN:</label></div>
                <div><input type="text" name="isbn"/></div>
                <div><label>Image:</label></div>
                <div><input type="file" name="file"/></div>
                <div><input type="submit" value="Upload"></div>
                </form>
            </body>
            </html>""" % upload_url)

class UploadURLHandler(webapp.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload')
        self.response.out.write("""%s""" % upload_url)
		
class UploadURLNewHandler(webapp.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/uploadnew')
        self.response.out.write("""%s""" % upload_url)
 
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        isbn = self.request.get("isbn")
        image = Image(blob_key=str(blob_info.key()),key_name=isbn)
        image.put()
        self.redirect('/serve/%s' % blob_info.key())
		
class UploadNewHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        import logging
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        isbn = self.request.get("isbn")
        logging.info("isbn" + isbn)
        image = Image(blob_key=str(blob_info.key()),key_name=isbn)
        image.put()
        #self.redirect('/serve/%s' % blob_info.key())
#        self.response.set_status(302)
        return self.redirect(('http://test.audiogo.co.uk/view/%s' % isbn),permanent=True)
        
class ListHandler(webapp.RequestHandler):
    def get(self):
        imagelist = blobstore.BlobInfo.all()
        if imagelist:
            self.response.out.write("<html><body><ul>")
            for image in imagelist:
                self.response.out.write("<li>"+image.filename+" - ["+ str(image.key()) +"]</li>")
            self.response.out.write("</ul></body></html>")
        else:
            self.response.out.write("NONE FOUND")
        
class RemovalHandler(webapp.RequestHandler):
    def get(self,resource):
        image = Image.get_by_key_name(resource)
        
        if image:
            if image.blob_key:
                image_blob = blobstore.BlobInfo.get(image.blob_key)
                image_blob.delete()
                image.delete()
                self.response.out.write("REMOVED - "+resource)

class ServeHandler(webapp.RequestHandler):
    def get(self,resource):
        self.response.out.write("%s %s %s" % (images.get_serving_url(resource, 32),
        images.get_serving_url(resource, 150),
        images.get_serving_url(resource, 80)))
        
class ThumbHandler(webapp.RequestHandler):
    def get(self,resource):
        image = Image.get_by_key_name(resource)
        if image:
            if image.blob_key:
                self.response.out.write("%s" % (images.get_serving_url(image.blob_key, 144)))
 
class LargeHandler(webapp.RequestHandler):
    def get(self,resource):
        image = Image.get_by_key_name(resource)
        if image:
            if image.blob_key:
                self.response.out.write("%s" % (images.get_serving_url(image.blob_key, 512)))

class ImageHandler(webapp.RequestHandler):
    def get(self,resource):
        image = Image.get_by_key_name(resource)
        size = self.request.get('size')
        if image:
            if image.blob_key:
                self.response.out.write("%s" % (images.get_serving_url(image.blob_key, int(size))))

application = webapp.WSGIApplication(
    [('/', MainPage),
    ('/upload', UploadHandler),
	('/get_upload_url_new', UploadURLNewHandler),
    ('/get_upload_url', UploadURLHandler),
    ('/list', ListHandler),
    ('/remove/([^/]+)?', RemovalHandler),
    ('/thumb/([^/]+)?', ThumbHandler),
    ('/large/([^/]+)?', LargeHandler),
    ('/image/([^/]+)?', ImageHandler),
    ('/serve/([^/]+)?', ServeHandler),
	('/uploadnew', UploadNewHandler)],
    debug=True)
 
def main():
    run_wsgi_app(application)
 
if __name__ == "__main__":
    main()
