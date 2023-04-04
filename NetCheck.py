import requests
import json
import os
import concurrent.futures
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import traceback
import sys
from datetime import datetime

# Definimos una función que hará la petición GET
def get_request(url):
    try:
        response = requests.get(url[1], verify=False)
        response.raise_for_status()
        #print(f"Url:{str(url[1])} - {response.elapsed.total_seconds()}")
        return response.status_code
    except requests.exceptions.HTTPError as http_err:
        pass
        #print(f'Error HTTP: {http_err}')
    except requests.exceptions.Timeout as timeout_err:
        pass
        #print(f'Timeout Error: {timeout_err}')
    except requests.exceptions.RequestException as err:
        pass
        #print(f'Error de solicitud: {err}')
    return 404

def Get_Json():
    try:
        data = {}
        if os.path.exists("NetCheck.json"):
            with open('NetCheck.json') as file:
                data = json.load(file)
        else:
            with open('NetCheck.json', 'w') as file:
                json.dump({}, file, indent=4)
    except Exception as e:
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))
    return data

def SelectRegister(data):
    list_url = []
    try:
        for x in data.keys():
            list_url.append([x,data[x]['Url'],data[x]['Timeout']])
    except Exception as e:
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))
    return list_url

def SendMessageTelegram(chatid,message,bot):
    url=f"https://api.telegram.org/{bot}/sendMessage"
    requests.post(url,
              data={'chat_id': chatid, 'text': message , 'parse_mode':'Markdown'})

    # Definimos una lista de URLs a las que queremos hacer una petición GET

if __name__ =="__main__":
    data = Get_Json()
    urls = SelectRegister(data)
    print(urls)
    #Definimos un diccionario vacío para almacenar los resultados de las peticiones GET
    responses = {}
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    # Utilizamos un contexto de ThreadPoolExecutor para enviar múltiples peticiones GET al mismo tiempo
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Utilizamos la función map para enviar las peticiones GET a cada URL de la lista
        # La función map devuelve un iterable de resultados que almacenamos en el diccionario de respuestas
        for url, response_code in zip(urls, executor.map(get_request, urls)):
            responses[url[0]] = response_code
            now = datetime.now()
            print(response_code)
            if response_code != 200:
                if not 'Drop' in data[url[0]]:
                    data[url[0]].update({"Drop":True,"First_Drop":str(now.strftime("%d/%m/%Y %H:%M:%S"))})
                    SendMessageTelegram(data[url[0]]["Chat_Id"],f" \U0001F534  {url[0]} Caida \n Fecha y Hora: {str(now.strftime('%d/%m/%Y %H:%M:%S'))}",data[url[0]]["Bot"])
            else:
                if 'Drop' in data[url[0]]:
                    Date_Last = data[url[0]]['First_Drop']
                    fecha1 = datetime.strptime(Date_Last,'%d/%m/%Y %H:%M:%S')
                    neo = str(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
                    fecha2=datetime.strptime(neo,'%d/%m/%Y %H:%M:%S')
                    diferencia = fecha2 - fecha1 # Calcula la diferencia
                    dias = diferencia.days
                    segundos_totales = diferencia.seconds
                    horas = segundos_totales // 3600
                    minutos = (segundos_totales % 3600) // 60
                    segundos = segundos_totales % 60
                    del data[url[0]]['Drop'] 
                    del data[url[0]]['First_Drop']
                    SendMessageTelegram(data[url[0]]["Chat_Id"],f" \U0001F7E2  {url[0]} Servicio en linea \n Fecha y Hora: {str(now.strftime('%d/%m/%Y %H:%M:%S'))} \n Tiempo Caido : {dias} Dias {horas} Horas {minutos} Minutos {segundos} Segundos",data[url[0]]["Bot"])
    # Imprimimos los resultados
    with open('NetCheck.json', 'w') as file:
            file.write(json.dumps(data, ensure_ascii=False,indent=4)) 

