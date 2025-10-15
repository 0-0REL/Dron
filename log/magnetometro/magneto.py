# Convertir archivo a formato de referencia
def convertir_archivo(input_file, output_file):
    with open(input_file, 'r') as f_in:
        with open(output_file, 'w') as f_out:
            for linea in f_in:
                # Dividir por tabs y convertir a floats
                valores = linea.strip().split('\t')
                if len(valores) == 3:
                    try:
                        # Convertir a float y escribir con máxima precisión
                        mx = float(valores[0])
                        my = float(valores[1])
                        mz = float(valores[2])
                        # Escribir en formato de referencia
                        f_out.write(f"{mx:f}\t{my:f}\t{mz:f}\n")
                    except ValueError:
                        print(f"Línea ignorada: {linea}")
    
    print(f"Archivo convertido: {input_file} -> {output_file}")

# Usar la función
if __name__ == "__main__":
    convertir_archivo("/home/rel/Descargas/mag_read.txt", "mag_read_converted.txt")