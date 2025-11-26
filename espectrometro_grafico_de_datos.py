import numpy as np
import matplotlib.pyplot as plt
import os
import datetime # Importamos datetime para generar el timestamp

# --- CONFIGURACIÓN DE CARPETAS Y ARCHIVOS ---

# La ruta a la carpeta donde están tus archivos .txt
CARPETA_DATOS = os.path.join("datos", "laser_verde")
EXTENSION_DATOS = ".txt"

Titulo= "Láser Verde"

# ---------------------------------------------

def cargar_y_analizar_espectros(carpeta_path):

    # 1. Preparar la lista de archivos
    archivos_espectro = []
    
    # Recorre todos los archivos en el directorio especificado
    for nombre_archivo in os.listdir(carpeta_path):
        if nombre_archivo.endswith(EXTENSION_DATOS):
            ruta_completa = os.path.join(carpeta_path, nombre_archivo)
            archivos_espectro.append(ruta_completa)
            
    if not archivos_espectro:
        print(f"Error: No se encontraron archivos {EXTENSION_DATOS} en la carpeta '{carpeta_path}'.")
        return

    print(f"Archivos encontrados: {len(archivos_espectro)}")
    
    # 2. Inicializar la figura y los ejes de Matplotlib
    fig, ax = plt.subplots(figsize=(14, 7))
    
    min_x = float('inf')
    max_x = float('-inf')
    max_y = float('-inf')

    # 3. Leer y trazar cada archivo
    for i, ruta_archivo in enumerate(archivos_espectro):
        nombre_archivo_base = os.path.basename(ruta_archivo)
        
        # --- ETIQUETA SIMPLIFICADA ---
        etiqueta_leyenda = f"e{i+1}"
        
        try:
            # Carga los datos (asumiendo 3 líneas de encabezado)
            datos = np.loadtxt(ruta_archivo, skiprows=3) 
            
            # La primera columna es X (Longitud de Onda), la segunda es Y (Intensidad)
            longitud_onda = datos[:, 0]
            intensidad = datos[:, 1]
            
            # Actualiza los límites para el gráfico final
            min_x = min(min_x, np.min(longitud_onda))
            max_x = max(max_x, np.max(longitud_onda))
            max_y = max(max_y, np.max(intensidad))
            
            # --- TRAZADO DEL ESPECTRO ---
            # 'k--' significa: 'k' (black/negro) y '--' (dashed/punteada)
            ax.plot(
                longitud_onda, 
                intensidad, 
                'k--', 
                linewidth=1, 
                alpha=0.7, # Transparencia para que se vean bien superpuestos
                label=etiqueta_leyenda # Usamos la etiqueta simplificada
            )
            print(f"Trazado: {nombre_archivo_base} (Etiqueta: {etiqueta_leyenda})")
            
        except Exception as e:
            print(f"Error al procesar el archivo {nombre_archivo_base}: {e}")
            continue

    # 4. Configuración Final de la Gráfica
    
    # Ajustar el eje X basado en el rango de los datos
    if min_x != float('inf'):
        ax.set_xlim(min_x * 0.99, max_x * 1.01) # Añadir un pequeño margen

    # Ajustar el eje Y de 0 hasta un poco más que el máximo
    if max_y != float('-inf'):
        ax.set_ylim(0, max_y * 1.1) 
        
    ax.set_xlabel("Longitud de Onda (nm)", fontsize=12, fontweight='bold')
    ax.set_ylabel("Intensidad", fontsize=12, fontweight='bold')
    ax.set_title(f"Superposición de Espectros de '{Titulo}'", 
                 fontsize=14, fontweight='bold')
    
    ax.grid(True, linestyle=':', alpha=0.5)
    
    # Mostrar la leyenda
    ax.legend(loc='upper right', fontsize=10) 
    
    # --- 5. GUARDAR LA IMAGEN (NUEVA SECCIÓN) ---
    
    # Crear un nombre de archivo único
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo_imagen = f"Superposicion_{Titulo.replace(' ', '_')}_{timestamp}.png"
    
    # Crear la ruta completa donde se guardará la imagen (en la misma carpeta de los TXT)
    ruta_guardado = os.path.join(carpeta_path, nombre_archivo_imagen)
    
    # Asegurarse de que la carpeta exista antes de guardar (aunque ya debería existir)
    os.makedirs(carpeta_path, exist_ok=True)
    
    # Guardar la imagen
    try:
        plt.savefig(ruta_guardado, bbox_inches='tight', dpi=300)
        print(f"\nImagen de superposición guardada en: {ruta_guardado}")
    except Exception as e:
        print(f"\nError al guardar la imagen: {e}")
        
    # 6. Mostrar la gráfica (es estática, no interactiva)
    plt.show()

# --- EJECUCIÓN DEL PROGRAMA ---

# 1. Verificar la existencia de la carpeta principal 'datos'
if not os.path.isdir("datos"):
    print("Error: La carpeta principal 'datos' no existe. Asegúrate de que la ruta sea correcta.")
else:
    # 2. Llamar a la función con la ruta deseada
    cargar_y_analizar_espectros(CARPETA_DATOS)