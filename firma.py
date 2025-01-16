import numpy as np
import sys
from complementary import highbits, lowbits, hashing, modpm, decompose, inf

MAX_INT = sys.maxsize
q = 2**23 - 2**13 + 1
n = np.random.randint(5, 15)
gamma1 = 104659
gamma2 = q//3

def keygen(n, m, q):
  A = np.random.randint(MAX_INT, size=(n, m)) % 119
  A = A%q

  s1 = np.random.randint(MAX_INT, size=(m, 1)) % 119
  s2 = np.random.randint(MAX_INT, size=(n, 1)) % 119

  t = (np.matmul(A, s1) + s2) % q

  pk = (t, A)
  sk = (t, A, s1, s2)

  return pk, sk

pk, sk = keygen(n, n, q)
print(pk)

def sign(sk, M):
  t = sk[0]
  A = sk[1]
  s1 = sk[2]
  s2 = sk[3]

  [n, m] = A.shape

  y = np.random.randint(MAX_INT, size=(n, 1)) % (gamma1 - 1)
  Ay = int(max(np.matmul(A, y)))

  w_1 = highbits(Ay, gamma1, q)

  c = hashing(M, w_1)
  z = y + c*s1

  sigma = (z, c)

  a = int(inf(c*s1))
  b = int(inf(c*s2))
  print("a=",a)
  print("b=",b)
  beta = int(max(a,b))

  if (inf(z) >= (gamma1 - beta)) or (lowbits(Ay - b, 2*gamma2, q) >= (gamma2 - beta)):
    sigma, beta = sign(sk, M)
    
  return sigma, beta

sigma, beta = sign(sk, "Mensaje a firmar")
print(sigma, beta)

def verify(pk, M, sigma, beta):
  t = pk[0]
  A = pk[1]

  z = sigma[0]
  c = sigma[1]

  Az = inf(np.matmul(A, z))
  ct = inf(c*t)
  print("Az=",Az)
  print("ct=",ct)
  print("Az-ct=",Az - ct)
  print("2*gamma2=",2*gamma2)
  print("Q=",q)
  print("Az -ct", Az - ct)
  w1 = highbits(Az - ct, 2*gamma2, q)
  
  return inf(z) < (gamma1 - beta) and c == hashing(M, w1)

print(verify(pk, "Mensaje a firmar", sigma, beta))