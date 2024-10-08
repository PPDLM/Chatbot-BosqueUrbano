﻿# Chatbot-BosqueUrbano
1. Importaciones y Configuración Inicial
- Flask: Un framework web en Python que permite crear aplicaciones web.
- twilio.twiml.messaging_response: Permite construir respuestas para mensajes entrantes de Twilio.
- gspread: Una biblioteca para interactuar con Google Sheets.
- oauth2client.service_account: Proporciona autenticación para acceder a APIs de Google.
- pydrive.auth y pydrive.drive: Permiten autenticarse y trabajar con Google Drive.
- gspread.exceptions.APIError: Excepción específica para errores de la API de Google Sheets.

2. Inicialización de la Aplicación Flask
- app = Flask(__name__): Crea una instancia de la aplicación Flask.

3. Configuración de Google Sheets API
- scope: Define los permisos que la aplicación necesita para acceder a Google Sheets y Google Drive.
- ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope): Carga las credenciales desde un archivo JSON.
- gspread.authorize(creds): Autoriza el cliente de gspread para interactuar con Google Sheets usando las credenciales.
- client.open("bosque_urbano").sheet1: Abre la hoja de cálculo llamada "bosque_urbano" y selecciona la primera hoja (sheet1).

4. Configuración de Google Drive
- GoogleAuth(): Inicializa la autenticación con Google Drive.
- gauth.LocalWebserverAuth(): Autenticación local a través de un navegador web.
- GoogleDrive(gauth): Crea una instancia de GoogleDrive para manejar archivos en Google Drive.

5. Función actualizar_confirmacion
- sheet.find(numero): Busca el número de teléfono en la hoja de cálculo.
- sheet.update_cell(cell.row, 4, confirmacion): Actualiza la celda correspondiente a la columna 4 (confirmación) con el valor proporcionado.
- APIError as e: Captura errores específicos de la API y los imprime.

6. Función subir_imagen
- drive.CreateFile({'title': nombre_archivo}): Crea un archivo en Google Drive con el nombre dado.
- file_drive.Upload(): Sube el archivo a Google Drive. Nota: Aquí deberías proporcionar el contenido del archivo, no solo la URL.
- return file_drive['id']: Devuelve el ID del archivo recién subido.

7. Ruta de la Aplicación /whatsapp
@app.route("/whatsapp", methods=['POST']): Define la ruta /whatsapp que acepta solicitudes POST.
request.values.get('Body', '').lower(): Obtiene el cuerpo del mensaje enviado por el usuario y lo convierte a minúsculas.
request.values.get('From', ''): Obtiene el número de teléfono del remitente del mensaje.
MessagingResponse(): Crea una respuesta de Twilio para enviar un mensaje de vuelta al usuario.
msg.body("mensaje"): Define el mensaje que se enviará de vuelta al usuario.
Condiciones:
if 'vivo' in incoming_msg: Si el mensaje contiene la palabra 'vivo', actualiza la hoja de cálculo y solicita una foto.
elif request.values.get('NumMedia') != '0': Si se ha enviado una imagen, guarda la imagen en Google Drive.
else: Si no se ha recibido ni la confirmación ni una imagen, solicita que el usuario confirme que su árbol está vivo.

8. Ejecución de la Aplicación
app.run(debug=True): Ejecuta la aplicación Flask en modo de depuración, lo que proporciona más detalles sobre errores y recarga automáticamente el servidor cuando se hacen cambios en el código.
