#!/usr/bin/env python
# coding: utf-8


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random as random
from casadi import *
from pdfo import *
import dataframe_image as dfi



n = 500
taux = 1/n
T= linspace(0,1,n)




def tracer_orientation (x,y,theta, r, i):
    if i == 1 :
        plt.arrow(x, y, r*cos(theta),r*sin(theta), width = 0.01, color = 'red' , label = "Axe local suivant x")
        plt.arrow(x, y, r*cos(pi/2+theta),r*sin(pi/2+theta), width = 0.01, color = 'yellow' , label = "Axe local suivant y")
        plt.legend()
    else :
        plt.arrow(x, y, r*cos(theta),r*sin(theta), width = 0.01, color = 'red' )
        plt.arrow(x, y, r*cos(pi/2+theta),r*sin(pi/2+theta), width = 0.01, color = 'yellow' )
 



def MH_DOC (c1,c2,c3,c4, Xi,Xf):
    x0 = Xi[0]
    y0 = Xi[1]
    theta0 = Xi[2]
    
    xf = Xf[0]
    yf = Xf[1]
    thetaf = Xf[2]
    
    opti = casadi.Opti()   # cette fonction nous permet de trouver la solution de problème

    ## les positions
    x = opti.variable(n)
    y = opti.variable(n)
    theta = opti.variable(n)

    ## les vitesses 
    v1 = opti.variable(n)        ## vitesse latérale
    v2 = opti.variable(n)        ## vitesse orthogonal
    w = opti.variable(n)         ## vitesse angulaire


    ## les accélération 
    u1 = opti.variable(n)        ## accélération latérale
    u3 = opti.variable(n)        ## accélération orthogonal
    u2 = opti.variable(n)        ## accélération angulaire


    opti.minimize(  taux*( dot(c1 *u1,u1) +  dot(c2 *u2,u2 ) + dot(c3 *  u3 ,u3 ) + dot(c4 *  (theta-thetaf) ,theta-thetaf ) ) )    # ma fonction objetion

        # mes fonctions de contrainte d'égalité:

    ## pour les condition initial
    opti.subject_to( x[0] == x0 + 10**(-4))       
    opti.subject_to( y[0] == y0 + 10**(-4))    
    opti.subject_to( theta[0] == theta0 + 10**(-4))


    opti.subject_to( v1[0] == 0.0001 )
    opti.subject_to( w[0] == 0.0001 )
    opti.subject_to( v2[0] == 0.0001 )
    opti.subject_to( v1[-1] == 0.0001 )
    opti.subject_to( w[-1] == 0.0001 )
    opti.subject_to( v2[-1] == 0.0001 )

    opti.subject_to( u1[-1] == 0.0001 )
    opti.subject_to( u2[-1] == 0.0001 )
    opti.subject_to( u3[-1] == 0.0001 )

    opti.subject_to( u1[0] == 0.0001 )
    opti.subject_to( u2[0] == 0.0001 )
    opti.subject_to( u3[0] == 0.0001 )



        ## pour les contraintes d'égaliter
    opti.subject_to( x[1:] + 10**(-4) == x[:n-1]+taux*(cos(theta[:n-1])*v1[:n-1] - sin(theta[:n-1])*v2[:n-1]) )
    opti.subject_to( y[1:] + 10**(-4) == y[:n-1]+taux*(sin(theta[:n-1])*v1[:n-1] + cos(theta[:n-1])*v2[:n-1]) )
    opti.subject_to( theta[1:] + 10**(-4) == theta[:n-1] + taux*w[:n-1] )
    opti.subject_to( (v1[:n-1] + taux* u1[:n-1] == v1[1:] + 10**(-4))  )
    opti.subject_to( (v2[:n-1] + taux* u3[:n-1] == v2[1:] + 10**(-4)) )
    opti.subject_to( (w[:n-1] + taux* u2[:n-1] == w[1:] + 10**(-4)) )


        ## pour les conditions finales
    opti.subject_to( x[-1]==xf + 10**(-4))
    opti.subject_to( y[-1]==yf + 10**(-4))
    opti.subject_to( theta[-1]==thetaf + 10**(-4))


    opti.solver('ipopt')      # suivant la méthode de KKT

    sol = opti.solve()
    
    return sol.value(x),sol.value(y),sol.value(theta)
    



xi = SX.sym('xi',1)                   
yi = SX.sym('yi',1)                
thetai = SX.sym('thetai',1)


xf = SX.sym('xf',1)
yf = SX.sym('yf',1)
thetaf = SX.sym('thetaf',1)


A = SX.sym('A',6)
B = SX.sym('B',6)
C = SX.sym('C',6)
D = SX.sym('D',6)


## Position
x=SX.sym('x',n)
x_prime = SX.sym('x_prime', n+1)
x_prime[0] = x[0]
x_prime[1:] =x


y=SX.sym('y',n)
y_prime = SX.sym('y_prime', n+1)
y_prime[0] = y[0]
y_prime[1:] =y

theta=SX.sym('theta',n)
theta_prime = SX.sym('theta_prime', n+1)
theta_prime[0] = theta[0]
theta_prime[1:] =theta


## Vitesse
v1=SX.sym('v1',n)  
v1_prime = SX.sym('v1_prime', n+1)
v1_prime[0] = 0
v1_prime[n] = 0
v1_prime[1:n] =v1[0:n-1]

v1_prime_1 = SX.sym('v1_prime_1', n+1)
v1_prime_1[0] = v1[0]
v1_prime_1[1:] =v1


v2=SX.sym('v2',n)  
v2_prime = SX.sym('v2_prime', n+1)
v2_prime[0] = 0
v2_prime[n] = 0
v2_prime[1:n] =v2[0:n-1]

v2_prime_1 = SX.sym('v2_prime_1', n+1)
v2_prime_1[0] = v2[0]
v2_prime_1[1:] =v2


w=SX.sym('w',n)  
w_prime = SX.sym('w_prime', n+1)
w_prime[0] = 0
w_prime[n] = 0
w_prime[1:n] =w[0:n-1]

w_prime_1 = SX.sym('w_prime_1', n+1)
w_prime_1[0] = w[0]
w_prime_1[1:] =w


## Accélération 

u1=SX.sym('u1',n)  
u1_prime = SX.sym('u1_prime', n+1)
u1_prime[0] = 0
u1_prime[n] = 0
u1_prime[1:n] = u1[0:n-1]

u2=SX.sym('u2',n)  
u2_prime = SX.sym('u2_prime', n+1)
u2_prime[0] = 0
u2_prime[n] = 0
u2_prime[1:n] = u2[0:n-1]

u3=SX.sym('u3',n)  
u3_prime = SX.sym('u3_prime', n+1)
u3_prime[0] = 0
u3_prime[n] = 0
u3_prime[1:n] = u3[0:n-1]

Lambda = SX.sym('Lambda',n+2, 6)




c1 = A[0]* (T**0) + A[1]* (T**1) + A[2]* (T**2) + A[3]* (T**3) + A[4]* (T**4) + A[5]* (T**5) 
c2 = B[0]* (T**0) + B[1]* (T**1) + B[2]* (T**2) + B[3]* (T**3) + B[4]* (T**4) + B[5]* (T**5) 
c3 = C[0]* (T**0) + C[1]* (T**1) + C[2]* (T**2) + C[3]* (T**3) + C[4]* (T**4) + C[5]* (T**5) 
c4 = D[0]* (T**0) + D[1]* (T**1) + D[2]* (T**2) + D[3]* (T**3) + D[4]* (T**4) + D[5]* (T**5) 



p1=vertcat(xi + 10**(-4),x_prime[2:] + 10**(-4),xf + 10**(-4))   
h= Function('h',[x, xi, xf],[p1])

p2=vertcat(0, v1)   
K = Function('K', [v1], [p2])

p =vertcat(v1[1:],0)
g = Function ('g',[v1],[p])

Y1_K = (x_prime+taux*(v1_prime*cos(theta_prime) - v2_prime*sin(theta_prime)) - h(x, xi,xf))
Y2_K = (y_prime+taux*(v1_prime*sin(theta_prime) + v2_prime*cos(theta_prime)) - h(y, yi,yf)) 
Y3_K = (theta_prime+taux*w_prime - h(theta, thetai,thetaf))

Y4_K = (vertcat(0,v1[1:],v1[-1]) - vertcat(-v1[0],v1[:-1],0))/taux - vertcat(0,u1[:-1],0) 
Y5_K = (vertcat(0,w[1:],w[-1]) - vertcat(-w[0],w[:-1],0))/taux - vertcat(0,u2[:-1],0)
Y6_K = (vertcat(0,v2[1:],v2[-1]) - vertcat(-v2[0],v2[:-1],0))/taux - vertcat(0,u3[:-1],0)



Y_K = SX.sym('Y_K',n+1 , 6)        ## notre contrainte

for i in range (0,n+1):
    Y_K[i,0]= Y1_K[i]
    Y_K[i,1]= Y2_K[i]
    Y_K[i,2]= Y3_K[i]       
    Y_K[i,3]= Y4_K[i]       
    Y_K[i,4]= Y5_K[i]       
    Y_K[i,5]= Y6_K[i]       
    
## notre terme qui est relié a la contrainte.
G_lambda = 0

for i in range (n+1):
    G_lambda += dot(Y_K[i,:], Lambda[i,:])
    
G_lambda += (u1[0])*Lambda[n+1,0] + (u2[0])*Lambda[n+1,1] + (u3[0])*Lambda[n+1,2] 
G_lambda += (u1[-1])*Lambda[n+1,3] + (u2[-1])*Lambda[n+1,4] + (u3[-1])*Lambda[n+1,5] 


F_val_K =  taux*(  dot(c1 *u1,u1) +  dot(c2 *u2,u2) +  dot(c3*u3,u3) +  dot(c4*(theta-thetaf),(theta-thetaf)))

## le Lagrangien 
L_val_K = F_val_K + G_lambda




grad_L_K = SX.zeros(9, n)
for i in range (n):
    grad_L_K[0,i]= jacobian(L_val_K, v1[i])
    grad_L_K[1,i]= jacobian(L_val_K, w[i])
    grad_L_K[2,i]= jacobian(L_val_K, v2[i])
    grad_L_K[3,i]= jacobian(L_val_K, x[i])
    grad_L_K[4,i]= jacobian(L_val_K, y[i])
    grad_L_K[5,i]= jacobian(L_val_K, theta[i])
    grad_L_K[6,i]= jacobian(L_val_K, u1[i])
    grad_L_K[7,i]= jacobian(L_val_K, u2[i])
    grad_L_K[8,i]= jacobian(L_val_K, u3[i])
    
    
    
R_K = Function ('R_K', [u1,u2,u3,v1,w,v2,x,y,theta, Lambda, A, B, C,D ,xi,yi,thetai, xf,yf,thetaf  ], [dot(grad_L_K,grad_L_K)])
    



def MH_IOC (X,Y,Theta,V1,W,V2,U1,U2,U3):
    opti = casadi.Opti()   # cette fonction nous permet de trouver la solution de problème


    A = opti.variable(6)
    B = opti.variable(6)
    C = opti.variable(6)
    D = opti.variable(6)
    
    c1 = A[0]* (T**0) + A[1]* (T**1) + A[2]* (T**2) + A[3]* (T**3) + A[4]* (T**4) + A[5]* (T**5) 
    c2 = B[0]* (T**0) + B[1]* (T**1) + B[2]* (T**2) + B[3]* (T**3) + B[4]* (T**4) + B[5]* (T**5) 
    c3 = C[0]* (T**0) + C[1]* (T**1) + C[2]* (T**2) + C[3]* (T**3) + C[4]* (T**4) + C[5]* (T**5) 
    c4 = D[0]* (T**0) + D[1]* (T**1) + D[2]* (T**2) + D[3]* (T**3) + D[4]* (T**4) + D[5]* (T**5) 
    

    Lambda = opti.variable(n+3,6)


    opti.minimize( R_K(U1, U2, U3,V1,W,V2,X,Y,Theta, Lambda, A,B,C,D, X[0],Y[0],Theta[0], X[-1],Y[-1],Theta[-1] )) 
    
    for j in range(n):

        opti.subject_to( 0 <= c1[j] )

        opti.subject_to( 0 <= c2[j] )

        opti.subject_to( 0 <= c3[j] )
        
        opti.subject_to( 0 <= c4[j] )
        

        opti.subject_to(  c1[j] + c2[j] + c3[j] + c4[j] == 1)

    opti.solver('ipopt')    

    sol = opti.solve()
    
    return sol.value(A),sol.value(B),sol.value(C),sol.value(D)




X1=SX.sym('X1',n)
X2=SX.sym('X2',n)  
X3=SX.sym('X3',n)  


m = SX.sym('m',1)
m = (dot(X1-x,X1-x) + dot(X2-y,X2-y) + dot(X3-theta,X3-theta))

M = Function ('M', [x,y,theta, X1,X2,X3], [m])




def MH_BL1 (X,Y,THETA,V1,W,V2,U1,U2,U3):
    opti = casadi.Opti()   # cette fonction nous permet de trouver la solution de problème

    ## les positions
    x = opti.variable(n)
    y = opti.variable(n)
    theta = opti.variable(n)

    ## les vitesses 
    v1 = opti.variable(n)  
    v2 = opti.variable(n)        
    w = opti.variable(n)         


    ## les accélération 
    u1 = opti.variable(n)        
    u3 = opti.variable(n)       
    u2 = opti.variable(n)       

    A = opti.variable(6)
    B = opti.variable(6)
    C = opti.variable(6)
    D = opti.variable(6)
    
    c1 = A[0]* (T**0) + A[1]* (T**1) + A[2]* (T**2) + A[3]* (T**3) + A[4]* (T**4) + A[5]* (T**5) 
    c2 = B[0]* (T**0) + B[1]* (T**1) + B[2]* (T**2) + B[3]* (T**3) + B[4]* (T**4) + B[5]* (T**5) 
    c3 = C[0]* (T**0) + C[1]* (T**1) + C[2]* (T**2) + C[3]* (T**3) + C[4]* (T**4) + C[5]* (T**5)
    c4 = D[0]* (T**0) + D[1]* (T**1) + D[2]* (T**2) + D[3]* (T**3) + D[4]* (T**4) + D[5]* (T**5) 
    

    Lambda = opti.variable(n+3,6)


    opti.minimize( 5*10**(2) *R_K(u1,u2,u3,v1,w,v2,x,y,theta, Lambda, A,B,C,D,  X[0],Y[0],THETA[0], X[-1],Y[-1],THETA[-1]) + M(x,y,theta, X,Y,THETA) ) 
    
    for j in range(n):

        opti.subject_to( 10**(-7) <= c1[j] )

        opti.subject_to( 10**(-7) <= c2[j] )

        opti.subject_to( 10**(-7) <= c3[j] )
        
        opti.subject_to( 10**(-7) <= c4[j] )
        

        opti.subject_to(  c1[j] + c2[j] + c3[j] + c4[j] == 1)
        
    opti.subject_to( x[0] == X[0] + 10**(-4))        
    opti.subject_to( y[0] == Y[0] + 10**(-4))
    opti.subject_to( theta[0] == THETA[0] + 10**(-4))
    
    opti.subject_to( v1[0] == 0.0001 )
    opti.subject_to( w[0]  == 0.0001 )
    opti.subject_to( v2[0] == 0.0001 )
    opti.subject_to( v1[-1] == 0.0001 )
    opti.subject_to( w[-1]  == 0.0001 )
    opti.subject_to( v2[-1] == 0.0001 )
        
    opti.subject_to( u1[-1] == 0.0001 )
    opti.subject_to( u2[-1] == 0.0001 )
    opti.subject_to( u3[-1] == 0.0001 )
    opti.subject_to( u1[0] == 0.0001 )
    opti.subject_to( u2[0] == 0.0001 )
    opti.subject_to( u3[0] == 0.0001 )



    ## pour les contraintes d'égaliter
    #opti.subject_to(  R_K(u1,u2,u3,v1,w,v2,x,y,theta, Lambda, A,B,C,D,  X[0],Y[0],THETA[0], X[-1],Y[-1],THETA[-1]) <= 10**(-6))
    opti.subject_to( x[1:] + 10**(-4) == x[:n-1]+taux*(cos(theta[:n-1])*v1[:n-1] - sin(theta[:n-1])*v2[:n-1]) )
    opti.subject_to( y[1:] + 10**(-4) == y[:n-1]+taux*(sin(theta[:n-1])*v1[:n-1] + cos(theta[:n-1])*v2[:n-1]) )
    opti.subject_to( theta[1:]  + 10**(-4) == theta[:n-1] + taux*w[:n-1] )
    opti.subject_to( (v1[:n-1] + taux* u1[:n-1] == v1[1:] + 10**(-4))  )
    opti.subject_to( (v2[:n-1] + taux* u3[:n-1] == v2[1:] + 10**(-4)) )
    opti.subject_to( (w[:n-1] + taux* u2[:n-1] == w[1:] + 10**(-4)) )


        ## pour les conditions finales
    opti.subject_to( x[-1]==X[-1] + 10**(-4))
    opti.subject_to( y[-1]==Y[-1] + 10**(-4))
    opti.subject_to( theta[-1]==THETA[-1] + 10**(-4))
    
    
    opti.set_initial(u1, U1)
    opti.set_initial(u2, U2)
    opti.set_initial(u3, U3)
    opti.set_initial(v1, V1)
    opti.set_initial(w, W)
    opti.set_initial(v2, V2)
    opti.set_initial(x, X)
    opti.set_initial(y, Y)
    opti.set_initial(theta, THETA)

    opti.solver('ipopt')    

    sol = opti.solve()
    
    return sol.value(A),sol.value(B),sol.value(C),sol.value(D), sol.value(x), sol.value(y), sol.value(theta)



options = {'maxfev': 10000 , 'rhobeg' : 0.1 , 'rhoend' : 1e-8}


Lin_const = []

for i in range(n):
    Lin_const.append(LinearConstraint([1, T[i], (T**2)[i],(T**3)[i],(T**4)[i],(T**5)[i],1, T[i], (T**2)[i],(T**3)[i],(T**4)[i],(T**5)[i],1, T[i], (T**2)[i],(T**3)[i],(T**4)[i],(T**5)[i],1, T[i], (T**2)[i],(T**3)[i],(T**4)[i],(T**5)[i]], 1, 1))
    Lin_const.append(LinearConstraint([0, 0,0,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,1, T[i], (T**2)[i],(T**3)[i],(T**4)[i],(T**5)[i]], 0, 1))    
    Lin_const.append(LinearConstraint([0, 0,0,0,0,0,0, 0,0,0,0,0,1, T[i], (T**2)[i],(T**3)[i],(T**4)[i],(T**5)[i],0, 0,0,0,0,0], 0, 1))    
    Lin_const.append(LinearConstraint([0, 0,0,0,0,0,1, T[i], (T**2)[i],(T**3)[i],(T**4)[i],(T**5)[i],0, 0,0,0,0,0,0, 0,0,0,0,0], 0, 1))    
    Lin_const.append(LinearConstraint([1, T[i], (T**2)[i],(T**3)[i],(T**4)[i],(T**5)[i],0,0,0,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0], 0, 1))    



def MH_PDFO (C):
    [A0,A1,A2,A3,A4,A5,B0,B1,B2,B3,B4,B5,C0,C1,C2,C3,C4,C5,D0,D1,D2,D3,D4,D5] = C
    c1 = A0* (T**0) + A1* (T**1) + A2* (T**2) + A3* (T**3) + A4* (T**4) + A5* (T**5) 
    c2 = B0* (T**0) + B1* (T**1) + B2* (T**2) + B3* (T**3) + B4* (T**4) + B5* (T**5)
    c3 = C0* (T**0) + C1* (T**1) + C2* (T**2) + C3* (T**3) + C4* (T**4) + C5* (T**5)
    c4 = D0* (T**0) + D1* (T**1) + D2* (T**2) + D3* (T**3) + D4* (T**4) + D5* (T**5)
     
    print(C)
    
    mk = 0
    
    for j in range (c1.shape[0]):
        if c1[j] < 0 :
            c1[j] = - c1[j] 
            mk = mk - c1[j] 
        if c2[j] < 0 :
            c2[j] = - c2[j]
            mk = mk - c2[j] 
        if c3[j] < 0 :
            c3[j] = - c3[j]
            mk = mk - c3[j] 
        if c4[j] < 0 :
            c4[j] = - c4[j]
            mk = mk - c4[j]             
            
    opti = casadi.Opti()   # cette fonction nous permet de trouver la solution de problème

    ## les positions
    x = opti.variable(n)
    y = opti.variable(n)
    theta = opti.variable(n)

    ## les vitesses 
    v1 = opti.variable(n)        ## vitesse latérale
    v2 = opti.variable(n)        ## vitesse orthogonal
    w = opti.variable(n)         ## vitesse angulaire


    ## les accélération 
    u1 = opti.variable(n)        ## accélération latérale
    u3 = opti.variable(n)        ## accélération orthogonal
    u2 = opti.variable(n)        ## accélération angulaire


    opti.minimize(  taux*( dot(c1 *u1,u1) +  dot(c2 *u2,u2 ) + dot(c3 *u3 ,u3 ) + dot(c4 *(theta-Theta_moy[-1]) ,theta-Theta_moy[-1] ) ) )   

        # mes fonctions de contrainte d'égalité:

    ## pour les condition initial
    opti.subject_to( x[0] == Xmoy[0] + 10**(-4))       
    opti.subject_to( y[0] == Ymoy[0] + 10**(-4))    
    opti.subject_to( theta[0] == Theta_moy[0] + 10**(-4))


    opti.subject_to( v1[0] == 0.0001 )
    opti.subject_to( w[0] == 0.0001 )
    opti.subject_to( v2[0] == 0.0001 )
    opti.subject_to( v1[-1] == 0.0001 )
    opti.subject_to( w[-1] == 0.0001 )
    opti.subject_to( v2[-1] == 0.0001 )

    opti.subject_to( u1[-1] == 0.0001 )
    opti.subject_to( u2[-1] == 0.0001 )
    opti.subject_to( u3[-1] == 0.0001 )

    opti.subject_to( u1[0] == 0.0001 )
    opti.subject_to( u2[0] == 0.0001 )
    opti.subject_to( u3[0] == 0.0001 )



        ## pour les contraintes d'égaliter
    opti.subject_to( x[1:] + 10**(-4) == x[:n-1]+taux*(cos(theta[:n-1])*v1[:n-1] - sin(theta[:n-1])*v2[:n-1]) )
    opti.subject_to( y[1:] + 10**(-4) == y[:n-1]+taux*(sin(theta[:n-1])*v1[:n-1] + cos(theta[:n-1])*v2[:n-1]) )
    opti.subject_to( theta[1:] + 10**(-4) == theta[:n-1] + taux*w[:n-1] )
    opti.subject_to( (v1[:n-1] + taux* u1[:n-1] == v1[1:] + 10**(-4))  )
    opti.subject_to( (v2[:n-1] + taux* u3[:n-1] == v2[1:] + 10**(-4)) )
    opti.subject_to( (w[:n-1] + taux* u2[:n-1] == w[1:] + 10**(-4)) )


        ## pour les conditions finales
    opti.subject_to( x[-1]==Xmoy[-1] + 10**(-4))
    opti.subject_to( y[-1]==Ymoy[-1] + 10**(-4))
    opti.subject_to( theta[-1]==Theta_moy[-1] + 10**(-4))


    opti.solver('ipopt')

    sol = opti.solve()
    
    X1_1 = sol.value(x)
    X2_1 = sol.value(y)
    X3_1 = sol.value(theta)
    
    
    m01 = sqrt((np.linalg.norm(Xmoy-X1_1)**2 + np.linalg.norm(Ymoy-X2_1)**2 + np.linalg.norm(Theta_moy-X3_1)**2 )/n)
    
    m02 = 10*abs(np.sum(c1 + c2 + c3 + c4) - n)
    
    m03 = 10* mk
    
    m1 = m01+m02+m03
    
    return float(m1)
