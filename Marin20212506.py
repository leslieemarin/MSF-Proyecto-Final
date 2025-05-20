"""
Proyecto Final

Departamento de Ingeniería Eléctrica y Electrónica, Ingeniería Biomédica
Tecnológico Nacional de México [TecNM - Tijuana]
Blvd. Alberto Limón Padilla s/n, C.P. 22454, Tijuana, B.C., México

Nombre del alumno: Marin Paredes Leslie Avelladith
Número de control: 20212506
Correo institucional: l20212506@tectijuana.edu.mx

Asignatura: Modelado de Sistemas Fisiológicos
Docente: Dr. Paul Antonio Valle Trujillo; paul.valle@tectijuana.edu.mx
"""
# Instalar librerias en consola
#!pip install control
#!pip install slycot

# Librerías para cálculo numérico y generación de gráficas
import numpy as np
import matplotlib.pyplot as plt
import control as ctrl

# Datos de la simulación
x0,t0,tend,dt,w,h = 0,0,20,1E-3,6,3
N = round((tend-t0)/dt) + 1 #veces de solucion numerica, numeros enteros
t = np.linspace(t0,tend,N) #linea de tiempo de 0,10
u1 = np.where(t >= 0, 1.0, 0.0) # Escalón unitario
u2= np.where((t >= 0) & (t <= 4), 1.0, 0.0)  # Pulso de 2 a 4 segundos

#arreglo de todas las señales
u = np.stack((u1,u2), axis=1) 
signal=['Herida Leve','Herida Severa']

# Parámetros: Herida leve
Re_leve, Rt_leve = 5E3, 2E3
Ce_leve, Ct_leve = 10E-6, 50E-6

# Parámetros: Herida severa
Re_severa, Rt_severa = 20E3, 15E3
Ce_severa, Ct_severa = 100E-6, 220E-6

def sys_TPN(Re,Ce,Rt,Ct):

# Componentes del circuito RLC y función de transferencia

    a2 = Re * Rt * Ce * Ct
    a1 = Ct * Re + Ct * Rt + Ce * Re
    a0 = 1

#funcion de transferencia viene con denominador y numerador
    num = [1] #sacado de la funcion PA(S)/Pao(S) = -->1<-- / CLS^2+RCS+1
    den = [a2,a1,a0] #S2, S, CONSTANTE si fuera cubica sería S3, S2, S, CONSTANTE 1 / --> CLS^2+RCS+1 <--

#aplicacion de la funcion de transferencia
    sys = ctrl.tf(num,den)
    return sys #despliegue de funcion de transferencia

# Funcion de transferencia: Individuo saludable [control]
sysL = sys_TPN(Re_leve, Ce_leve, Rt_leve, Ct_leve)
print('Herida Leve [control]:')
print(sysL)

# Funcion de transferencia: Individuo enfermo [caso]
sysS = sys_TPN(Re_severa, Ce_severa, Rt_severa, Ct_severa)
print('Herida Severa [caso]:')
print(sysS)

def plotsignals(u,sysL,sysS,sysPID,signal):
    
    fig = plt.figure() #1era figura codigo basado en page 87 Inicializa la figura
    plt.plot(t,u,'-',color=[0.7,0.3,0.9],label = '$P_{ao}(t)$') #Grafica la entrada
    
    # P A C I E N T E     S A N O       [ F I G U R A ]
    ts,Vs =ctrl.forced_response(sysL,t,u,x0)
    plt.plot(t,Vs,'-',color = [0.1,0.3,0.9],
             label='$P_A(t): Control$')
    
    # P A C I E N T E     E N F E R M O       [ F I G U R A ]
    ts, Ve = ctrl.forced_response(sysS,t,u,x0)
    plt.plot(t,Ve,'-',color = [0.3,0.8,0.8],
             label='$P_A(t):Caso$')
    
    # C O N T R O L     P I D      [ F I G U R A ]
    ts,pid = ctrl.forced_response(sysPID,t,Vs,x0)
    # plt.plot(t,u3,'-', linewidth=3, color = [0.8,0.3,0.6], label = 'Ve(t)' ) 
    plt.plot(t,pid,':', linewidth=3, color = [0.9,0.7,0.9], 
             label= '$VPID(t): Tratamiento$')
    
    plt.grid(False)
    plt.xlim(0,20)
    plt.ylim(-0.2,1.2)
    plt.xticks(np.arange(0, 21, 1))
    plt.yticks(np.arange(-0.2, 1.3, 0.1))
    plt.xlabel('$t$ [s]')
    plt.ylabel('$V(t)$ [V]')
    plt.legend(bbox_to_anchor = (0.5,-0.3), loc = 'center', ncol=4,
               fontsize = 8, frameon = False)
    plt.show()
    
    ## Almacenamiento de figura 
    fig.set_size_inches(w,h)
    fig.tight_layout()
    namepng = 'python_' + signal + '.png'
    namepdf = 'python_' + signal + '.pdf'
    fig.savefig(namepng, dpi = 600,bbox_inches = 'tight')
    fig.savefig(namepdf, bbox_inches = 'tight')
    
def tratamiento(Cr, Re,Rr,Ce,sysE):
    numPID = [Re*Rr*Ce*Cr,Re*Ce+Rr*Cr,1]
    denPID = [Re*Cr,0]
    PID = ctrl.tf(numPID,denPID)
    X = ctrl.series(PID,sysE)
    sysPID = ctrl.feedback(X, 1, sign = -1) #Cierra el lazo, hace una comparativa 
    return sysPID
    
    # Controlador para tratamiento
    
Cr = 1E-6
kP = 721.1926
kI = 271.4443
kD =  425.7384
Re = 1 /(kI*Cr)
Rr = kP*Re
Ce = kD/Rr
    
sysPID = tratamiento(Cr, Re, Rr, Ce, sysS)
    
plotsignals(u1, sysL, sysS, sysPID, 'Herida Leve')
    
    # Controlador para la respiración anormal [taquipnea]
plotsignals(u2, sysL, sysS, sysPID, 'Herida Severa')



