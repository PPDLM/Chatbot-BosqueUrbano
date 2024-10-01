from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from gspread.exceptions import APIError
import schedule
import time
import threading
from datetime import datetime
from dateutil.relativedelta import relativedelta
from twilio.rest import Client

app = Flask(__name__)

# Configuración de Google Sheets API (Cuenta de Servicio)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secrets.json', scope)
client = gspread.authorize(creds)
sheet = client.open("bosque_urbano").sheet1

# Configuración de Google Drive (Autenticación con PyDrive)
gauth = GoogleAuth()
gauth.credentials = creds  # Usa las credenciales de la cuenta de servicio para Google Drive
drive = GoogleDrive(gauth)

# Configuración de Twilio
twilio_account_sid = 'your_account_sid'
twilio_auth_token = 'your_auth_token'
twilio_phone_number = 'your_twilio_phone_number'
client_twilio = Client(twilio_account_sid, twilio_auth_token)

def enviar_mensaje(numero, mensaje):
    client_twilio.messages.create(
        body=mensaje,
        from_=twilio_phone_number,
        to=numero
    )

def verificar_fechas():
    today = datetime.now().date()
    try:
        # Obtener todos los valores de la columna de fechas
        fechas = sheet.col_values(3)  # Asume que las fechas están en la primera columna

        for i, fecha in enumerate(fechas):
            # Convertir fecha en la hoja de cálculo al formato de fecha
            fecha_hoja = datetime.strptime(fecha, "%d/%m/%Y").date()

            # Si la fecha coincide con la de hace un año, enviar un mensaje
            if fecha_hoja == today - relativedelta(years=1):
                # Obtener el número de teléfono de la columna correspondiente
                telefono = sheet.cell(i + 1, 1).value  # Asume que los números están en la segunda columna
                enviar_mensaje(telefono, "Recuerda confirmar el estado de tu árbol.")
    except APIError as e:
        print(f"Error de API al obtener fechas: {str(e)}")

def programar_verificaciones():
    schedule.every().day.at("02:00").do(verificar_fechas)  # Verifica cada día a las 02:00 PM

    while True:
        schedule.run_pending()
        time.sleep(1)

def actualizar_confirmacion(numero, confirmacion):
    try:
        # Busca el número de teléfono en la hoja
        cell = sheet.find(numero.split(":")[1])
        print(numero.split(":")[1])
        if cell:
            # Si encuentra el número, actualiza la columna de confirmación
            sheet.update_cell(row=cell.row, col=4, value=confirmacion)  # La columna 4 es la de confirmación
        else:
            print(f"El número {numero} no se encontró en la hoja de cálculo.")
    except APIError as e:
        print(f"Error de API al buscar o actualizar el número: {str(e)}")

def subir_imagen(imagen_url, nombre_archivo):
    file_drive = drive.CreateFile({'title': nombre_archivo})
    file_drive.Upload()  # Aquí deberías proporcionar el contenido del archivo en lugar de la URL
    return file_drive['id']

@app.route("/whatsapp", methods=['POST'])
def whatsapp():
    incoming_msg = request.values.get('Body', '').lower()
    phone_number = request.values.get('From', '')  # Obtener el número de teléfono del remitente
    resp = MessagingResponse()
    msg = resp.message()
    
    if 'VIVO' in incoming_msg:
        # Actualiza la hoja de cálculo en la columna de confirmación
        actualizar_confirmacion(phone_number, 'CONFIRMADO')
        msg.body("Gracias por confirmar que tu árbol está vivo. Por favor, envía una foto.")
    elif request.values.get('NumMedia') != '0':
        # Guardar la imagen
        media_url = request.values.get('MediaUrl0')
        file_name = "image.jpg"  # Puedes usar el nombre del archivo recibido en la solicitud
        subir_imagen(media_url, file_name)
        msg.body("Gracias por la imagen. La organización la revisará pronto.")
    else:
        msg.body("Por favor, confirma si tu árbol está vivo respondiendo con la palabra 'VIVO'.")

    return str(resp)

if __name__ == "__main__":    # Iniciar el hilo de verificación de fechas
    thread = threading.Thread(target=programar_verificaciones)
    thread.start()
    
    app.run(debug=True)