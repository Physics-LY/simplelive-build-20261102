import ctypes,os,pathlib,sys,time,json
lib=pathlib.Path(sys.argv[1]).resolve();media=pathlib.Path(sys.argv[2]).resolve()
if os.name=='nt':os.add_dll_directory(str(lib.parent))
m=ctypes.CDLL(str(lib));m.mpv_create.restype=ctypes.c_void_p;m.mpv_initialize.argtypes=[ctypes.c_void_p];m.mpv_initialize.restype=ctypes.c_int;m.mpv_set_option_string.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_char_p];m.mpv_command.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_char_p)];m.mpv_get_property.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_int,ctypes.c_void_p];m.mpv_terminate_destroy.argtypes=[ctypes.c_void_p]
h=m.mpv_create();assert h,'mpv_create returned null'
try:
 for key,val in [('vo','null'),('ao','null'),('hwdec','no'),('terminal','yes'),('msg-level','all=warn'),('keep-open','yes')]:assert m.mpv_set_option_string(h,key.encode(),val.encode())>=0,key
 assert m.mpv_initialize(h)>=0,'mpv_initialize failed'
 args=(ctypes.c_char_p*4)(b'loadfile',str(media).encode('utf-8'),b'replace',None);assert m.mpv_command(h,args)>=0,'loadfile failed'
 start=time.monotonic();width=ctypes.c_int64();height=ctypes.c_int64();pos=ctypes.c_double()
 while time.monotonic()-start<30:
  a=m.mpv_get_property(h,b'video-params/w',4,ctypes.byref(width));b=m.mpv_get_property(h,b'video-params/h',4,ctypes.byref(height));c=m.mpv_get_property(h,b'time-pos',5,ctypes.byref(pos))
  if a>=0 and b>=0 and c>=0 and width.value>0 and height.value>0 and pos.value>=0.5:
   print(json.dumps({'result':'PASS','width':width.value,'height':height.value,'playback_seconds':pos.value,'file':media.name}));break
  time.sleep(.1)
 else:raise RuntimeError('Video decode/playback did not advance within 30 seconds')
finally:m.mpv_terminate_destroy(h)
