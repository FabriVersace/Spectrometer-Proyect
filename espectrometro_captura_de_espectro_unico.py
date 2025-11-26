import serial
import numpy as np
import matplotlib.pyplot as plt
import time
import datetime 
import os # Importamos la librería OS
from matplotlib.collections import LineCollection

# --- CONFIGURACIÓN SERIAL Y OFFSET ---

CARPETA_DATOS = os.path.join("datos", "laser_verde")

ser = serial.Serial('COM10', 115200, timeout=1) # PC=Laptop

#ser = serial.Serial('COM3', 115200, timeout=1) # PC= Torre


print("Conectado -- Intentando capturar datos...")
time.sleep(2)

# VARIABLES GLOBALES
OFFSET_VALOR = 127
ADC_MAX = 1000 
Y_MAX_LIMITE = ADC_MAX - OFFSET_VALOR 

# Función para convertir nm a color RGB 
def nm_to_rgb(wavelength):
    """Convierte longitud de onda (nm) a color RGB aproximado"""
    gamma = 1
    
    if wavelength < 380: wavelength = 380
    if wavelength > 780: wavelength = 780
        
    if 380 <= wavelength < 440:
        r = -(wavelength - 440) / (440 - 380)
        g = 0.0
        b = 1.0
    elif 440 <= wavelength < 490:
        r = 0.0
        g = (wavelength - 440) / (490 - 440)
        b = 1.0
    elif 490 <= wavelength < 510:
        r = 0.0
        g = 1.0
        b = -(wavelength - 510) / (510 - 490)
    elif 510 <= wavelength < 580:
        r = (wavelength - 510) / (580 - 510)
        g = 1.0
        b = 0.0
    elif 580 <= wavelength < 645:
        r = 1.0
        g = -(wavelength - 645) / (645 - 580)
        b = 0.0
    elif 645 <= wavelength <= 780:
        r = 1.0
        g = 0.0
        b = 0.0
    else:
        r, g, b = 0.0, 0.0, 0.0

    # intensidad en los bordes
    if 380 <= wavelength < 420:
        factor = 0.3 + 0.7 * (wavelength - 380) / (420 - 380)
    elif 420 <= wavelength < 700:
        factor = 1.0
    elif 700 <= wavelength <= 780:
        factor = 0.3 + 0.7 * (780 - wavelength) / (780 - 700)
    else:
        factor = 1.0

    r = min(1.0, (r * factor) ** gamma)
    g = min(1.0, (g * factor) ** gamma)
    b = min(1.0, (b * factor) ** gamma)
    
    return (r, g, b)

# --- CAPTURA Y PROCESAMIENTO DE UNA SOLA LÍNEA DE DATOS ---

datos_capturados = None
datos_ajustados = None # Mantener esta variable para usarla más tarde

# Esperamos hasta 10 segundos por una línea de datos válida
tiempo_inicio = time.time()
while time.time() - tiempo_inicio < 10: 
    if ser.in_waiting > 0:
        try:
            raw = ser.readline()
            texto = raw.decode('utf-8', errors='ignore').strip()
            
            if texto and ',' in texto:
                numeros = []
                for num in texto.split(','):
                    num = num.strip()
                    if num and num.isdigit():
                        numeros.append(int(num))
                
                if len(numeros) == 288:
                    # Datos válidos encontrados
                    # Sustracción y Clip
                    datos_numpy = np.array(numeros)
                    datos_sustraidos = datos_numpy - OFFSET_VALOR
                    datos_ajustados = np.clip(datos_sustraidos, 0, Y_MAX_LIMITE) 
                    datos_capturados = datos_ajustados.tolist()
                    print("Datos capturados exitosamente.")
                    break
        except Exception as e:
            print(f"Error durante la lectura serial: {e}")
            pass
    time.sleep(0.01) # Pequeña pausa para no saturar la CPU

# --- CIERRE TEMPRANO SI NO HAY DATOS ---
if datos_capturados is None:
    print("Error: No se pudieron capturar 288 puntos de datos válidos.")
    ser.close()
    exit()

# --- CONFIGURACIÓN Y TRAZADO DE LA GRÁFICA (SIN MODO INTERACTIVO) ---

# Crear array de longitudes de onda y colores (Necesario para el trazado)
x = np.linspace(380, 850, 288)
colors = [nm_to_rgb(wl) for wl in x]

# Cálculo de información del peak
peak_intensidad = np.max(datos_ajustados) # Usamos los datos_ajustados de la captura
idx_peak = np.argmax(datos_ajustados)
peak_longitud_onda = x[idx_peak]
peak_color = nm_to_rgb(peak_longitud_onda)

# Configurar gráfica
fig, ax = plt.subplots(figsize=(14, 7))

# Configuración de LineCollection con los datos capturados
points = np.array([x, datos_capturados]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)
lc = LineCollection(segments, colors=colors, linewidth=2)
ax.add_collection(lc)

# Configuración de Ejes
ax.set_xlim(380, 850)
ax.set_ylim(0, Y_MAX_LIMITE) 
ax.set_xlabel("Longitud de Onda (nm)", fontsize=12, fontweight='bold')
ax.set_ylabel(f"Intensidad ", fontsize=12, fontweight='bold')

# TÍTULO FINAL
ax.set_title(f'Espectrómetro | Peak: {peak_longitud_onda:.1f} nm | Intensidad: {int(peak_intensidad)}', 
             fontsize=14, fontweight='bold', color=peak_color)

ax.grid(True, alpha=0.3)
# ------------------------------------------------------------------

# --- GESTIÓN DE CARPETAS Y GUARDADO DE ARCHIVOS ---

# 1. Definir la ruta de la carpeta


# 2. Crear la carpeta si no existe
# os.makedirs(..., exist_ok=True) asegura que si ya existe, no arroje un error.
os.makedirs(CARPETA_DATOS, exist_ok=True)
print(f"Carpeta '{CARPETA_DATOS}' verificada/creada.")

# 3. Crear el nombre de archivo base
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
nombre_base = f"Espectro_Captura_{timestamp}"

# 4. Construir las rutas completas de los archivos
# os.path.join() construye rutas que funcionan tanto en Windows, Linux como macOS.
ruta_imagen = os.path.join(CARPETA_DATOS, nombre_base + ".png")
ruta_datos = os.path.join(CARPETA_DATOS, nombre_base + ".txt")

# 5. Guardar la imagen
plt.savefig(ruta_imagen, bbox_inches='tight', dpi=300) 
print(f"Imagen guardada en: {ruta_imagen}")

# 6. Guardar los datos en TXT
datos_combinados = np.stack((x, datos_ajustados), axis=1)

header_text = f"Espectro C12880MA - Capturado el {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
header_text += f"Offset sustraido: {OFFSET_VALOR}\n"
header_text += f"Longitud_Onda (nm)\tIntensidad (ADC)"

np.savetxt(
    ruta_datos,
    datos_combinados,
    fmt=['%.4f', '%d'], 
    delimiter='\t',
    header=header_text,
    comments='# '
)
print(f"Datos guardados en: {ruta_datos}")
# ------------------------------------------------------------------

# --- FINALIZACIÓN DEL PROGRAMA ---
ser.close()
plt.close() 
print("\nPrograma terminado exitosamente.")