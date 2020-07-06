import numpy as np
import csv
from scipy import stats
from scipy import signal
from scipy import integrate
import matplotlib.pyplot as plt


# Problem 1

# Bits and number of bits
N = input("Enter number of bits (min 50): ")
N = int(N)
bits = [0]*N

# Get bits from csv
bits = np.genfromtxt('bits10k.csv', delimiter=',')
bits = bits.astype(int)

# Operational frequency
f = 5000 

# Period
T = 1/f 

# Number of samplings
p = 80

# Points per period
tp = np.linspace(0, T, p)

# sin(2piftp)
sin = np.sin(2*np.pi * f * tp)

# sin waveform
plt.plot(tp, sin)
plt.xlabel('Tiempo / s')
plt.savefig("images/wave.png")

# Sampling frequency
fs = p/T 

# Tx linspace
t = np.linspace(0, N*T, N*p)

# initiate signal
sign = np.zeros(t.shape)

# BPSK modulated signal
for k, b in enumerate(bits):
    if b == 1:
        sign[k*p:(k+1)*p] = sin
    else:
        sign[k*p:(k+1)*p] = -sin    

# Visualización de los primeros bits modulados
pb = 10
plt.figure()
plt.plot(sign[0:pb*p]) 
plt.savefig("images/Tx.png")




# Problem 2 

# Instant power
Pinst = sign**2

# Medium power
Ps = integrate.trapz(Pinst, t) / (N * T)
print("Medium power: ", Ps, ' W')




# Problem 3

# get SNR lower and upper limit, then call function get_noise
SNR_L = input("Enter SNR lower limit: ")
SNR_U = input("Enter SNR upper limit: ")
iterate = int(SNR_U) - int(SNR_L)
Rx_list = [[]*N for i in range(iterate + 1)]

# get_noise: Function that plots first 10 bits of sign + noise for each SNR 
def get_noise(iterate, SNR_L, Rx_list):
    SNR = int(SNR_L)
    for i in range(iterate + 1):
        Pn = Ps / (10**(SNR / 10))                          # Noise and given sign's power
        sigma = np.sqrt(Pn)                                 # Noise's standard dev
        ruido = np.random.normal(0, sigma, sign.shape)
        Rx_list[SNR] = sign + ruido                       # Channel 
        pb = 10
        plt.figure()
        plt.title('Senal con ruido blanco, con SNR: '+ str(SNR))
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Amplitud')
        plt.plot(Rx_list[SNR][0:pb*p])
        plt.savefig("images/Rx" + str(SNR) + '.png')              # plots first 10 bits of signal + noise
        SNR += 1

get_noise(iterate, SNR_L, Rx_list)


# Problem 4

# Before noise
fw, PSD = signal.welch(sign, fs, nperseg=1024)
plt.figure()
plt.semilogy(fw, PSD)
plt.title('Senal modulada sin ruido')
plt.xlabel('Frecuencia / kHz')
plt.ylabel('Densidad espectral de potencia / V**2/kHz')
plt.savefig("images/welch_pre_noise.png")


# Post noise
SNR_W = int(SNR_L)
for i in range(iterate + 1):   
    fw, PSD = signal.welch(Rx_list[i], fs, nperseg=1024)
    plt.figure()
    plt.semilogy(fw, PSD)
    plt.title('Senal despues del canal ruidoso, con SNR: '+ str(SNR_W))
    plt.xlabel('Frecuencia / kHz')
    plt.ylabel('Densidad espectral de potencia / V**2/kHz')
    plt.savefig("images/welch" + str(SNR_W) + '.png')
    SNR_W += 1



# Problem 5

BER_V = []
# Pseudo-energy from the original wave
Es = np.sum(sin**2)

# Initiate bit vector with zeros
bitsRx = np.zeros(bits.shape)

# Signal decodification by energy detection
SNR_F = int(SNR_L)
for i in range(iterate + 1):
    for k, b in enumerate(bits):
    # Producto interno de dos funciones
        Ep = np.sum(Rx_list[i][k*p:(k+1)*p] * sin) 
        if Ep > Es/2:
            bitsRx[k] = 1
        else:
            bitsRx[k] = 0
    err = np.sum(np.abs(bits - bitsRx))
    BER = err/N
    BER_V.append(BER)
    print('There are {} errors within {} bits with a SNR of {}dB for an error rate of {}%'.format(err, N, SNR_F, BER))
    SNR_F += 1



# Problem 6

# SNR_V list contains SNR values
SNR_V = [*range(int(SNR_L), int(SNR_U) + 1, 1)]
plt.figure()
plt.scatter(SNR_V, BER_V)
plt.xlabel('SRN(dB)')
plt.ylabel('Ber') 
plt.grid(axis='y', alpha=0.75)  
plt.title('Error rate')
plt.savefig("images/BERvSRN.png")