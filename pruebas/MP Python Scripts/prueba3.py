print ('Start Script')
for chan in range(1,9):
    Script.SendRC(chan,1500,False)
    Script.SendRC(3,1000,True)

Script.ChangeMode('Stabilize')
#Script.SendRC(3,1000,False)

print('Armar motores')
MAV.doARM(True)
print('Armando')
Script.WaitFor('ARMING MOTORS',3000)

print('Motores armados')

print('subiendo')
Script.SendRC(3,1700,True)
Script.Sleep(5000)
Script.SendRC(3,1500,True)
Script.Sleep(1000)
if False:
    print('elevando nariz')
    Script.SendRC(2,1700,True)
    Script.Sleep(3000)
    Script.SendRC(2,1500,True)
    Script.Sleep(2000)

    print('Inclinando')
    Script.SendRC(1,1700,True)
    Script.Sleep(3000)
    Script.SendRC(1,1500,True)
    Script.Sleep(2000)

    print('rotando')
    Script.SendRC(4,1700,True)
    Script.Sleep(3000)
    Script.SendRC(4,1500,True)
    Script.Sleep(2000)

print('bajando')
Script.SendRC(3,1500,True)
Script.Sleep(1000)
Script.SendRC(3,1300,True)
Script.Sleep(2000)

print('apagando...')
Script.SendRC(3,1000,True)
Script.WaitFor('DISARMING MOTORS',5000)
print('fin')