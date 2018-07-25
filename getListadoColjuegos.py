#!/usr/bin/python3
# ------------------------------------------------------------------------------
# Fecha inicial: 24 Julio 2018
# Descarga automatica de listado URL a bloquear Coljuegos de MINTIC
#
# Instruccion para la ejecucion (Permitir la ejecucion del script)
#   chmod +x <script>.py
#   python3 <script>.py
# ------------------------------------------------------------------------------
import subprocess

# Variales con informacion de Acceso MIN TIC
URL_MINTIC = "http://archivo.mintic.gov.co/ubpi/664/articles-75802_archivo_txt.txt"
User = "ArturoCuellar"
Pass = "ArturoCuellar6542"


cmd = "wget -SO- -T 1 -t 1 --spider --user=" + User + " --password=" + Pass + \
      " " + URL_MINTIC +" 2>&1 >/dev/null | egrep -i '404|Authentication Fail'"
check_list = subprocess.getoutput(cmd)
if(check_list == ""):
    print("Existe lista en MinTIC")
elif (check_list == "Username/Password Authentication Failed."):
    print("ERROR: Usuario o Password fallaron!!!")
else:
    print("ERROR: Cambios en URL de Listas en MINTIC!!")
