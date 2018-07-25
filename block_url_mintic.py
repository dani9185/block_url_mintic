#!/usr/bin/python3
#-----------------------------------------------------------------------------
# Descripcion:
# Fecha Creacion: 25 julio 2018
# Descarga automatica de listado URL a bloquear Coljuegos de MINTIC y genera
# el file para el servidor bind
# Prerequisitos de instalacion:
#	  sudo yum -y install python3
#     sudo yum -y install python3-pip (Instalaicon de pip instalacion de libs)
#	  sudo pip3 install tldextract
# Run time command:
#   sudo python3 block_url_mintic.py
#-----------------------------------------------------------------------------

#*****************************************************************************
# Library Load
#*****************************************************************************
import os
#import re
import sys
import subprocess
#import requests
#import xmltodict
import tldextract
#from urllib.parse import urlparse


#******************************************************************************
# Global Variable
#******************************************************************************
PATH = ""
PATH_BIND = "/etc/bind/named.conf.redirect-coljuegos.zones"
# Variales con informacion de Acceso MIN TIC
URL_MINTIC = "http://archivo.mintic.gov.co/ubpi/664/articles-75802_archivo_txt.txt"
User = "ArturoCuellar"
Pass = "ArturoCuellar6542"
#******************************************************************************
# Funtions
#******************************************************************************


def nonblank_lines(f):
    for l in f:
        line = l.rstrip()
        if line:
            yield line


def url2domain(url):
    urlparser = tldextract.extract(url)
    wildcard = urlparser.domain + '.' + urlparser.suffix
    return wildcard + '\n'


def domain2bindfile(domain):
    part1 = 'zone "'
    part2 = '"{\n\ttype master;\n\tfile "/etc/bind/redirect_coljuegos/db.redirect_coljuegos.zone";\n\tallow-query { any; };\n};\n\n'
    return part1 + domain + part2


def main():
    #Checkea que el file exista y se pueda acceder
    cmd = "wget -SO- -T 1 -t 1 --spider --user=" + User + " --password=" \
          + Pass + " " + URL_MINTIC + " 2>&1 >/dev/null | " \
          "egrep -i '404|Authentication Fail'"
    check_list = subprocess.getoutput(cmd)
    if(check_list == ""):
        #Descarga el listado en formato txt de MINTIC
        cmd = "wget -q --user=" + User + " --password=" + Pass + \
              " --output-document=listadoColjuegos_new.txt " + URL_MINTIC
        subprocess.call(cmd, shell=True)
        #Saca los MD5 de los archivos para comparar si hay algun cambio.
        subprocess.call("md5sum listadoColjuegos.txt | awk {'print $1}' > "
                        "checksum_listadoColjuegos", shell=True)
        subprocess.call("md5sum listadoColjuegos_new.txt | awk {'print $1}' > "
                        "checksum_listadoColjuegos_new", shell=True)
        #Compara los MD5 obtenidos para revisar si hay diferencia
        cmd = "diff -q checksum_listadoColjuegos checksum_listadoColjuegos_new"
        Lists_diff = subprocess.getoutput(cmd)
        if(Lists_diff == ""):
            # Listados Coljuegos Iguales
            print("Listas Iguales")
            subprocess.call("rm -f listadoColjuegos_new.txt", shell=True)
        else:
            print("Listas Diferentes")
            # Listados Coljuegos Diferentes
            subprocess.call("mv listadoColjuegos_new.txt listadoColjuegos.txt",
                            shell=True)
            #Convierte la codificacion del archivo a UTF-8
            subprocess.call("iconv -f ISO-8859-1 -t UTF-8//TRANSLIT "
                            "listadoColjuegos.txt -o listadoColjuegos_tmp.txt",
                            shell=True)
            # Genera el file Temp con los dominios sin URI Coljuegos.
            temp_ptr = open('temp', 'w')
            with open('listadoColjuegos_tmp.txt', 'r') as fin:
                for line in nonblank_lines(fin):
                    temp_ptr.write(url2domain(line))
            temp_ptr.close()
            # Ordena alfabeticamente el listado de dominos Coljuegos
            txt = open('temp', 'r').read()
            txt = txt.lower()
            content_set = '\n'.join(sorted(set(txt.splitlines())))
            # Genera el file de salida con los dominos alfabeticamente
            cleandata_ptr = open('domains.txt', 'w')
            for line in content_set:
                cleandata_ptr.write(line)
            cleandata_ptr.close()
            # Genera el file para bind para redireccion a portal de Coljuegos
            bindfile_ptr = open(PATH_BIND, 'w')
            with open('domains.txt', 'r') as fin:
                for line in nonblank_lines(fin):
                    bindfile_ptr.write(domain2bindfile(line))
            bindfile_ptr.close()
            # Reinicia y syncroniza los servidores DNS de BTLATAM:
            subprocess.call("sh ~/sync-zones.sh", shell=True)
            # Elimina files temporales
            os.remove("domains.txt")
            os.remove("temp")
            os.remove("listadoColjuegos_tmp.txt")
        os.remove("checksum_listadoColjuegos")
        os.remove("checksum_listadoColjuegos_new")
    elif (check_list == "Username/Password Authentication Failed."):
        print("ERROR: Usuario o Password fallaron!!!")
    else:
        print("ERROR: Cambios en URL de Listas en MINTIC!!")


#******************************************************************************
# MAIN process
#******************************************************************************
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        try:
            print("Keyboard Interrupt")
            sys.exit(0)
        except SystemExit:
            os._exit(0)
