# ESTA MAL
print('hola')
Script.ChangeMode('Stabilize')
#Script.ChangeMode('Auto')
print('Modo',cs.wpno,cs.mode)
print('altura',cs.alt)
MAV.doARM(True)
print('espera armado')
#Script.WaitFor(ARMING ,5000)}
Script.Sleep(3000)
print("se armo?",cs.armed)
if cs. armed is True:
    Script.SendRC(3,2000,True)
    Script.Sleep(5000)
    Script.SendRC(3,1000,True)
MAV.doARM(False)
#Script.WaitFor('DISARMING MOTORS')
print('fin')