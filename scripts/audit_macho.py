from pathlib import Path
import struct,json,sys
CPU={0x01000007:'x86_64',0x0100000c:'arm64',7:'i386',12:'arm'}
def ver(v):return '.'.join(str(x) for x in [v>>16,(v>>8)&255,v&255])
def parse(data,offset=0):
 magic=data[offset:offset+4]
 if magic in (b'\xca\xfe\xba\xbe',b'\xca\xfe\xba\xbf'):
  n=struct.unpack_from('>I',data,offset+4)[0];result=[]
  for i in range(n):
   fmt='>IIQQII' if magic.endswith(b'\xbf') else '>IIIII';size=struct.calcsize(fmt);a=struct.unpack_from(fmt,data,offset+8+i*size);result+=parse(data,offset+a[2])
  return result
 if magic not in (b'\xcf\xfa\xed\xfe',b'\xce\xfa\xed\xfe',b'\xfe\xed\xfa\xcf',b'\xfe\xed\xfa\xce'):return []
 endian='<' if magic[0] in (0xcf,0xce) else '>';is64=magic in (b'\xcf\xfa\xed\xfe',b'\xfe\xed\xfa\xcf');cpu,sub,filetype,ncmds=struct.unpack_from(endian+'IIII',data,offset+4);p=offset+(32 if is64 else 28);minimum=None;sdk=None;libraries=[]
 for i in range(ncmds):
  cmd,size=struct.unpack_from(endian+'II',data,p)
  if cmd==0x32:
   platform,mv,sv=struct.unpack_from(endian+'III',data,p+8);minimum=ver(mv);sdk=ver(sv)
  elif cmd==0x24:mv,sv=struct.unpack_from(endian+'II',data,p+8);minimum=ver(mv);sdk=ver(sv)
  elif cmd in (0xc,0x80000018,0x8000001f,0x80000023):
   nameoffset=struct.unpack_from(endian+'I',data,p+8)[0];libraries.append(data[p+nameoffset:p+size].split(b'\0')[0].decode('utf-8',errors='replace'))
  if size<8:break
  p+=size
 return [{'arch':CPU.get(cpu,hex(cpu)),'minimum_macos':minimum,'sdk':sdk,'libraries':libraries}]
def scan(root):
 results=[]
 for p in Path(root).rglob('*'):
  if p.is_symlink() or not p.is_file():continue
  try:
   with p.open('rb') as f:head=f.read(4)
   if head not in (b'\xca\xfe\xba\xbe',b'\xca\xfe\xba\xbf',b'\xcf\xfa\xed\xfe',b'\xce\xfa\xed\xfe',b'\xfe\xed\xfa\xcf',b'\xfe\xed\xfa\xce'):continue
   slices=parse(p.read_bytes());results.append({'path':str(p.relative_to(root)),'slices':slices})
  except Exception as e:results.append({'path':str(p),'error':str(e)})
 return results
if __name__=='__main__':
 root=sys.argv[1];results=scan(root);print(json.dumps(results,ensure_ascii=False,indent=2))
 if '--require-big-sur-intel' in sys.argv:
  errors=[]
  for r in results:
   slices=r.get('slices',[])
   if [s['arch'] for s in slices]!=['x86_64']:errors.append(r['path']+': must contain x86_64 only')
   for s in slices:
    v=s['minimum_macos']
    if not v or tuple(map(int,v.split('.')))>(11,0,0):errors.append(r['path']+': minimum '+str(v))
  if not results:errors.append('No Mach-O binaries found')
  if errors:print('\n'.join(errors),file=sys.stderr);sys.exit(1)
