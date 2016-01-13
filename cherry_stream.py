import cherrypy
import os

ext_mapper={".mp4":"mp4"}
MOVIE_DIR = '/home/user/Videos'

def content(file_name, start_pos=0, chunck_size=280883):
    f = open(file_name ,'rb')  
    f.seek(start_pos)            
    byte = f.read(chunck_size)    
    yield byte        
    
class Root:    
    def index(self, **kwargs):

        file_name = kwargs.get('file_name', None)
        if not file_name:
            return ''
        
        file_name = os.path.join(MOVIE_DIR, file_name)
        file_extension = os.path.splitext(file_name)[1]
        file_size = os.path.getsize(file_name)
        
        cherrypy.response.headers['Content-Type'] = 'video/%s'%ext_mapper.get(file_extension, 'mp4')        
        cherrypy.response.status = '206'
        
        range = cherrypy.request.headers.get('Range')

        if range:
            start, end = tuple(range.replace('bytes=','').split('-'))
            try:
                start = int(start)
                end = int(end)
            except:
                pass
            
            if not end:
                end = file_size-1
                                   
            chunck_size = end - start + 1
            
            #cherrypy.response.headers['Transfer-Encoding'] = 'chunked'
            cherrypy.response.headers['Accept-Ranges'] = 'bytes'
            cherrypy.response.headers['Content-Range'] = 'bytes ' + str(start) + '-' + str(end) + '/%s'%(file_size)
            cherrypy.response.headers['Content-Length'] = chunck_size

            g = content(file_name=file_name, start_pos=start, chunck_size=chunck_size)            
            return g
        else:
            cherrypy.response.headers['Content-Length'] = file_size
            g = content(file_name=file_name)
            return g
        
    index.exposed = True
    index._cp_config = {'response.stream': True}

cherrypy.server.socket_host = '0.0.0.0'    
cherrypy.quickstart(Root())