import struct
import sys
archivo=f'{sys.argv[1]}'.encode()
empaquetado=struct.pack(f"=H{len(sys.argv[1])}sB{len('neta scii')}sB",1,archivo,0,b'neta scii',0)
print(empaquetado)
codigo=struct.unpack(f"=H{len(empaquetado)-2}s",empaquetado)
print(codigo)
unpacked=struct.unpack(f"={len(sys.argv[1])}sB{len('neta scii')}sB",codigo[1])
print(unpacked)