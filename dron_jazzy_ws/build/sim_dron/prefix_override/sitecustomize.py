import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/rodrigo/Documentos/Dron/dron_jazzy_ws/install/sim_dron'
