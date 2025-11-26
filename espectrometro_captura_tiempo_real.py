import serial
import numpy as np
import matplotlib.pyplot as plt
import time
from matplotlib.collections import LineCollection

# --- CONFIGURACIÓN SERIAL Y OFFSET ---

ser = serial.Serial('COM10', 115200, timeout=1) # PC=Laptop

#ser = serial.Serial('COM3', 115200, timeout=1) # PC= Torre


print("Conectado -- Esperando datos...")
time.sleep(2)

# VARIABLES GLOBALES
OFFSET_VALOR = 127
ADC_MAX = 1000 
Y_MAX_LIMITE = ADC_MAX - OFFSET_VALOR 
running = True # Flag de control para el bucle principal

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

# --- FUNCIONES DE CIERRE ---

def on_close(event):
    """Función para detener el bucle al cerrar la ventana de Matplotlib."""
    global running
    print("\nEvento de cierre de ventana detectado.")
    running = False

def on_key_press(event):
    """Función para detener el bucle al presionar la tecla 'q'."""
    global running
    if event.key == 'q':
        print("\nTecla 'q' (Quit) detectada.")
        running = False
# ----------------------------------

# Configurar gráfica
plt.ion()
fig, ax = plt.subplots(figsize=(14, 7))

# Conectar las funciones de cierre a los eventos de la figura
fig.canvas.mpl_connect('close_event', on_close)
fig.canvas.mpl_connect('key_press_event', on_key_press)

# Crear array de longitudes de onda y colores
x = np.linspace(380, 850, 288)
colors = [nm_to_rgb(wl) for wl in x]

# Configuración inicial de LineCollection y Ejes
points = np.array([x, np.zeros(288)]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)
lc = LineCollection(segments, colors=colors, linewidth=2)
ax.add_collection(lc)

ax.set_xlim(380, 850)
ax.set_ylim(0, Y_MAX_LIMITE) 
ax.set_xlabel("Longitud de Onda (nm)", fontsize=12, fontweight='bold')
ax.set_ylabel(f"Intensidad", fontsize=12, fontweight='bold')

# --- TÍTULO  ---
ax.set_title("Espectrómetro - Espectro en Tiempo Real", fontsize=14, fontweight='bold')


fig.text(0.5, 0.01, 
         "Presiona 'Q' para Salir o Cierra la Ventana", 
         ha='center', va='bottom', 
         fontsize=8, 
         color='gray')

# ------------------------------------------------------------------

ax.grid(True, alpha=0.3)
# --------------------------------------------------------

# Bucle principal, usa flag running
try:
    while running:
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
                        # Sustracción y Clip
                        datos_numpy = np.array(numeros)
                        datos_sustraidos = datos_numpy - OFFSET_VALOR
                        datos_ajustados = np.clip(datos_sustraidos, 0, Y_MAX_LIMITE) 
                        
                        # Actualización de la gráfica
                        numeros_ajustados = datos_ajustados.tolist() 
                        new_points = np.array([x, numeros_ajustados]).T.reshape(-1, 1, 2)
                        new_segments = np.concatenate([new_points[:-1], new_points[1:]], axis=1)
                        lc.set_segments(new_segments)
                        
                        # Cálculo y actualización del título
                        peak_intensidad = np.max(datos_ajustados)
                        idx_peak = np.argmax(datos_ajustados)
                        peak_longitud_onda = x[idx_peak]
                        peak_color = nm_to_rgb(peak_longitud_onda) # Llama a la función para el color
                        
                        # Actualización del título limpio
                        ax.set_title(f'Espectrómetro - Peak: {peak_longitud_onda:.1f} nm | Intensidad: {int(peak_intensidad)}', 
                                     fontsize=14, fontweight='bold', color=peak_color)
                        
                        plt.pause(0.01)
                        
            except Exception as e:
                # print(f"Error en el procesamiento de datos: {e}") 
                pass 
                
except KeyboardInterrupt:
    pass 
    
#FINALIZACIÓN DEL PROGRAMA 

ser.close()
plt.close()
print("\nPrograma terminado exitosamente.")