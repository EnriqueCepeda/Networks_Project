import struct
import sys
archivo=str.encode(sys.argv[1])
empaquetado=struct.pack(f"=H{len(sys.argv[1])}sB{len('netascii')}sB",1,archivo,0,b'netascii',0)
print(empaquetado)
codigo=struct.unpack(f"=H{len(empaquetado)-2}s",empaquetado)
print(codigo)
unpacked=struct.unpack(f"={len(codigo[1])-10}sB{len('netascii')}sB",codigo[1])
print(unpacked)