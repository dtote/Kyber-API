
import sympy
import random
import time
from hashlib import sha3_256, sha3_512, shake_128, shake_256
import os
from flask import Flask, request, jsonify
import json
import base64
import matplotlib.pyplot as plt

## Funciones auxiliares
def es_primo(n):
  """
  Función para comprobar si un número es primo
  """
  if n < 2:
    return False
  for i in range(2, int(n**0.5) + 1): # El 2 no se mete en el for pues su raíz aplicando int es 1 que +1 es 2 y por tanto no hace bucle y da True, como esperamos.
    if n % i == 0:
      return False
  return True

def bitrev(z,n):
  """
  Función para realizar la transformación bit-reversal de un entero i.
  Ejemplo: bitrev(3, 8) = 6 0b011 -> 0b110 = 6
  Se utiliza para mejorar la eficiencia de ciertos cálculos
  """
  # Calcular el logaritmo en base 2 de la longitud de la secuencia
  seq = [x for x in range(n)]
  m = n.bit_length() - 1
  # Inicializar la lista de salida
  out = [0] * n
  # Iterar sobre los elementos de la secuencia
  for i in range(n):
    # Calcular el índice con los bits invertidos
    j = int(bin(i)[2:].zfill(m)[::-1], 2)
    # Asignar el elemento al índice correspondiente
    out[j] = seq[i]

  return out[z]

def traspuesta(A):
  """
  Función para calcular la traspuesta de una matriz.
  Entendemos como matriz a una lista de lista, en la que cada lista corresponde a una fila de la matriz.
  """
  new_rows = [list(item) for item in zip(*A)]
  return new_rows

def bytes2bits(input_bytes):
    """
    Convierte los bytes a un array de bits.
    Se utiliza una notación en little-endian, es decir, el bit menos significativo es el primero.
    """
    bit_string = ''.join(format(byte, '08b')[::-1] for byte in input_bytes)
    return list(map(int, list(bit_string)))

def bits2bytes(s):
    """
    Convertimos un string de bits todo junto, (que se diferencia un byte cada 8 elementos seguidos), a bytes.
    """
    return bytes([int(s[i:i+8][::-1], 2) for i in range(0, len(s), 8)])

#Ejemplo:
print('La representacion en bits de [144,1] es:',bytes2bits([144,1]))
print('La representacion en bits de "100101110101011010011110" es: ',list(bits2bytes('100101110101011010011110')))

## Funciones de hash
def XOF(bytes32, a, b, length):
        """
        XOF: B* x B x B -> B*
        """
        input_bytes = bytes32 + a + b
        return shake_128(input_bytes).digest(length)

def H(input_bytes):
        """
        H: B* -> B^32
        """
        return sha3_256(input_bytes).digest()

def G(input_bytes):
        """
        G: B* -> B^32 x B^32
        """
        output = sha3_512(input_bytes).digest()
        return output[:32], output[32:]

def PRF(s, b, length):
        """
        PRF: B^32 x B -> B*
        """
        input_bytes = s + bytes([b])
        if len(input_bytes) != 33:
            raise ValueError(f"El input de bytes debe ser una lista de 32 bytes y un único byte.")
        return shake_256(input_bytes).digest(length)

def KDF(input_bytes, length):
     """
     KDF: B* -> B*
     """
     return shake_256(input_bytes).digest(length)

#Ejemplo de uso:
x = XOF(bytes([random.randint(0, 255) for _ in range(17)]),bytes([12]),bytes([78]),8)
print(list(x)) # Aquí los tamaños deben ser de: arbitrario,1,1. En el arbitrario escogemos 17 pero puede ser cualquiera.
x = H(bytes([random.randint(0, 255) for _ in range(27)])) # Aquí el tamaño es arbitrario, cogemos 27 pero puede ser cualquiera.
print(list(x))
x = G(bytes([random.randint(0, 255) for _ in range(18)])) # Aquí el tamaño es arbitrario, cogemos 18 pero puede ser cualquiera.
print(list(x))
x = PRF(bytes([random.randint(0, 255) for _ in range(32)]),45,10) # Aquí los tamaños deben ser de 32,1.
print(list(x))
x = KDF(bytes([random.randint(0, 255) for _ in range(32)]),22) # Aquí el tamaño es arbitrario, cogemos 22 pero puede ser cualquiera.
print(list(x))
# Función para encontrar elemento primitivo:
# Queremos hacer una trasnformada de 256 elementos (transformada discreta: elemento a elemento.), esto debido a que lo usaremos para la multiplicación de polinomios de grado x^n+1 con n=256.
# Ahora debemos comprobar que hay una 256-raíz primitiva de la unidad en Zq para ello se debe dar que n divida a q-1, es decir que exista un m natural tal que: q-1= m*n, es decir: q =m*n+1.
#Luego para asegurar la existencia de esta raíz primitiva q debe ser de la forma: m*256+1, como en nuestro caso: q= 3329 =  13*256+1 entonces estamos seguro que existe la raíz primitiva.
# Nota: La razón por la que n debe dividir a q es porque si es raíz de la unidad (ni si quiera primitiva) pongamos g de Zq, entonces por definicion g^n=1 y si esto ocurre debido a un resultado tiene que dividir a q-1.
# (Este resultado anterior es consecuencia de que si el orden del grupo es q entonces para todo g en el grupo G: g^(q-1)=1.

def primera_raiz_primitiva(n,q):
  # Comprobamos hipótesis.
  if es_primo(q) == False:
    print('Error: Debe tomarse q primo.')
    return None
  if (q-1)%n!=0:
    print('Error: Se busca un n tal que n divida a q-1.')
    return None

  # Iremos comprobando si g^n=1 y  g a otra potencia menor no es 1.
  raiz_primitiva=0 # Inicializamos, también con t.

  for g in range(2,q):
    t=0
    i=2 # Empezamos en i=2 pues elevado a 0 no cuenta y elevado a 1 si da 1 seria el elemento 1.
    while t!=1 and i<=n:
      t=pow(g,i,q)
      i=i+1
    if t==1 and i==n+1:
        raiz_primitiva=g
        return raiz_primitiva # Lo ponemos aquí para que pare el bucle una vez se de esto ya acabe.

# Ejemplos de la función primera_raiz_primitiva:
print(primera_raiz_primitiva(256,13*2**8+1)) # Este es para el número q primo de kyber 3329=13*2^8+1
print(primera_raiz_primitiva(256,6*(2**8)+1)) # Este debería dar error pues no es primo.
print(primera_raiz_primitiva(2,(2**2)+1)) # Este es Z5
print(primera_raiz_primitiva(512,13*2**8+1)) # Aquí vemos que no existe 512 raíz de la unidad para kyber.
print(primera_raiz_primitiva(2,(2**4)+1)) # este es Z17, este es buen ejemplo pues sabemos que en Zp los unicos g de Zp tal que g^2=1(modp) son 1 y -1, como descartamos el 1 siempre será -1 mod p= p-1 (mod p) la 2-raiz-primitivo, en este caso es 17-1=16

def NTT(a,q):
  """
  El output está en bitreverse.
  """
  n=len(a)
  phi= primera_raiz_primitiva(2*n,q)

  # Inicializamos para el while
  m = 1
  k = n//2

  while m<n:
    for i in range(0,m):
      j1= 2*i*k
      j2=j1+k-1
      S= phi**(bitrev(m+i,n))

      for j in range(j1,j2+1): #Butterfly operation
        u= a[j] # Estas dos copias son para que no reinicie el a[j] al utilizarlo en el cambio de a[j+t].
        v= a[j+k]

        a[j]= (u+S*v)%q
        a[j+k]=(u-S*v)%q

    m = 2*m # Para el while, vamos multiplicando por 2.
    k = k//2 # En el while, vamos dividiendo por 2.

  return a

def NTT_kyber(a):
  """
  Aquí no hay una 512-raiz prmitiva (en Zq).
  Simplemente aplicamos a la parte par e impar y juntamos pues
  si existe la 256-raiz primitiva (en Zq).
  El output está en bitreverse.
  """

  # Primero si el grado del polinomio es menor que 256
  # para aplicar NTT rellenamos con ceros pues no cambia el polinomio.
  if len(a)<256:
    a= a + [0] * (256-len(a))

  q=3329
  n=len(a)//2 # Ahora necesitamos nuestro n = 128 = 256/2.

  a_par = [coef for idx, coef in enumerate(a) if idx % 2 == 0]
  a_impar= [coef for idx, coef in enumerate(a) if idx % 2 != 0]

  a_par_ntt = NTT(a_par,q)
  a_impar_ntt = NTT(a_impar,q)

  # Juntamos la parte par e impar con sus correspondientes índices.
  a = [a_par_ntt[i//2] if i%2==0 else a_impar_ntt[(i-1)//2] for i in range(256)]

  return  a
def INTT(a,q):
  """
  Se toma de entrada unn polinomio en un orden bit-reverse
  y se devuelve en orden estándar.
  """
  n=len(a)
  phi= primera_raiz_primitiva(2*n,q)
  phi_inversa = pow(phi,2*n-1,q)

  # Inicializamos para el while
  m = n//2
  k = 1

  while m>=1:
    for i in range(0,m):
      j1= 2*i*k
      j2=j1+k-1
      S= phi_inversa**(bitrev(m+i,n))

      for j in range(j1,j2+1): #Butterfly operation
        u= a[j] # Estas dos copias son para que no reinicie el a[j] al utilizarlo en el cambio de a[j+t].
        v= a[j+k]

        a[j]= (u+v)%q
        a[j+k]=((u-v)*S)%q

    m= m//2 # Para el while, vamos multiplicando por 2.
    k= 2*k # En el while, vamos dividiendo por 2.

  # Multiplicamos el resultado por el inverso de n en q.
  n_inverso= pow(n,q-2,q) # Pues todo elemento de Zq a la q-1 es 1, luego el inverso se obtienen elevando a q-2.
  a=[(n_inverso*x)%q for x in a]
  return a

def INTT_kyber(a):
  """
  Aquí no hay una 512-raiz prmitiva (en Zq).
  Simplemente aplicamos a la parte par e impar y juntamos pues
  si existe la 256-raiz primitiva (en Zq).
  El input está en bitreverse-order y el otput en orden estándar.
  """

  # Primero si el grado del polinomio es menor que 256
  # para aplicar INTT rellenamos con ceros pues no cambia el polinomio.
  if len(a)<256:
    a= a + [0] * (256-len(a))

  q=3329
  n=len(a)//2 # Ahora necesitamos nuestro n = 128 = 256/2.

  a_par = [coef for idx, coef in enumerate(a) if idx % 2 == 0]
  a_impar= [coef for idx, coef in enumerate(a) if idx % 2 != 0]

  a_par_intt = INTT(a_par,q)
  a_impar_intt = INTT(a_impar,q)

  # Juntamos la parte par e impar con sus correspondientes índices.
  a = [a_par_intt[i//2] if i%2==0 else a_impar_intt[(i-1)//2] for i in range(256)]

  return  a
print(INTT(NTT([6,3,4,6,2,16,7,8,6,3,4,6,2,16,7,8],257),257)) # 257 es 2^8+1 y es primo.
print(INTT(NTT([6,3,4,6,2,16,7,8],17),17))

def KyberConvolution(p,g, pnttdomain = False , gnttdomain= False):
  """
  Función que nos dará la convolución para kyber sobre NTT, es decir la multiplicación optimizada de dos polinomios
  usando NTT e INTT.
  Esta será específica para kyber pues no existe una 512 raíz de la unidad, luego sus parámetros vienen ya impuestos
  por q=3329, n=256.
  """
  # Parámetros:
  q=3329
  n=256
  phi= 17 # Ya sabmeos que esta es la primera 256-raíz primitiva de Z3329.

  # Ahora si el grado de alguno de los polinomios es menor que 256
  # para aplicar NTT rellenamos con ceros pues no cambia el polinomio.
  if len(p)<n:
    p= p + [0] * (n-len(p))

  if len(g)<n:
    g= g + [0] * (n-len(g))

  # Ahora dividimos cada uno en su parte par e impar.
  p_par = [coef for idx, coef in enumerate(p) if idx % 2 == 0]
  p_impar = [coef for idx, coef in enumerate(p) if idx % 2 != 0]

  g_par = [coef for idx, coef in enumerate(g) if idx % 2 == 0]
  g_impar = [coef for idx, coef in enumerate(g) if idx % 2 != 0]

  if pnttdomain == False and gnttdomain == False: # Todavía no se ha aplicado o no lo consideramos en el dominio NTTa ninguno.

    # Aplicamos la ntt, intt (convolution) a estos polinomios.
    p_par_ntt = NTT(p_par,q)
    p_impar_ntt = NTT(p_impar,q)


    g_par_ntt = NTT(g_par,q)
    g_impar_ntt = NTT(g_impar,q)

    # Una vez realizado esto, ponemos cada uno transformado en una lista de polinomios de la forma: (p0+p1x,p2+p3x,...,p254+p255x)
    # Esto para hacer directamente la multiplicación punto a punto.
    # Para implementarlo, como lo tenemos separado basta ir indice a indice en los pares e impares a la vez.

    # Ahora para la multiplicación punto a punto usamos el desarrollo:
    # h2i=p2i*g2i+p2i+1*g2i+1*w^(2*br(i)+1)
    # h2i+1= p2i*g2i+1 +p2i+1*g2i

    # La idea es recorrer del 0 hasta 255 definiendo como lo escrito anterior de los hi, así el índice i//2 corresponde al índice que tiene p2i en la lista p_par y i-1//2 corresponde al índice que tiene p_impar en p_impar.
    point_wise_mult_par= [(p_par_ntt[i//2]*g_par_ntt[i//2]+p_impar_ntt[i//2]*g_impar_ntt[i//2]*(phi**(2*bitrev(i//2,n//2)+1)))%q for i in range(0,n,2)]
    point_wise_mult_impar=[(p_par_ntt[(i-1)//2]*g_impar_ntt[(i-1)//2]+p_impar_ntt[(i-1)//2]*g_par_ntt[(i-1)//2])%q for i in range(1,n,2)]

    #Aplicamos inversa a estos polinomios separados y los juntamos obteniendo la multiplicación de ellos.
    C_par = INTT(point_wise_mult_par,q)
    C_impar = INTT(point_wise_mult_impar,q)

    # Así juntando estos coeficientes pares e impares tenemos nuestro polinomio multiplicacion de p*g.
    p_mult_g =[C_par[i//2] if i%2==0 else C_impar[(i-1)//2] for i in range(256)]

  if pnttdomain == True and gnttdomain == True: # Aquí suponemos que ambos polinomios ya se les ha aplicado NTT o están en el dominio NTT, simplemente no aplicamnos NTT.
    # Lo pasaremos por INTT y por tanto debemos convertir a formato ordenado bitrev, en este caso al ser ambos True, pasamos ambos.

    point_wise_mult_par= [(p_par[i//2]*g_par[i//2]+p_impar[i//2]*g_impar[i//2]*(phi**(2*bitrev(i//2,n//2)+1)))%q for i in range(0,n,2)]
    point_wise_mult_impar=[(p_par[(i-1)//2]*g_impar[(i-1)//2]+p_impar[(i-1)//2]*g_par[(i-1)//2])%q for i in range(1,n,2)]

    #Aplicamos inversa a estos polinomios separados y los juntamos obteniendo la multiplicación de ellos.
    C_par = INTT(point_wise_mult_par,q)
    C_impar = INTT(point_wise_mult_impar,q)

    # Así juntando estos coeficientes pares e impares tenemos nuestro polinomio multiplicacion de p*g.
    p_mult_g =[C_par[i//2] if i%2==0 else C_impar[(i-1)//2] for i in range(256)]

  if pnttdomain == True and gnttdomain == False: # Solo p esta en el dominio NTT.

    # Aplicamos la ntt, intt (convolution) a g.
    g_par_ntt = NTT(g_par,q)
    g_impar_ntt = NTT(g_impar,q)

    point_wise_mult_par= [(p_par[i//2]*g_par_ntt[i//2]+p_impar[i//2]*g_impar_ntt[i//2]*(phi**(2*bitrev(i//2,n//2)+1)))%q for i in range(0,n,2)]
    point_wise_mult_impar=[(p_par[(i-1)//2]*g_impar_ntt[(i-1)//2]+p_impar[(i-1)//2]*g_par_ntt[(i-1)//2])%q for i in range(1,n,2)]

    #Aplicamos inversa a estos polinomios separados y los juntamos obteniendo la multiplicación de ellos.
    C_par = INTT(point_wise_mult_par,q)
    C_impar = INTT(point_wise_mult_impar,q)

    # Así juntando estos coeficientes pares e impares tenemos nuestro polinomio multiplicacion de p*g.
    p_mult_g =[C_par[i//2] if i%2==0 else C_impar[(i-1)//2] for i in range(256)]

  if pnttdomain == False and gnttdomain == True: # Solo g esta en el dominio NTT.

    # Aplicamos la ntt, intt (convolution) a p.
    p_par_ntt = NTT(p_par,q)
    p_impar_ntt = NTT(p_impar,q)

    point_wise_mult_par= [(p_par_ntt[i//2]*g_par[i//2]+p_impar_ntt[i//2]*g_impar[i//2]*(phi**(2*bitrev(i//2,n//2)+1)))%q for i in range(0,n,2)]
    point_wise_mult_impar=[(p_par_ntt[(i-1)//2]*g_impar[(i-1)//2]+p_impar_ntt[(i-1)//2]*g_par[(i-1)//2])%q for i in range(1,n,2)]

    #Aplicamos inversa a estos polinomios separados y los juntamos obteniendo la multiplicación de ellos.
    C_par = INTT(point_wise_mult_par,q)
    C_impar = INTT(point_wise_mult_impar,q)

    # Así juntando estos coeficientes pares e impares tenemos nuestro polinomio multiplicacion de p*g.
    p_mult_g =[C_par[i//2] if i%2==0 else C_impar[(i-1)//2] for i in range(256)]

  return p_mult_g

# Con los siguientes polinomios haremos el proceso de multiplicacion vía ntt.
p=[random.randint(0, 3329) for _ in range(256)] # Un polinomio aleatorio de tamaño 256 para comparar sympy con nuestra ntt. No hace falta reducir mod q pues el max es 256
g=[random.randint(0, 3329) for _ in range(256)] # Otro polinomio cualquiera de tamaño 256, se coge esa expresión para que sea distinto a p(x) simplemente, aquí el max es 6*256+3=1537<3329, no hace falra reducir.

p_mult_g= KyberConvolution(p,g)
print(p_mult_g)


def suma_pol(p,g):
  suma = [(a+b)%3329 for a,b in zip(p,g)]
  return suma

def sum_pols(v):
  """
  Sumaremos varios polinomios en vez de una dupla de ellos unicamente.
  """
  sum = v[0]
  for i in range(1,len(v)):
    sum = suma_pol(sum,v[i])
  return sum

def vector_sum(u,v):
  """
  Suma de dos vectores.
  """

  # Verificaciones:
  if len(u[0])!=len(v[0]):
    raise ValueError('Las dimensiones deben ser iguales.')

  for i in range(len(u)):
    for j in range(len(u[0])):
      if len(u[i][j])!=256:
        raise ValueError('Polinomios deben ser de tamaños 256.')

  # Codigo:
  new_elements = []
  for i in range(len(u)):
    new_elements.append([suma_pol(a,b) for a,b in zip(u[i], v[i])])
  return new_elements

def Matriz_mult_viaNTT(A, B, Anttdomain = False, Bnttdomain = False):
  """
  Multiplicación de una Matriz A y otra B utilizando mult punto a punto en polinomios.
  """
  new_elements = [[sum_pols([pointwise(a,b) for a,b in zip(A_row, B_col)]) for B_col in traspuesta(B)] for A_row in A]
  return new_elements

def pointwise(p,g):
  """
  Multiplicamos dos polinomios usando
  la multiplicación punto a punto en Zq[x]/(x^2-w^2br(i)+1)
  """
  # Parámetros:
  q=3329
  n=256
  phi= 17 # Ya sabemos que esta es la primera 256-raíz primitiva de Z3329.

  # Ahora si el grado de alguno de los polinomios es menor que 256
  # para aplicar NTT rellenamos con ceros pues no cambia el polinomio.
  if len(p)<n:
    p= p + [0] * (n-len(p))

  if len(g)<n:
    g= g + [0] * (n-len(g))

  p_par = [coef for idx, coef in enumerate(p) if idx % 2 == 0]
  p_impar = [coef for idx, coef in enumerate(p) if idx % 2 != 0]

  g_par = [coef for idx, coef in enumerate(g) if idx % 2 == 0]
  g_impar = [coef for idx, coef in enumerate(g) if idx % 2 != 0]

  point_wise_mult_par= [(p_par[i//2]*g_par[i//2]+p_impar[i//2]*g_impar[i//2]*(phi**(2*bitrev(i//2,n//2)+1)))%q for i in range(0,n,2)]
  point_wise_mult_impar=[(p_par[(i-1)//2]*g_impar[(i-1)//2]+p_impar[(i-1)//2]*g_par[(i-1)//2])%q for i in range(1,n,2)]
  pog =[point_wise_mult_par[i//2] if i%2==0 else point_wise_mult_impar[(i-1)//2] for i in range(256)]
  return pog

# Ejemplo de uso:
B = [[[1,2],[2,3]],[[3,4],[5,0]]]
v = [[[0,1]],[[1,0]]]
print(Matriz_mult_viaNTT(B,v))

def Parse(b):
  """
  Función para cambiar de representación entre bytes y coeficientes de Zq[x]. (Parse)
  Input: Conjunto de bytes arbitrario.
  Output: Coeficientes de Zq[x] que se interpretará como un elemento en el dominio NTT. (biyectivo)
  """
  i, j, n, q = 0, 0, 256, 3329
  a=n*[0] # Serán nuestros coeficientes de Zq.

  while j<n and i+3<len(b): #Por si el tamaño de bytes es pequeño.
    d1= b[i]+256*(b[i+1]%16)
    d2=(b[i+1]//16)+16*b[i+2]

    if d1<q:
      a[j]=d1
      j=j+1
    if d2<q and j<n:
      a[j]=d2
      j=j+1
    i=i+3
  return [int(elemento) for elemento in a]

# Ejemplo:
lista_parse= Parse(bytes([random.randint(0, 255) for _ in range(900)]))
print(lista_parse)

def CBD(input_bytes, eta):
        """
        Algoritmo 2 (Centered Binomial Distribution)
        https://pq-crystals.org/kyber/data/kyber-specification-round3-20210804.pdf

        Se espera un input_bytes de al menos 64*eta de longitud.
        """
        n=256
        assert (n >> 2)*eta == len(input_bytes)
        coefficients = [0 for _ in range(n)]
        list_of_bits = bytes2bits(input_bytes)
        for i in range(n):
            a = sum(list_of_bits[2*i*eta + j]       for j in range(eta))
            b = sum(list_of_bits[2*i*eta + eta + j] for j in range(eta))
            coefficients[i] = a-b
        return coefficients

# Ejemplo de uso:
print(CBD(bytes([random.randint(0, 255) for _ in range(64*2)]),2)) # Escogemos el tamaño minimo posible 64*eta.

def decode(input_bytes, l=None):
        """
        Decode (Algorithm 3)

        decode: B^32l -> R_q
        """
        n, q = 256,3329
        if l is None:
            l, r = divmod(8*len(input_bytes),n) # Aqui comprobamos que el resto r es 0, es decir que es divisible por n, es decir que len(input_bytes) es múltiplo de 32.
            if r != 0:
                raise ValueError("La lista de bytes de entrada debe tener una longitud multiplo de 32")
        else:
            if n*l!=len(input_bytes)*8:
                raise ValueError("La lista de bytes de entrada debe tener una longitud multiplo de 32")
        coefficients = [0 for _ in range(n)]
        list_of_bits = bytes2bits(input_bytes)
        for i in range(n):
            coefficients[i] = sum(list_of_bits[i*l + j] << j for j in range(l)) # el << j mueve los bits j veces a la izquierda.
        return coefficients

def decode_matrix(input_bytes, m_fil, n_col, l=None):
  """
  Debido al requerimiento de tamaño n*l = 8*len(pol o bytes) hacemos una función
  para hacer la descodficiación de una lista de listas de polinomios. (matriz).
  """
  n=256
  if l is None:
    # Tamaño de lista debe ser 32*l*m_fil*n_col
    l, check = divmod(8*len(input_bytes), n*m_fil*n_col)
    if check != 0:
      raise ValueError("La longitud del input de bytes debe ser multiplo de 32.")
    else:
      if n*l*m_fil*n_col > len(input_bytes)*8:
        raise ValueError("La longitud de bytes es pequeña para el l dado.")
  chunk_length = 32*l
  byte_chunks = [input_bytes[i:i+chunk_length] for i in range(0, len(input_bytes), chunk_length)]
  matrix = [[0 for _ in range(n_col)] for _ in range(m_fil)]
  for i in range(m_fil):
    for j in range(n_col):
      matrix[i][j] = decode(byte_chunks[n_col*i+j], l)
  return matrix

def encode(p, l=None):
   """
   Encode (Inverse of Algorithm 3)
   R_q--> B^32l
   """
   if l is None:
    l = max(x.bit_length() for x in p)
   bit_string = ''.join(format(c, f'0{l}b')[::-1] for c in p) # Agrupamos en bytes de como mucho l bits.
   return bits2bytes(bit_string)

def encode_matrix(A, l=None):
  """
  Lo utilizaremos para vectores se entienden como matrices de
  tamaño 1xk o de tamaño kx1.
  """

  col = len(A[0])
  output = b""

  for fila in A:
    for j in range(col):
      output += encode(fila[j],l=l)
  return output
def round_up(x):
    """
    Redondea 0.5 siempre.
    """
    return round(x + 0.000001)

def compress(x, d):
            """
            Comprimos una lista de coeficientes/bytes de un polinomio.
            Veáse que realmente no se conservará  la invertibilidad con decompress pero serán cercanos.
            """
            q=3329 # Siempre será el mismo q, para todas las versiones de Kyber: 512,768,1024.
            compr_mod = 2**d
            number = compr_mod/q
            pol_comprimido = [round_up(number*c)%compr_mod for c in x]
            return pol_comprimido

def compress_matrix(A,d):
  """
  Con lo anterior comprimimos elementos de una matriz.
  """
  B = [[0 for _ in range(len(A[0]))] for _ in range(len(A))]
  for i in range(len(A)):
    for j in range(len(A[0])):
      B[i][j] = compress(A[i][j],d)
  return B

def decompress(x, d):
  """
  Descomprimimos la lista haciendolo para cada componente/byte/coeficiente.
  Veáse que x' = decompress(compress(x)), pero x' != x, pero es cercano (diferencia menor que Bq, viene definido en el resource.)
  """
  q=3329
  number = q / (2**d)
  pol_descomprimido = [round_up(number*c) for c in x ]
  return pol_descomprimido

def decompress_matrix(A, d):
  """
  Con lo anterior decomprimimos elementos de una matriz.
  """
  B = [[0 for _ in range(len(A[0]))] for _ in range(len(A))]
  for i in range(len(A)):
    for j in range(len(A[0])):
      B[i][j] = decompress(A[i][j],d)
  return B

def generate_error_vector(k, sigma, eta, N):
  """
  Función auxiliar que genera un elemento en el
  módulo de la Distribución Binomial Centrada.
  """
  elements = []
  for i in range(k):
    input_bytes = PRF(sigma, N, 64*eta)
    poly = CBD(input_bytes, eta)
    elements.append(poly)
    N = N + 1

  v = [] # Nuestro vector que entenderemos como matriz 2x1.
  v.append(elements) # Aquí estaría en 1x2, asi que devolvemos la traspuesta.
  return traspuesta(v), N

def generate_matrix_from_seed(k, rho, traspose = False):
  """
  Función auxiliar que genera un elemento de tamaño.
  k x k de una semilla `rho`.

  Cuando "transpuesta" se establece en True, la matriz A es
  construida como la transposición.
  """
  A = []
  n = 256
  for i in range(k):
    row = []
    for j in range(k):
      if traspose:
        input_bytes = XOF(rho, bytes([i]), bytes([j]), 3*n)
      else:
        input_bytes = XOF(rho, bytes([j]), bytes([i]), 3*n)
      aij = Parse(input_bytes)
      row.append(aij)
    A.append(row)
  return A
def graficar_reticulo(matrix):
    """
    Grafica un retículo donde cada polinomio se representa como un conjunto de puntos.
    
    :param matrix: Matriz de retículo, donde cada elemento es un polinomio (lista de coeficientes).
    """
    ax = plt.subplots(figsize=(8, 8))

    # Recorrer filas y columnas
    for i, fila in enumerate(matrix):
        for j, polinomio in enumerate(fila):
            # Graficar cada polinomio como puntos
            grados = list(range(len(polinomio)))
            coeficientes = polinomio
            ax.scatter(
                [j + 1 + 0.1 * k for k in grados],  # Desplazar ligeramente en X para separar puntos
                coeficientes,
                label=f"Polinomio ({i + 1}, {j + 1})"
            )

    # Etiquetas y diseño
    ax.set_title("Visualización del Retículo")
    ax.set_xlabel("Columna del Retículo")
    ax.set_ylabel("Coeficientes de los Polinomios")
    ax.grid(True)
    plt.legend()
    plt.show()


def keygen(k,n1):
  """
        Algorithm 4 (Key Generation)
        https://pq-crystals.org/kyber/data/kyber-specification-round3-20210804.pdf

        Input:
            None
        Output:
            Secret Key (12*k*n) / 8      bytes
            Public Key (12*k*n) / 8 + 32 bytes
  """
  # Kyber parámetros.
  n, q = 256, 3329

  d = os.urandom(32) # Semilla de aleatoridad. # El sistema nos da 32 bytes aleatorios y los pasamos a formato lista con enteros.
  # print('d es: ',d)
  rho, sigma = G(d)
  # print('rho es: ', rho)
  # print('sigma es: ', sigma)
  # Incializamos contador para el PRF.
  N=0

  # Generamos la matriz A ∈ R^kxk
  A_nt = generate_matrix_from_seed(k, rho)
  # print('A es : ', A_nt)

  # Generamos el vector error s ∈ R^k
  s, N = generate_error_vector(k,sigma, n1, N)
  # print('s es: ',s)
  s_nt = [[NTT_kyber(s[i][0])] for i in range(k)]
  # print('sk es: ', s_nt)

  # Generamos el vector error e ∈ R^k
  e, N = generate_error_vector(k,sigma, n1, N)
  # print('e es: ', e)
  e_nt = [[NTT_kyber(e[i][0])] for i in range(k)]

  # Hacemos la multplicación de la matriz A y s_nt utilizando la convolución, pues sus elementos son polinomios de Rq.
  t = Matriz_mult_viaNTT(A_nt,s_nt)
  #print('A*NTT(s) es: ',t)
  #print('NTT(e) es: ',e_nt)
  # Sumamos ahora el vector error.
  t = vector_sum(t,e_nt)
  # print('t = A*NTT(s)+NTT(e) es: ',t)

  # Ahora codificamos, realmente esto es usado para la representacion bytes (b:'\x...') pero queremos tener los algoritmos
  # en enteros así que al final lo devolveremos todo en formato de listas de enteros, que representan bytes cada uno, si se quisieran obtener por
  # algún motivo bastaría con aplicar bytes() a los outputs y ya.
  # Antes de codificar t y s_nt, imprimimos sus valores en crudo
  # graficar_reticulo(t)
  # graficar_reticulo(s_nt)
  # pk = encode_matrix(t,12)+rho
  # sk = encode_matrix(s_nt,12)
  # print('pk es: ', list(pk))
  # print('sk es: ', list(sk))

  return pk, sk
  
def encryption(pk,m,r1,k,n1,n2,du,dv):
  """
  Inputs: public key: pk, message: m, r = coins, k = dimention.
  Output : "Chipertext : B^(du*k*n/8+dv*n/8)
  """
  n , q, N = 256, 3329, 0

  rho = pk[-32:]

  tt = decode_matrix(pk, 1, k, l=12)
  # print('tt es: ',tt)
  # print(' t es: ',traspuesta(tt))
  m_pol = decompress(decode(m,1),1)
  # print('m_pol es: ', m_pol)

  # Generamos matriz, r (aleatorio) y error e2 aleatorio desde la semilla.
  At = generate_matrix_from_seed(k, rho,True)
  # print('A es : ', traspuesta(A))

  r , N = generate_error_vector(k,r1, n1, N)
  # print('r es: ',r)
  r_nt = [[NTT_kyber(r[i][0])] for i in range(k)]

  e1, N = generate_error_vector(k,r1, n2, N)
  # print('e1 es: ',e1)

  # Generamos polinomio (escalar de Rq) error e2:
  e2 = CBD(PRF(r1, N, 64*n2), n2)
  # print('e2 es: ',e2)

  # Realizamos las operaciones de matrices y sumas en Rq.
  u = Matriz_mult_viaNTT(At,r_nt)
  u = [[INTT_kyber(u[i][0])] for i in range(k)]

  u = vector_sum(u,e1)
  # print('u es: ',u)

  v = Matriz_mult_viaNTT(tt,r_nt)[0][0]
  v = INTT_kyber(v)
  v = suma_pol(v,e2) # vease que ahora son escalares a sumar, no vectores.
  v = suma_pol(v,m_pol)
  print('v es: ',v)

  # Codificamos:
  c1 = encode_matrix(compress_matrix(u,du),du)
  c2 = encode(compress(v,dv),dv)

  c = c1+c2
  print('El mensaje cifrado es: ', c)
  return c
def decryption(sk,c,du,dv):
  """
  Inputs: secret key: sk, du, dv, Chipertext : B^(du*k*n/8+dv*n/8)
  Output : message: m
  """
  n, q = 256, 3329
  # Partimos el ciphertext a vectores.
  c2 = c[du*k*(n//8):]

  # Recuperamos el vector u.
  u = decompress_matrix(decode_matrix(c, k, 1, l=du),du)
  # print('u es: ',u)
  # print('decode: ',decode_matrix(c,k,1,du))
  # Aplicamos NTT al vector u.
  u_nt = [[NTT_kyber(u[i][0])] for i in range(k)]

  # Recuperamos el polinomio v.
  v = decompress(decode(c2, l=dv),dv)
  # print('v es: ',v)

  # s traspuesta en el dominio NTT.
  st = decode_matrix(sk, 1, k, l=12)
  # print('sk es: ',st[0])

  # Recuperar mensaje como polinomio.
  st_u = Matriz_mult_viaNTT(st,u_nt)[0][0]
  # print('st_u es: ',st_u)
  st_u = INTT_kyber(st_u)
  # print('INTT(st*u) es: ',st_u)
  m = [(a-b) for a,b in zip(v,st_u)] # La resta es de un polinomio.

  # Devolvemos el mensaje codificado en bytes.
  return encode(compress(m,1),1)
#7 Padding para cifrar y descifrar mensajes de cualquier longitud de bytes.

# Parámetros: (Usamos los de Kyber 512 en este caso).
k=2
du, dv= 10, 4
n1, n2= 3,2
# pk,sk= keygen(k,n1) # Generamos claves.
r1 = os.urandom(32)

def pad(message):
  """
  Funcción para rellenar (pad) un mensaje de tamaño menor a 32.
  """
  pad_len = 32 - (len(message) % 32)
  padding = bytes([pad_len] * pad_len)
  return message + padding

def partir_32(message):
  """
  Función para separar un mensaje con mayor tamaño de bytes que 32
  Lo que hará es partir en varios bloques de 32 bytes y el último lo que sobre.
  """
  blocks = [message[i:i+32] for i in range(0, len(message), 32)]
  return blocks


def unpad(padded_message):
  """
  Función para invertir el padding una vez ya hemos
  hecho el proceso de cifrar y descifrar.
  """
  pad_len = padded_message[-1]
  return padded_message[:-pad_len]

def pad_encryption(message, pk):
  """
  Función para encriptar un mensaje de longitud arbitraria.
  Usamremos las funciones pad y unpad y la encriptación de Kyber.
  La función devolverá un número del 1 a 4 para saber en que caso estamos al descifrar.
  """
  if len(message)<32: # Aquí usamos pad y el cifrado.
    M = 1 # Caso longitud menor.
    message = pad(message)
    ciphertext = encryption(pk,message,r1,k,n1,n2,du,dv)
    return M, ciphertext

  if len(message) == 32: # Aquí ya estaría de estándar es 32 bytes, aplicamos encriptación normal.
    M = 2 # Caso longitud exacta.
    ciphertext = encryption(pk,message,r1,k,n1,n2,du,dv)
    return M, ciphertext

  else: # En este caso de mayor tamaño debemos hacer una partición y rellenar el que nos quede si es que no es múltiplo de 32.

    if len(message)%32 == 0: # Si es múltiplo de 32 solo hay que hacer partición.
      M = 3

      messages = partir_32(message) # Veáse que ahora obtenemos una lista en la que tenemos que cifrar sus elementos.
      # ciphertexts = []

      # for m in messages:
      #   # ciphertext = encryption(pk,m,r1,k,n1,n2,du,dv)
      ciphertexts.append(ciphertext)

      return M, ciphertexts # Obtenemos una lista de mensajes cifrados.

    else: # En este caso lo que sobre de dividir en 32 bytes debemos hacerle un pad.
      M = 4
      messages = partir_32(message)
      ciphertexts = []

      # El último debemos hacerle padding:
      messages[-1] = pad(messages[-1])

      for m in messages:
        ciphertext = encryption(pk,m,r1,k,n1,n2,du,dv)
        ciphertexts.append(ciphertext)

      return M, ciphertexts # Obtenemos una lista de mensajes cifrados.

def unpad_decryption(M,sk, ciphertexts):
  """
  Función para desencriptar un mensaje de longitud arbitraria.
  Usamremos las funciones pad y unpad y la desencriptación de Kyber.
  """
  if M == 1:
    message = decryption(sk,ciphertexts,du,dv)
    message = unpad(message)
    return message
  if M == 2:
    message = decryption(sk,ciphertexts,du,dv)
    return message
  if M == 3:
    messages = []

    for c in ciphertexts:
      message = decryption(sk,c,du,dv)
      messages.append(message)

    message = b''.join(messages)

    return message

  if M == 4:
    messages = []

    for c in ciphertexts:
      message = decryption(sk,c,du,dv)
      messages.append(message)

    messages[-1] = unpad(messages[-1]) # Solo se hace un/padding en el último.
    message = b''.join(messages)
    return message


app = Flask(__name__)

@app.route('/encrypt', methods=['POST'])
def encrypt():
    # Obtener el mensaje del cuerpo de la solicitud
    data = request.json
    message = data.get('message')
    pk_base64 = data.get('public_key')
    # Asegúrate de que el mensaje es una cadena y conviértelo a bytes
    if isinstance(message, str):
        message = message.encode('utf-8')
    elif not isinstance(message, bytes):
        return jsonify({'error': 'El mensaje debe ser una cadena o bytes.'}), 400

    # Lógica de cifrado
    pk = base64.b64decode(pk_base64)
    M, encrypted_message = pad_encryption(message, pk)

    # Convertir el mensaje cifrado a Base64 para que sea JSON serializable
    encrypted_message_base64 = base64.b64encode(encrypted_message).decode('utf-8')
    #secret_key = base64.b64encode(sk).decode('utf-8')
    # Devolver la respuesta en formato JSON
    return jsonify({'encrypted_message': encrypted_message_base64, 'M': M})

@app.route('/decrypt', methods=['POST'])
def decrypt():
    # Obtener el mensaje cifrado y la clave secreta del cuerpo de la solicitud
    data = request.json

    encrypted_message_base64 = data.get('encryptedMessage')
    M = data.get('M')
    secret_key_base64 = data.get('secret_key')

    # Validar que ambos estén presentes
    if not encrypted_message_base64:
        return jsonify({'error': 'El mensaje cifrado y la clave secreta deben ser proporcionados.'}), 400

    try:
        # Decodificar el mensaje cifrado y la clave secreta desde Base64
        encrypted_message = base64.b64decode(encrypted_message_base64)
        sk = base64.b64decode(secret_key_base64)

        # Desencriptar el mensaje utilizando la clave secreta y la función unpad_decryption
        result = unpad_decryption(M, sk, encrypted_message)  # Usar secret_key
        print('result',result)

        # Verificar que `unpad_decryption` no devuelva None
        # Verificar si el resultado es una tupla con dos elementos
        if not result:
          return jsonify({'error': 'La desencriptación falló. No se pudo recuperar el mensaje correctamente.'}), 500

        decrypted_message = result

        # Convertir el mensaje desencriptado a una cadena
        decrypted_message_str = decrypted_message.decode('utf-8')

        # Devolver la respuesta en formato JSON
        return jsonify({'decrypted_message': decrypted_message_str})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint para generar las claves
@app.route('/generate_keys', methods=['POST'])
def generate_keys():
    k = 2
    n1 = 3
    # Invocamos la función keygen para generar las claves
    public_key, secret_key = keygen(k, n1)
    
    # Convertir las claves a Base64 para que sean JSON serializables
    public_key = base64.b64encode(public_key).decode('utf-8')
    secret_key = base64.b64encode(secret_key).decode('utf-8')
    # Devolver las claves en formato JSON
    return jsonify({
        'public_key': public_key,
        'secret_key': secret_key
    })

if __name__ == '__main__':
    app.run(port=5001)  # Ejecutar el servidor en el puerto 5001


# message = b'hola'

# M, ciphertext = pad_encryption(message)
# original_message = unpad_decryption(M,ciphertext)

# print('El mensaje original es: ')
# print(original_message)