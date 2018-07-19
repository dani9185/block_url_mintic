#!/bin/bash
# ------------------------------------------------------------------------------
# Fecha inicial: 18 Julio 2018
# Descarga automatica de listado URL a bloquear Coljuegos de MINTIC
#
# Instruccion para la ejecucion (Permitir la ejecucion del script)
#   chmod +x <script>.sh
#   ./<script>.sh 
# ------------------------------------------------------------------------------


# Variales con informacion de Acceso MIN TIC
URL_MINTIC="http://archivo.mintic.gov.co/ubpi/664/articles-75802_archivo_txt.txt"
User="ArturoCuellar"
Pass="ArturoCuellar6542"

# Revisa si la url puede descargar el listado o problemas en el usuario y pass
OUTPUT="$(wget -SO- -T 1 -t 1 --spider --user=${User} --password=${Pass} ${URL_MINTIC} 2>&1 >/dev/null | egrep -i "404|Authentication Fail")"
if [ -z "${OUTPUT}" ]; then
    wget -q --user=${User} --password=${Pass} --output-document=listadoColjuegos_new.txt ${URL_MINTIC}
	md5sum listadoColjuegos.txt | awk {'print $1}' > checksum_listadoColjuegos
	md5sum listadoColjuegos_new.txt | awk {'print $1}' > checksum_listadoColjuegos_new
	OUTPUT="$(diff -q checksum_listadoColjuegos checksum_listadoColjuegos_new)"
	if [ -z "${OUTPUT}" ]; then
		#echo "iguales"
		rm -f listadoColjuegos_new.txt
	else
		echo "diferentes"
		mv listadoColjuegos_new.txt listadoColjuegos.txt
		cat listadoColjuegos.txt | wc -l
	fi
	rm -f checksum*
elif [ "${OUTPUT}" == "Username/Password Authentication Failed." ]; then
	echo "ERROR: Usuario o Password fallaron!!!"
else
	echo "ERROR: Cambios URL de Listado en MINTIC!!"
fi
