import pandas as pd
import re

log_file = "/home/rodrigo/Descargas/02rosout01-10.log"
csv_file = "/home/rodrigo/Descargas/02rosout01-10.csv"

# Timestamp mínimo a partir del cual leer
min_timestamp = 11759352955.416252136

logs = []

# Patrón para tu log
pattern = re.compile(
    r'(\d+\.\d+)\s+'          # timestamp
    r'(\w+)\s+'               # level
    r'(\S+)\s+'               # node
    r'\[(.*?)\]\s+'           # archivo y línea
    r'\[topics: (.*?)\]\s+'   # topics
    r'(.*)'                   # mensaje completo
)

with open(log_file, 'r') as f:
    for line in f:
        match = pattern.match(line)
        if match:
            timestamp = float(match.group(1))
            if timestamp >= min_timestamp:   # solo logs posteriores
                level = match.group(2)
                node = match.group(3)
                file_line = match.group(4)
                topics = match.group(5)
                message = match.group(6)
                logs.append([timestamp, level, node, file_line, topics, message])

# Crear DataFrame
df = pd.DataFrame(logs, columns=["timestamp", "level", "node", "file_line", "topics", "message"])

# Guardar CSV
df.to_csv(csv_file, index=False)
print(f"Archivo CSV filtrado guardado como {csv_file}")