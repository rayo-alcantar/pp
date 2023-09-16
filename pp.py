import os
import sys
import winsound
import subprocess
import json
import easygui
import random
if hasattr(sys, '_MEIPASS'):
    os.environ['VLC_PLUGIN_PATH'] = os.path.join(sys._MEIPASS, 'plugins')
import vlc
import accessible_output2.outputs.auto
import time
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1' #le decimos a pygame que no queremos su bienvenida de mierda.
import pygame
import requests

LOCAL_VERSION = 0.5 #versión.
#crear objeto
o=accessible_output2.outputs.auto.Auto()

#Creamos la función para usarla en otras.
def Talk(Text):
    o.speak(f"{Text}", interrupt=True)

def download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

def check_for_updates():
    try:
        response = requests.get("https://rayoscompany.com/pp.txt")
        online_version = float(response.text.strip())

        if online_version > LOCAL_VERSION:
            Talk(f"¡Hay una nueva versión disponible! Tu versión actual es {LOCAL_VERSION} y la versión en línea es {online_version}. Descargando la nueva versión...")
            download_url = "http://rayoscompany.com/pp.zip"
            download_file(download_url, "pp.zip")
            Talk("La nueva versión se ha descargado como play-porno.zip en la carpeta del programa. Por favor, descomprime y reemplaza los archivos para actualizar.")
            time.sleep(3)
        else:
            Talk("Estás utilizando la versión más reciente del programa.")
    except requests.exceptions.RequestException:
        Talk("No se pudo comprobar las actualizaciones. Por favor, verifica tu conexión a Internet.")

# Llame a la función check_for_updates() cuando desee verificar las actualizaciones
def beep(frequency, duration):
    winsound.Beep(frequency, duration)

# Realizar un beep y dar la bienvenida al usuario
beep(1000, 200)
check_for_updates()
Talk(f'¡Bienvenido a play porno! ¡Versión {LOCAL_VERSION}!')
time.sleep(3)
#funciones para sleeccionar carpeta.
# Función para guardar la configuración en un archivo JSON
def save_config(folder_path):
    config_data = {'path': folder_path}
    with open('config.json', 'w') as config_file:
        json.dump(config_data, config_file)
# Función para leer la configuración desde un archivo JSON
def read_config():
    config_file_path = "config.json"
    if os.path.exists(config_file_path):
        with open(config_file_path, "r") as config_file:
            try:
                config_data = json.load(config_file)
                return config_data.get("path", None)
            except json.JSONDecodeError:
                print("El archivo de configuración está vacío o tiene un formato incorrecto.")
                return None
    return None


# Función para seleccionar una carpeta usando easygui
def select_folder():
    folder_path = easygui.diropenbox()
    return folder_path

path = read_config()

if not path:
    path = select_folder()
    if path:
        save_config(path)
    else:
        Talk("No se seleccionó una carpeta. El programa se cerrará.")
        exit()

#Definimos función para verbalizar los atajos de teclado del programa.
def show_help_menu():
    help_text = """
    Menú de ayuda:
    Flecha izquierda: Retroceder 15 segundos.
    Flecha derecha: Avanzar 15 segundos.
    Espacio: Pausar o reanudar la reproducción.
    Q: Salir del programa.
    T: Anunciar el tiempo de reproducción actual y la duración total.
    Flecha arriba: Aumentar el volumen.
    Flecha abajo: Disminuir el volumen.
    M: Mutear y desmutear audio.
    N: Avanzar a la siguiente pista de audio.
    1-0: Avanzar al porcentaje correspondiente (10-90%) de la reproducción.
    h: Abrir archivo de ayuda.
    o: Abrir explorador de archivos para seleccionar audio.
    """
    Talk(help_text)
                          #Funcción para anunciar el tiempo de reproducción
def announce_playback_time(player):
    current_time = player.get_time() // 1000
    total_time = player.get_length() // 1000

    current_minutes = current_time // 60
    current_seconds = current_time % 60

    total_minutes = total_time // 60
    total_seconds = total_time % 60

    Talk(f"Tiempo de reproducción actual: {current_minutes:.0f} minutos y {current_seconds:.0f} segundos. Duración total: {total_minutes:.0f} minutos y {total_seconds:.0f} segundos.")


# Obtener la lista de archivos en la carpeta
files = os.listdir(path)

# Filtrar solo los archivos de audio
audio_files = [f for f in files if f.endswith('.mp3') or f.endswith('.wav') or f.endswith('.ogg')]

# Generar un número aleatorio entre 0 y el número de archivos de audio (menos 1)
rand_index = random.randint(0, len(audio_files) - 1)

# Obtener el nombre del archivo de audio en la posición generada aleatoriamente
audio_file = audio_files[rand_index]

# Mostrar el nombre del archivo de audio que se reproducirá
Talk(f"Reproduciendo: {audio_file}")

# Crear un objeto de VLC MediaPlayer y cargar el archivo de audio
player = vlc.MediaPlayer(os.path.join(path, audio_file))

# Reproducir el archivo de audio
player.play()

# Esperar un momento para que el audio comience a reproducirse
time.sleep(0.1)

pygame.init()
display = pygame.display.set_mode((300, 300))
pygame.display.set_caption(audio_file)

# Variables de control
running = True
muted = False
current_pos = 0

while running:
    paused = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Si se presiona la flecha izquierda, retroceder 15 segundos en la reproducción
            if event.key == pygame.K_LEFT:
                current_pos = max(0, player.get_time() - 15000)
                player.set_time(current_pos)
                Talk("Retrocediste el audio.")

            # Si se presiona la flecha derecha, avanzar 15 segundos en la reproducción
            elif event.key == pygame.K_RIGHT:
                current_pos = player.get_time() + 15000
                player.set_time(current_pos)
                Talk("Avanzaste el audio.")

            # Si se presiona la tecla de espacio, pausar o reanudar la reproducción
            elif event.key == pygame.K_SPACE:
                if not paused:
                    player.pause()
                    paused = True
                    Talk("Pausaste el audio.")
                else:
                    player.pause()
                    paused = False
                    talk("Reanudaste el audio.")
                
            # Si se presiona la tecla 'Q', salir del programa
            elif event.key == pygame.K_q:
                winsound.Beep(frequency, duration)
                Talk("Cerrando el programa...")
                time.sleep(1)
                running = False
                
                time.sleep(2)
                
                

            # Agregar esta condición para manejar la tecla "T"
            elif event.key == pygame.K_t:
                announce_playback_time(player)

                        # Aumentar el volumen con la flecha arriba
            elif event.key == pygame.K_UP:
                current_volume = player.audio_get_volume()
                new_volume = min(current_volume + 5, 100)
                player.audio_set_volume(new_volume)
                Talk(f"Volumen: {new_volume}%")

            # Disminuir el volumen con la flecha abajo
            elif event.key == pygame.K_DOWN:
                current_volume = player.audio_get_volume()
                new_volume = max(current_volume - 5, 0)
                player.audio_set_volume(new_volume)
                Talk(f"Volumen: {new_volume}%")
                    # Si se presiona la tecla 'n', avanzar a la siguiente pista de audio
            elif event.key == pygame.K_n:
                rand_index = random.randint(0, len(audio_files) - 1)
                new_audio_file = audio_files[rand_index]
                while new_audio_file == audio_file:  # Asegurar que se seleccione un archivo de audio diferente
                    rand_index = random.randint(0, len(audio_files) - 1)
                    new_audio_file = audio_files[rand_index]
                audio_file = new_audio_file
                Talk(f"Reproduciendo: {audio_file}")
                player.stop()  # Detener la reproducción actual
                player = vlc.MediaPlayer(os.path.join(path, audio_file))  # Crear un nuevo objeto de VLC MediaPlayer
                player.play()
                pygame.display.set_caption(audio_file)
                current_pos = 0
            elif event.key == pygame.K_5:
                half_length = int(player.get_length() / 2)
                player.set_time(half_length)
                Talk("Avanzaste al 50% de la reproducción.")
            elif event.key == pygame.K_1:
                target_percent = 0.1
                target_position = int(player.get_length() * target_percent)
                player.set_time(target_position)
                Talk(f"Avanzaste al {target_percent * 100:.0f}% de la reproducción.")
            elif event.key == pygame.K_2:
                target_percent = 0.2
                target_position = int(player.get_length() * target_percent)
                player.set_time(target_position)
                Talk(f"Avanzaste al {target_percent * 100:.0f}% de la reproducción.")
            elif event.key == pygame.K_3:
                target_percent = 0.3
                target_position = int(player.get_length() * target_percent)
                player.set_time(target_position)
                Talk(f"Avanzaste al {target_percent * 100:.0f}% de la reproducción.")
            elif event.key == pygame.K_4:
                target_percent = 0.4
                target_position = int(player.get_length() * target_percent)
                player.set_time(target_position)
                Talk(f"Avanzaste al {target_percent * 100:.0f}% de la reproducción.")
            elif event.key == pygame.K_6:
                target_percent = 0.6
                target_position = int(player.get_length() * target_percent)
                player.set_time(target_position)
                Talk(f"Avanzaste al {target_percent * 100:.0f}% de la reproducción.")
            elif event.key == pygame.K_7:
                target_percent = 0.7
                target_position = int(player.get_length() * target_percent)
                player.set_time(target_position)
                Talk(f"Avanzaste al {target_percent * 100:.0f}% de la reproducción.")
            elif event.key == pygame.K_8:
                target_percent = 0.8
                target_position = int(player.get_length() * target_percent)
                player.set_time(target_position)
                Talk(f"Avanzaste al {target_percent * 100:.0f}% de la reproducción.")
            elif event.key == pygame.K_9:
                target_percent = 0.9
                target_position = int(player.get_length() * target_percent)
                player.set_time(target_position)
                Talk(f"Avanzaste al {target_percent * 100:.0f}% de la reproducción.")
            elif event.key == pygame.K_0:
                player.set_time(0)
                Talk("Reiniciaste el audio.")
                
            if event.key == pygame.K_F1:
                show_help_menu()
            elif event.key == pygame.K_m:
                if not muted:
                    player.audio_toggle_mute()
                    muted = True
                    Talk("Audio silenciado")
                else:
                    player.audio_toggle_mute()
                    muted = False
                    Talk("Audio reactivado.")
            
            elif event.key == pygame.K_o:
                # Abrir explorador de archivos para seleccionar un archivo
                import tkinter as tk
                from tkinter import filedialog
            
                root = tk.Tk()
                root.withdraw()
                
                file_path = filedialog.askopenfilename(initialdir=path, title="Selecciona un archivo",
                                                      filetypes=[("Archivos de audio", "*.mp3 *.wav *.ogg")])
            
                if file_path:
                    # Obtener nombre de archivo
                    selected_file = os.path.basename(file_path)
            
                    # Crear MediaPlayer y reproducir
                    player.stop()
                    player = vlc.MediaPlayer(file_path)
                    player.play()
            
                    # Actualizar interfaz gráfica
                    pygame.display.set_caption(selected_file) 
                    Talk(f"Reproduciendo {selected_file}")
            elif event.key == pygame.K_h:
                try:
                    Talk("Abriendo la ayuda...")
                    subprocess.run(["notepad.exe", "readme.txt"])
                except FileNotFoundError:
                    Talk("No se encontró el archivo readme.txt")
                    
# Detener la reproducción del audio y salir de pygame
player.stop()
pygame.quit()