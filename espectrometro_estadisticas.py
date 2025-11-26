import numpy as np
import matplotlib.pyplot as plt
import os

# --- CONFIGURACIÓN DE CARPETAS Y ARCHIVOS ---
CARPETA_DATOS = os.path.join("datos", "diurna")
EXTENSION_DATOS = ".txt"
TITULO = "Análisis Estadístico - Luz Diurna"
# ---------------------------------------------

def analisis_estadistico_y_histograma_ajustado(carpeta_path, titulo):
    """
    Carga todos los espectros, calcula estadísticas y genera un histograma
    enfocado exclusivamente en el PÍXEL DE INTENSIDAD MÁXIMA.
    """
    
    archivos_espectro = []
    # (Código para cargar archivos omitido por brevedad, asumiendo que funciona)
    for nombre_archivo in os.listdir(carpeta_path):
        if nombre_archivo.endswith(EXTENSION_DATOS):
            ruta_completa = os.path.join(carpeta_path, nombre_archivo)
            archivos_espectro.append(ruta_completa)
            
    if not archivos_espectro:
        print(f"Error: No se encontraron archivos {EXTENSION_DATOS} en la carpeta '{carpeta_path}'.")
        return

    datos_completos = []
    longitud_onda_x = None
    
    for ruta_archivo in archivos_espectro:
        try:
            datos = np.loadtxt(ruta_archivo, skiprows=3) 
            if longitud_onda_x is None:
                longitud_onda_x = datos[:, 0]
            intensidad = datos[:, 1]
            datos_completos.append(intensidad)
        except Exception as e:
            print(f"Error al procesar el archivo {os.path.basename(ruta_archivo)}: {e}")
            continue

    if not datos_completos: return

    matriz_intensidad = np.array(datos_completos)
    media_intensidad = np.mean(matriz_intensidad, axis=0) 
    std_intensidad = np.std(matriz_intensidad, axis=0)
    
    # 1. ENCONTRAR EL PÍXEL DEL PEAK GLOBAL
    # Encontramos la posición del píxel con la intensidad más alta en el espectro promedio.
    idx_peak_global = np.argmax(media_intensidad)
    peak_max_nm = longitud_onda_x[idx_peak_global]
    
    # 2. EXTRAER DATOS SÓLO DE ESE PÍXEL
    # Extraemos todos los valores de intensidad de TODAS las capturas, pero solo para el píxel del pico.
    datos_histograma_foco = matriz_intensidad[:, idx_peak_global]
    
    # --- RESULTADOS CLAVE ---
    media_pico_val = media_intensidad[idx_peak_global]
    std_pico_val = std_intensidad[idx_peak_global]
    error_relativo = (std_pico_val / media_pico_val) * 100
    
    
    # 3. GENERACIÓN DEL HISTOGRAMA (MÁS FÁCIL DE INTERPRETAR)
    plt.figure(figsize=(10, 7))
    
    plt.hist(datos_histograma_foco, bins=10, color='darkgreen', alpha=0.8, edgecolor='black')
    
    # Líneas de referencia: Media y error de 1 sigma
    plt.axvline(media_pico_val, color='red', linestyle='dashed', linewidth=2, label=f'Media: {media_pico_val:.2f}')
    plt.axvline(media_pico_val + std_pico_val, color='orange', linestyle='dotted', linewidth=1, label=f'+1 $\sigma$')
    plt.axvline(media_pico_val - std_pico_val, color='orange', linestyle='dotted', linewidth=1, label=f'-1 $\sigma$')
    
    plt.title(f"Distribución de Intensidad en el Peak ({peak_max_nm:.2f} nm)\n(Error Relativo: {error_relativo:.2f} %)", fontsize=14, fontweight='bold')
    plt.xlabel("Intensidad (ADC sustraído Offset)", fontsize=12, fontweight='bold')
    plt.ylabel("Frecuencia (Conteo de Espectros)", fontsize=12, fontweight='bold')
    plt.legend()
    plt.grid(axis='y', linestyle=':', alpha=0.5)
    
    # Guardar la figura del histograma
    nombre_archivo_hist = os.path.join(carpeta_path, "Analisis_Histograma_Foco.png")
    plt.savefig(nombre_archivo_hist, bbox_inches='tight', dpi=300)
    print(f"Histograma de Intensidad ajustado guardado en: {nombre_archivo_hist}")
    
    
    # 4. Salida para el informe
    print("\n--- ERROR ESTADÍSTICO EN EL PICO MÁXIMO ---")
    print(f"Pico de Intensidad Máximo: {peak_max_nm:.2f} nm")
    print(f"Intensidad Promedio en el Pico: {media_pico_val:.2f} ADC")
    print(f"Desviación Estándar (Error): {std_pico_val:.2f} ADC")
    print(f"Error Relativo (Coeficiente de Variación): {error_relativo:.2f} %")


# --- EJECUCIÓN ---
analisis_estadistico_y_histograma_ajustado(CARPETA_DATOS, TITULO)