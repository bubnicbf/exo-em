from scipy.constants import epsilon_0
from scipy.constants import mu_0
import matplotlib.pyplot as plt
#import matplotlib.colors as colors
import numpy as np
#from SimPEG.Utils import ndgrid, mkvc
from ipywidgets import *
from JSAnimation import IPython_display, HTMLWriter
from matplotlib import animation

#Evaluate k wavenumber
kwave = lambda mu,sig,eps,f: np.sqrt(mu*mu_0*eps*epsilon_0*(2.*np.pi*f)**2.-1.j*mu*mu_0*sig*2.*np.pi*f)

#Define a frquency range for a survey
frange = lambda minfreq, maxfreq, step: np.logspace(minfreq,maxfreq,num = step, base = 10.)

#Functions to create random n-layered earth with physical properties
thick = lambda minthick, maxthick, nlayer: np.append(np.array([1.2*10.**5]), 
                                                     np.ndarray.round(minthick + (maxthick-minthick)* np.random.rand(nlayer-1,1)
                                                            ,decimals =1))

sig = lambda minsig, maxsig, nlayer: np.append(np.array([0.]), 
                                               np.ndarray.round(10.**minsig + (10.**maxsig-10.**minsig)* np.random.rand(nlayer,1)
                                                      ,decimals=3))

mu  = lambda minmu, maxmu, nlayer: np.append(np.array([1.]), 
                                             np.ndarray.round(minmu + (maxmu-minmu)* np.random.rand(nlayer,1)
                                                    ,decimals=1))

eps = lambda mineps, maxeps, nlayer: np.append(np.array([1.]), 
                                               np.ndarray.round(mineps + (maxeps-mineps)* np.random.rand(nlayer,1)
                                                                ,decimals=1))

#Evaluate Effective Conductivity
sighat = lambda sig,eps,f: sig - 1.j*eps*epsilon_0*2.*np.pi*f

#Evaluate wavelength
wavelength = lambda k: 2.*np.pi/np.real(k)


#Evaluate Impedance Z of a layer
ImpZ = lambda f, mu, k: 2.*np.pi*f*mu*mu_0/k

#Complex Cole-Cole Conductivity
PCC= lambda siginf,m,t,c,f: siginf*(1.-(m/(1.+(1.j*2.*np.pi*f*t)**c)))


#Converted thickness array into top of layer array
def top(thick):
    topv= np.zeros(len(thick)+1)
    
    topv[0]=-thick[0]

    for i in range(1,len(topv),1):
        topv[i] = topv[i-1] + thick[i-1]
    
    return topv

#Propagation Matrix
def PropagationMatrixUD(z1,z2,h,k): 
    
    tran = np.matrix([[np.exp(-1.j*k*h),0.],[0.,np.exp(-1.j*k*h)]],dtype='complex_')
    
    prop2 = np.matrix([[1.,1,],[-1./z2,1./z2]],dtype='complex_')
    
    prop1_1 = np.matrix([[1.,-z1],[1.,z1]],dtype='complex_')/2.
    
    PropMatUD = tran*prop1_1*prop2
    
    return PropMatUD

transi = lambda h,k: np.matrix([[np.exp(-1.j*k*h),0.],[0.,np.exp(1.j*k*h)]],dtype='complex_')

transi_1 = lambda h,k: np.matrix([[np.exp(1.j*k*h),0.],[0.,np.exp(-1.j*k*h)]],dtype='complex_')

prop = lambda z: np.matrix([[1.,1,],[-1./z,1./z]],dtype='complex_')

propinv = lambda z: np.matrix([[1.,-z],[1.,z]],dtype='complex_')/2.

UD_Z = lambda UD,z,zj,k : transi_1((z-zj),k)*UD

#Time Variation of E and H
E_ZT = lambda U,D,f,t : np.exp(1.j*2*np.pi*f*t)*(U+D)
H_ZT = lambda U,D,Z,f,t : (1./Z)*np.exp(1.j*2*np.pi*f*t)*(D-U)

#Plot the configuration of the problem
def PlotConfiguration(thick,sig,eps,mu,ax,widthg,z):
    
    topn = top(thick)
    widthn = np.arange(-widthg,widthg+widthg/10.,widthg/10.)
    
    ax.set_ylim([z.min(),z.max()])
    ax.set_xlim([-widthg,widthg])
    
    ax.set_ylabel("Depth (m)", fontsize=16.)
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")
    
    hatches=['/'  , '+', 'x', '|' , '\\', '-'  , 'o' , 'O' , '.' , '*' ] 
    
    ax.annotate(("Air, $\sigma$ =%1.0f mS/m")%(sig[0]*10**(3)),
            xy=(-widthg/2., -np.abs(z.max())/2.), xycoords='data',
            xytext=(-widthg/2., -np.abs(z.max())/2.), textcoords='data',
            fontsize=14.)
    
    ax.annotate(("$\epsilon_r$= %1i")%(eps[0]),
            xy=(-widthg/2., -np.abs(z.max())/3.), xycoords='data',
            xytext=(-widthg/2., -np.abs(z.max())/3.), textcoords='data',
            fontsize=14.)
    
    ax.annotate(("$\mu_r$= %1i")%(mu[0]),
            xy=(-widthg/2., -np.abs(z.max())/3.), xycoords='data',
            xytext=(0, -np.abs(z.max())/3.), textcoords='data',
            fontsize=14.)
    
    #ax.set_title(('Time = % ns')%(sig[1]*1e9), fontsize = 16)

    
    for i in range(1,len(topn)-1,1):
        if topn[i] == topn[i+1]:
            pass
        else:
            ax.annotate(("$\sigma$ =%3.3f mS/m")%(sig[i]*10**(3)),
                xy=(0., (2.*topn[i]+topn[i+1])/3), xycoords='data',
                xytext=(0., (2.*topn[i]+topn[i+1])/3), textcoords='data',
                fontsize=14.)
    
            ax.annotate(("$\epsilon_r$= %1i")%(eps[i]),
                xy=(-widthg/1.1, (2.*topn[i]+topn[i+1])/3), xycoords='data',
                xytext=(-widthg/1.1, (2.*topn[i]+topn[i+1])/3), textcoords='data',
                fontsize=14.)
    
            ax.annotate(("$\mu_r$= %1.2f")%(mu[i]),
                xy=(-widthg/2., (2.*topn[i]+topn[i+1])/3), xycoords='data',
                xytext=(-widthg/2., (2.*topn[i]+topn[i+1])/3), textcoords='data',
                fontsize=14.)
        
            ax.plot(widthn,topn[i]*np.ones_like(widthn),color='black')    
            ax.fill_between(widthn,topn[i],topn[i+1],alpha=0.3,color="none",edgecolor='black', hatch=hatches[(i-1)%10])
        
        #ax.annotate(("Layer, $\sigma$ = %10.0f S/m")%(sig[0]),
        #    xy=(widthg/2., -np.abs(z.max())/2.), xycoords='data',
        #    xytext=(widthg/2., -np.abs(z.max())/2.), textcoords='data',
        #    fontsize=16.)
        
    ax.plot(widthn,topn[-1]*np.ones_like(widthn),color='black')    
    ax.fill_between(widthn,topn[-1],z.max(),alpha=0.3,color="none",edgecolor='black', hatch=hatches[(len(topn)-2)%10])
    
    ax.annotate(("$\sigma$ =%3.3f mS/m")%(sig[-1]*10**(3)),
            xy=(0., (2.*topn[-1]+z.max())/3), xycoords='data',
            xytext=(0., (2.*topn[-1]+z.max())/3), textcoords='data',
            fontsize=14.)
    
    ax.annotate(("$\epsilon_r$= %1i")%(eps[-1]),
            xy=(-widthg/1.1, (2.*topn[-1]+z.max())/3), xycoords='data',
            xytext=(-widthg/1.1, (2.*topn[-1]+z.max())/3), textcoords='data',
            fontsize=14.)
    
    ax.annotate(("$\mu_r$= %1.2f")%(mu[-1]),
            xy=(-widthg/2., (2.*topn[-1]+z.max())/3), xycoords='data',
            xytext=(-widthg/2., (2.*topn[-1]+z.max())/3), textcoords='data',
            fontsize=14.)
    
    ax.annotate("",
            xy=(widthg/2., -1.*z.max()/5.), xycoords='data',
            xytext=(widthg/2., 0.), textcoords='data',
            arrowprops=dict(arrowstyle='->, head_width=1.2,head_length=1.2',color='green',linewidth=2.)
            )

    ax.annotate("",
            xy=(widthg/2., -3./4.*z.max()/5.), xycoords='data',
            xytext=(widthg/2., 0.), textcoords='data',
            arrowprops=dict(arrowstyle='->, head_width=1.4,head_length=1.4',color='green',linewidth=2.)
            )

    ax.annotate("",
            xy=(widthg/2., -1./2.*z.max()/5.), xycoords='data',
            xytext=(widthg/2., 0.), textcoords='data',
            arrowprops=dict(arrowstyle='->, head_width=1.6,head_length=1.6',color='green',linewidth=2.)
            )
    
    ax.annotate("",
            xy=(1.2*widthg/2., -1.*z.max()/5.), xycoords='data',
            xytext=(1.2*widthg/2., 0.), textcoords='data',
            arrowprops=dict(arrowstyle='->, head_width=1.2,head_length=1.2',color='green',linewidth=2.)
            )

    ax.annotate("",
            xy=(1.2*widthg/2., -3./4.*z.max()/5.), xycoords='data',
            xytext=(1.2*widthg/2., 0.), textcoords='data',
            arrowprops=dict(arrowstyle='->, head_width=1.4,head_length=1.4',color='green',linewidth=2.)
            )

    ax.annotate("",
            xy=(1.2*widthg/2., -1./2.*z.max()/5.), xycoords='data',
            xytext=(1.2*widthg/2., 0.), textcoords='data',
            arrowprops=dict(arrowstyle='->, head_width=1.6,head_length=1.6',color='green',linewidth=2.)
            )
    
    ax.annotate("",
            xy=(1.5*widthg/2., -1.*z.max()/5.), xycoords='data',
            xytext=(1.5*widthg/2., 0.), textcoords='data',
            arrowprops=dict(arrowstyle='->, head_width=1.2,head_length=1.2',color='green',linewidth=2.)
            )

    ax.annotate("",
            xy=(1.5*widthg/2., -3./4.*z.max()/5.), xycoords='data',
            xytext=(1.5*widthg/2., 0.), textcoords='data',
            arrowprops=dict(arrowstyle='->, head_width=1.4,head_length=1.4',color='green',linewidth=2.)
            )

    ax.annotate("",
            xy=(1.5*widthg/2., -1./2.*z.max()/5.), xycoords='data',
            xytext=(1.5*widthg/2., 0.), textcoords='data',
            arrowprops=dict(arrowstyle='->, head_width=1.6,head_length=1.6',color='green',linewidth=2.)
            )

    
    ax.invert_yaxis()

    return ax

#Plot the general N layer case
def PlotLayer(thick,ax,widthg,z):
    
    topn = top(thick)
    widthn = np.arange(-widthg,widthg+widthg/10.,widthg/10.)
    
    ax.set_ylim([z.min(),z.max()])
    ax.set_xlim([widthn.min(),widthn.max()])
    
    hatches=['/'  , '+', 'x', '|' , '\\', '-'  , 'o' , 'O' , '.' , '*' ] 
    
    ax.annotate(("Air,  $\sigma$=0 mS/m,  $\epsilon_r$=1,  $\mu_r$=1"),
            xy=(-widthg/1.5, -np.abs(z.max())/4.), xycoords='data',
            xytext=(-widthg/1.5, -np.abs(z.max())/4.), textcoords='data',
            fontsize=20.)
    
    #ax.set_title(('Time = % ns')%(sig[1]*1e9), fontsize = 16)

    ax.get_yaxis().set_ticks([])
    ax.get_xaxis().set_ticks([])
    
    ax.axis('off')
    
    for i in range(1,len(topn)-2,1):
        
        ax.annotate("",
            xy=(-widthg, topn[i]), xycoords='data',
            xytext=(-widthg,topn[i+1]), textcoords='data',
            arrowprops=dict(arrowstyle='<->',color='black',linewidth=2.))
        
        ax.annotate(("$h_%1i$")%((i)),
            xy=(-widthg,(topn[i]+topn[i+1])/2), xycoords='data',
            xytext=(-widthg,(topn[i]+topn[i+1])/2), textcoords='data',
            fontsize=24.)
        
        ax.annotate(("$z_%1i$")%((i-1)),
            xy=(widthg,topn[i]), xycoords='data',
            xytext=(widthg,topn[i]), textcoords='data',
            fontsize=24.)
        
        ax.annotate(("$\sigma_%1i$")%(i),
            xy=(0., (topn[i]+topn[i+1])/2), xycoords='data',
            xytext=(0., (topn[i]+topn[i+1])/2), textcoords='data',
            fontsize=24.)
    
        ax.annotate(("$\epsilon_%1i$")%(i),
            xy=(-widthg/1.5, (topn[i]+topn[i+1])/2), xycoords='data',
            xytext=(-widthg/1.5, (topn[i]+topn[i+1])/2), textcoords='data',
            fontsize=24.)
    
        ax.annotate(("$\mu_%1i$")%(i),
            xy=(-widthg/2., (topn[i]+topn[i+1])/2), xycoords='data',
            xytext=(-widthg/2., (topn[i]+topn[i+1])/2), textcoords='data',
            fontsize=24.)
        
        ax.annotate(("Layer %1i")%(i),
            xy=(widthg/2., (topn[i]+topn[i+1])/2), xycoords='data',
            xytext=(widthg/2., (topn[i]+topn[i+1])/2), textcoords='data',
            fontsize=20.)
        
        ax.plot(widthn,topn[i]*np.ones_like(widthn),color='black')    
        ax.fill_between(widthn,topn[i],topn[i+1],alpha=0.3,color="none",edgecolor='black', hatch=hatches[(i-1)%10])
        
        
    ax.annotate(("....."),
            xy=(0,(topn[-2]+topn[-2+1])/2), xycoords='data',
            xytext=(0,(topn[-2]+topn[-2+1])/2), textcoords='data',
            fontsize=32.)
    
    ax.plot(widthn,topn[-2]*np.ones_like(widthn),color='black')    
    ax.fill_between(widthn,topn[-2],topn[-1],alpha=0.3,color="none",edgecolor='black', hatch=hatches[(len(topn)-1)%10])
        
    ax.plot(widthn,topn[-1]*np.ones_like(widthn),color='black')    
    ax.fill_between(widthn,topn[-1],z.max(),alpha=0.3,color="none",edgecolor='black', hatch=hatches[(len(topn)-2)%10])
    
    ax.annotate("",
            xy=(-widthg, topn[-1]), xycoords='data',
            xytext=(-widthg,z.max()), textcoords='data',
            arrowprops=dict(arrowstyle='->',color='black',linewidth=2.))
        
    ax.annotate(("$\infty$"),
            xy=(-widthg,(topn[-1]+z.max())/2), xycoords='data',
            xytext=(-widthg,(topn[-1]+z.max())/2), textcoords='data',
            fontsize=24.)
    
    ax.annotate(("$z_{n-1}$"),
            xy=(widthg,topn[-1]), xycoords='data',
            xytext=(widthg,topn[-1]), textcoords='data',
            fontsize=24.)
    
    ax.annotate(("Layer n"),
            xy=(widthg/2., (topn[-1]+z.max())/2), xycoords='data',
            xytext=(widthg/2., (topn[-1]+z.max())/2), textcoords='data',
            fontsize=24.)
    
    ax.annotate(("$\sigma_n$"),
            xy=(0., (topn[-1]+z.max())/2), xycoords='data',
            xytext=(0., (topn[-1]+z.max())/2), textcoords='data',
            fontsize=24.)
    
    ax.annotate(("$\epsilon_n$"),
            xy=(-widthg/1.5, (topn[-1]+z.max())/2), xycoords='data',
            xytext=(-widthg/1.5, (topn[-1]+z.max())/2), textcoords='data',
            fontsize=24.)
    
    ax.annotate(("$\mu_n$"),
            xy=(-widthg/2., (topn[-1]+z.max())/2), xycoords='data',
            xytext=(-widthg/2., (topn[-1]+z.max())/2), textcoords='data',
            fontsize=20.)
    
    ax.annotate("",
            xy=(widthg/2., -1.*z.max()/5.), xycoords='data',
            xytext=(widthg/2., 0.), textcoords='data',
            arrowprops=dict(arrowstyle='->, head_width=1.2,head_length=1.2',color='green',linewidth=2.)
            )

    ax.annotate("",
            xy=(widthg/2., -3./4.*z.max()/5.), xycoords='data',
            xytext=(widthg/2., 0.), textcoords='data',
            arrowprops=dict(arrowstyle='->, head_width=1.4,head_length=1.4',color='green',linewidth=2.)
            )

    ax.annotate("",
            xy=(widthg/2., -1./2.*z.max()/5.), xycoords='data',
            xytext=(widthg/2., 0.), textcoords='data',
            arrowprops=dict(arrowstyle='->, head_width=1.6,head_length=1.6',color='green',linewidth=2.)
            )
    
    ax.annotate("",
            xy=(1.2*widthg/2., -1.*z.max()/5.), xycoords='data',
            xytext=(1.2*widthg/2., 0.), textcoords='data',
            arrowprops=dict(arrowstyle='->, head_width=1.2,head_length=1.2',color='green',linewidth=2.)
            )

    ax.annotate("",
            xy=(1.2*widthg/2., -3./4.*z.max()/5.), xycoords='data',
            xytext=(1.2*widthg/2., 0.), textcoords='data',
            arrowprops=dict(arrowstyle='->, head_width=1.4,head_length=1.4',color='green',linewidth=2.)
            )

    ax.annotate("",
            xy=(1.2*widthg/2., -1./2.*z.max()/5.), xycoords='data',
            xytext=(1.2*widthg/2., 0.), textcoords='data',
            arrowprops=dict(arrowstyle='->, head_width=1.6,head_length=1.6',color='green',linewidth=2.)
            )
    
    ax.annotate("",
            xy=(1.5*widthg/2., -1.*z.max()/5.), xycoords='data',
            xytext=(1.5*widthg/2., 0.), textcoords='data',
            arrowprops=dict(arrowstyle='->, head_width=1.2,head_length=1.2',color='green',linewidth=2.)
            )

    ax.annotate("",
            xy=(1.5*widthg/2., -3./4.*z.max()/5.), xycoords='data',
            xytext=(1.5*widthg/2., 0.), textcoords='data',
            arrowprops=dict(arrowstyle='->, head_width=1.4,head_length=1.4',color='green',linewidth=2.)
            )

    ax.annotate("",
            xy=(1.5*widthg/2., -1./2.*z.max()/5.), xycoords='data',
            xytext=(1.5*widthg/2., 0.), textcoords='data',
            arrowprops=dict(arrowstyle='->, head_width=1.6,head_length=1.6',color='green',linewidth=2.)
            )

    
    ax.invert_yaxis()

    return ax

#Propagate Up and Down component for a certain frequency & evaluate E and H field
def Propagate(f,H,sig,chg,taux,c,mu,eps,n):
   
    sigcm = np.zeros_like(sig,dtype='complex_')
    
    for j in range(1,len(sig)):
        sigcm[j]=PCC(sig[j],chg[j],taux[j],c[j],f)
    
    K = kwave(mu,sigcm,eps,f)
    Z = ImpZ(f,mu,K)
    
    EH = np.matrix(np.zeros((2,n+1),dtype = 'complex_'),dtype = 'complex_')
    UD = np.matrix(np.zeros((2,n+1),dtype = 'complex_'),dtype = 'complex_')

    UD[1,-1] = 1.
    
    for i in range(-2,-(n+2),-1):
        
        UD[:,i] = transi(H[i+1],K[i])*propinv(Z[i])*prop(Z[i+1])*UD[:,i+1]
        UD = UD/((np.abs(UD[0,:]+UD[1,:])).max())
    
    for j in range(0,n+1):  
        EH[:,j] = np.matrix([[1.,1,],[-1./Z[j],1./Z[j]]])*UD[:,j]

    return UD, EH, Z ,K
    

#Evaluate the apparent resistivity and phase for a frequency range
def appres(F,H,sig,chg,taux,c,mu,eps,n):
    
    Res = np.zeros_like(F)
    Phase = np.zeros_like(F)
    App_ImpZ= np.zeros_like(F,dtype='complex_')
    
    for i in range(0,len(F)):
        
        UD,EH,Z ,K = Propagate(F[i],H,sig,chg,taux,c,mu,eps,n)
        
        App_ImpZ[i] = EH[0,1]/EH[1,1]
        
        Res[i] = np.abs(App_ImpZ[i])**2./(mu_0*2.*np.pi*F[i])
        Phase[i] = np.angle(App_ImpZ[i], deg = True)
        
    return Res,Phase

#Evaluate Up, Down components, E and H field, for a frequency range, 
#a discretized depth range and a time range (Movie)  
def calculateEHzt(F,H,sig,chg,taux,c,mu,eps,n,zsample,tsample):
    
    topc = top(H)
        
    layer = np.zeros(len(zsample),dtype=np.int)-1
    
    Exzt = np.matrix(np.zeros((len(zsample),len(tsample)),dtype = 'complex_'),dtype = 'complex_')
    Hyzt = np.matrix(np.zeros((len(zsample),len(tsample)),dtype = 'complex_'),dtype = 'complex_')
    Uz = np.matrix(np.zeros((len(zsample),len(tsample)),dtype = 'complex_'),dtype = 'complex_')
    Dz = np.matrix(np.zeros((len(zsample),len(tsample)),dtype = 'complex_'),dtype = 'complex_')
    UDaux = np.matrix(np.zeros((2,len(zsample)),dtype = 'complex_'),dtype = 'complex_')
    
    for i in range(0,n+1,1):
        layer = layer+(zsample>=topc[i])*1
        
    for j in range(0,len(F)):
        
        UD,EH,Z ,K = Propagate(F[j],H,sig,chg,taux,c,mu,eps,n)
        
        for p in range(0,len(zsample)):
            
            UDaux[:,p] = UD_Z(UD[:,layer[p]],zsample[p],topc[layer[p]],K[layer[p]])
            
            for q in range(0,len(tsample)):
                
                Exzt[p,q]  = Exzt[p,q] + E_ZT(UDaux[0,p],UDaux[1,p],F[j],tsample[q])/len(F)
                Hyzt[p,q] = Hyzt[p,q] + H_ZT(UDaux[0,p],UDaux[1,p],Z[layer[p]],F[j],tsample[q])/len(F)
                Uz[p,q] = Uz[p,q] + UDaux[0,p]*np.exp(1.j*2*np.pi*F[j]*tsample[q])/len(F)
                Dz[p,q] = Dz[p,q] + UDaux[1,p]*np.exp(1.j*2*np.pi*F[j]*tsample[q])/len(F)
    
    return  Exzt,Hyzt,Uz,Dz,UDaux,layer
    

#Function to Plot Apparent Resistivity and Phase
def PlotAppRes(F,H,sig,chg,taux,c,mu,eps,n,fenv,envelope):

    Res, Phase = appres(F,H,sig,chg,taux,c,mu,eps,n)

    fig,ax = plt.subplots(1,2,figsize=(16,10))

    ax[0].scatter(Res,F,color='black')
    ax[0].set_xscale('Log')
    ax[0].set_yscale('Log')
    ax[0].set_xlim([10.**(np.log10(Res.min())-1.),10.**(np.log10(Res.max())+1.)])
    ax[0].set_ylim([F.min(),F.max()])
    ax[0].set_xlabel('Apparent Resistivity (Ohm*m)',fontsize=16.,color="black")
    ax[0].set_ylabel('Frequency (Hz)',fontsize=16.)
    ax[0].grid(which='major')

    ax0 = ax[0].twiny()
    
    ax0.set_xlim([0.,90.])
    ax0.set_ylim([F.min(),F.max()])
    ax0.scatter(Phase,F,color='purple')
    #ax[1].set_yscale('Log')
    #ax[1].grid(which='major')
    ax0.set_xlabel('Phase (Degrees)',fontsize=16.,color="purple")
    #ax[1].set_ylabel('Frequency (Hz)')
    
    zc=np.arange(-(H[1:].max()+10)*n,(H[1:].max()+10)*n,10.)
    
    ax[0].tick_params(labelsize=16)
    ax[1].tick_params(labelsize=16)
    ax0.tick_params(labelsize=16)
    
    if envelope == 1:
        
        fenvelope = F[fenv]
        widthn=np.logspace(np.log10(Res.min())-1., np.log10(Res.max())+1., num=100, endpoint=True, base=10.0)
        fenvelope1n=np.ones(100)*fenvelope
        ax[0].plot(widthn,fenvelope1n,linestyle='dashed',color='black')
        
        tc=np.arange(0.,1./fenvelope,0.01/(fenvelope))
        Exzt,Hyzt,Uz,Dz,UDaux,layer = calculateEHzt(np.array([fenvelope]),H,sig,chg,taux,c,mu,eps,n,zc,tc)
        
        ax1=ax[1].twiny()
        
        ax[1].tick_params(labelsize=16)
        ax1.tick_params(labelsize=16)

        ax[1].set_xlabel('Amplitude Electric Field E (V/m)',color='blue',fontsize=16)

        ax1.set_xlabel('Amplitude Magnetic Field H (A/m)',color='red',fontsize=16)
        
        #ax1.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
        
        ax[1].fill_betweenx(zc,np.squeeze(np.asarray(np.real(Exzt.min(axis=1)))),
                      np.squeeze(np.asarray(np.real(Exzt.max(axis=1)))), 
                      color='blue', alpha=0.1)

        ax1.fill_betweenx(zc,np.squeeze(np.asarray(np.real(Hyzt.min(axis=1)))),
                      np.squeeze(np.asarray(np.real(Hyzt.max(axis=1)))), 
                      color='red', alpha=0.1)
       
        ax[1] = PlotConfiguration(H,sig,eps,mu,ax[1],(1.5*np.abs(Exzt).max()),zc)
        ax1.set_xlim([-1.5*np.abs(Hyzt).max(),1.5*np.abs(Hyzt).max()])
        #ax1.plot(np.zeros(2), np.r_[-30, 20])
        ax1.set_xlim([-1.5*np.abs(Hyzt).max(),1.5*np.abs(Hyzt).max()])
    else:
        print 'No envelop (if True, might be slow)'
        ax[1] = PlotConfiguration(H,sig,eps,mu,ax[1],1.,zc)
        ax[1].get_xaxis().set_ticks([])
    
    plt.tight_layout()
    plt.show()

#Interactive MT for Notebook
def PlotAppRes3LayersInteract(h1,h2,sigl1,sigl2,sigl3,mul1,mul2,mul3,epsl1,epsl2,epsl3,fenvelope,envelope):
    
    frangn=frange(-5,5,100.)
    sig3= np.array([0.,0.001,0.1, 0.001])
    thick3 = np.array([120000.,50.,50.])
    eps3=np.array([1.,1.,1.,1])
    mu3=np.array([1.,1.,1.,1])
    chg3=np.array([0.,0.1,0.,0.2])
    chg3_0=np.array([0.,0.1,0.,0.])
    taux3=np.array([0.,0.1,0.,0.1])
    c3=np.array([1.,1.,1.,1.])
    
    sig3[1]=sigl1
    sig3[1]=10.**sig3[1]
    sig3[2]=sigl2
    sig3[2]=10.**sig3[2]
    sig3[3]=sigl3
    sig3[3]=10.**sig3[3]
    mu3[1]=mul1
    mu3[2]=mul2
    mu3[3]=mul3
    eps3[1]=epsl1
    eps3[2]=epsl2
    eps3[3]=epsl3
    thick3[1]=h1
    thick3[2]=h2
    
    PlotAppRes(frangn,thick3,sig3,chg3_0,taux3,c3,mu3,eps3,3,fenvelope,envelope)
    

    
       
    
    


