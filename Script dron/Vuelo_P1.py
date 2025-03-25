print ('INICIO')

for chan in range(1,9):
    Script.SendRC(chan,1500,False)
    Script.SendRC(3,1000,True)

#Script.ChangeMode('Stabilize')
Script.SendRC(5,1000,True)
print ('Modo:', cs.mode)
# Armar motores
print('Armando motores...')
#MAV.doARM(True)
Script.Sleep(3000)
print('ARMADO')

print('Despegando...')
Script.SendRC(3,1600,True)
while cs.alt < 0.08:
    print cs.alt
    Script.Sleep(100)
print('DESPEGO')

print 'volando'
#Script.ChangeMode('Alt Hold')
Script.SendRC(5,1600,True)
print ('Modo:', cs.mode)
# Se mantiene 5 segundos
Script.Sleep(5000)

print('aterrizando...')
#Script.ChangeMode('Land')
Script.SendRC(5,1200,True)
print ('Modo:', cs.mode)
Script.Sleep(5000)
print('ATERRIZO')

print('apagando...')
Script.SendRC(3,1000,True)
Script.Sleep(5000)

print('FIN')