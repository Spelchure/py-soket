# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 08:16:48 2020

@author: ALPEREN
"""

import socket
from threading import Thread
import sys
import re
from optparse import OptionParser


COM_ENCODING = 'utf-8' # mesajların encode biçimi utf 1 byte
ADRES="127.0.0.1" # server için ip adresi
KAPI=8888 # port
KOMUT_STR="Mesaj(cikis icin :kapat) >> " # komut


class Baglanti: 
    """Ana bağlantı sınıfı"""
    
    def __init__(self, socket, commsize = 1024):
        
        self.sock = socket
        self.size = commsize
          
    def read_string(self):
        """String oku"""
        try:
            data = self.sock.recv(self.size)
            if data:
                return data.decode(COM_ENCODING)
        except OSError:
            pass
        return None
           
    def write_string(self, msg):
        """String gönder"""
        try:
            self.sock.sendall(bytes(msg, COM_ENCODING))
        except (ConnectionAbortedError,ConnectionResetError):
            print("Hata: Baglanti sonlandirildi.\n")
            raise
       
    def dinleyici(self):
        """İstemciden string oku"""
        while True:
            s = self.read_string()
            if s:
                print("\nKarsi: " + s)
                
    def soket_degistir(self, soket):
        self.sock = soket
        
class Client(Baglanti):
    """İstemci sınıfı"""
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host,port))
        super().__init__(self.sock)
        
    def __del__(self):
        self.sock.close()
        
        
class Server(Baglanti):
    """Sunucu sınıfı"""
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Kullanılan adresi yeniden kullanmamızı sağlıyor:
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host,port))
        super().__init__(self.sock)
        
    def server_loop(self):
        self.sock.listen(1)
        soket, adres = self.sock.accept()
        print("{} adresi baglandi.".format(adres))
        self.soket_degistir(soket)
        
        
    def __del__(self):
        self.sock.close()

def main():
    parser = OptionParser(usage="Kullanim: %prog <ayarlar>\n\tOrnek: %prog --baglan 127.0.0.1:8888\n")
    parser.add_option("-b", "--baglan",action="store",
                      dest="ipport",help="Baglanilacak adres IP:PORT")
    parser.add_option("-o", "--olustur", action="store_true",
                      help="Baglantilari bekle")
    
    global KOMUT_STR
    
    if len(sys.argv) < 2 :
        parser.print_help()
        sys.exit(0)
    
    (options, args) = parser.parse_args()
 
    
    if options.ipport and options.olustur:
            parser.print_help()
            sys.exit(0)
            
    
    if options.ipport:
        mObj = re.match(r"(.+):(.+)", options.ipport)
        if not mObj:
            print("\nLutfen IP ve PORT adresini dogru giriniz.")
            sys.exit(0)
        ip = mObj.group(1)
        try:
            port = int(mObj.group(2))
        except ValueError:
            print("\nLutfen PORT degerini sayisal giriniz.")
            sys.exit(0)
       
        conn = Client(ip,port)    
        lst = Thread(target = conn.dinleyici)
        lst.start()
       
        while True:
            cmd = input(KOMUT_STR)
            if cmd == ":kapat":
                break
            print("\nSen: " + cmd)
            conn.write_string(cmd)
            KOMUT_STR = "\n"
              
    elif options.olustur:
        serv = Server(ADRES, KAPI)
        lst = Thread(target = serv.dinleyici)
        print("Baglantilar bekleniyor ...")
        serv.server_loop() #
        lst.start()
        while True:
            cmd = input(KOMUT_STR)
            if cmd == ":kapat":
                break
            print("\nSen: " + cmd)
            serv.write_string(cmd)
            KOMUT_STR = "\n"
      

    
    
if __name__ == '__main__':
    main()