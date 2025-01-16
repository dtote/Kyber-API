import hashlib
import numpy as np
# Reduccion modular de r respecto a alpha
def modpm(r, alpha): 
  a = int((alpha-1) / 2) + 1
  b = int(r / 2 + 1)
  r1 = r % alpha
  
  if alpha % 2 == 0:
    if not r1 in range(b): 
      r1 -= alpha 
    else:
      if not r1 in range(a):
        r1 -= alpha
  return r1

# Ejemplo de uso
# Tenemos un valor hash r = 123456 y deseamos reducirlo utilizando la reduccion modular respecto a alpha = 1000
r_reducido = modpm(123456, 1000)
print(r_reducido) # 456

# Función para aplicar la descomposición de un módulo q
def decompose(r, alpha, q): 
  r = r % q
  r0 = modpm(r, alpha)

  if r - r0 == q - 1:
    r1 = 0
    r0 = r0 - 1
  
  else:
    r1 = int(r - r0) / alpha
  return (r1, r0)

# Ejemplo de uso:
r = 10
alpha = 3
q = 7
r1, r0 = decompose(r, alpha, q)
print(f"r1: {r1}, r0: {r0}")

# Funciones utilizadas en el proceso de la firma

# Funcion que devuelve la parte alta de un numero, puede ser utilizada como clave secreta de un número
def highbits(r, alpha, q):
  return decompose(r, alpha, q)[0]

# Funcion que devuelve la parte baja de un numero, puede ser utilizada como clave publica de un número
def lowbits(r, alpha, q):
  return decompose(r, alpha, q)[1]

# Esta funcion calcula la norma infinito de una matriz, puede ser utilizada para medir la distancia o tamaño de los vectores en una matriz
def inf(matriz):
  return max(np.linalg.norm(matriz, ord=np.inf, axis = 1))

# Ejemplo de uso:
hb = []
lb = []

for i in range(1,5):
  for j in range(1,5):
    hb.append(highbits(i, j, q))
    lb.append(lowbits(i, j, q))

print(hb)
print(lb)

# Funcion que se utiliza para calcular el hash de un mensaje
# Se utiliza en situaciones donde se necesita verificar la integridad de los datos y en la firma digital
# 1. Verificacion de integridad de los datos: Si el hash dem mensaje recibido coincide con el hash del mensaje original, entonces los datos no han sido alterados
# 2. Firma digital: Si el hash del mensaje coincide con el hash del mensaje original, entonces el mensaje ha sido firmado por el emisor
def hashing(text, w_1):
  hash_obj = hashlib.sha256(text.encode('utf-8'))
  hash_result = int.from_bytes(hash_obj.digest(), byteorder='big') % (10 ** w_1)

  return hash_result

# Ejemplo de uso:

# Almacenar la contraseña de un usuario
contraseña = "mi_contraseña_segura"
w_1 = 5
hash_contraseña = hashing(contraseña, w_1)
almacenamiento_seguro = hash_contraseña
contraseña_introducida = "mi_contraseña_segura" # Esta sería la contraseña introducida por el usuario
hash_contraseña_introducida = hashing(contraseña_introducida, w_1)

if hash_contraseña_introducida == almacenamiento_seguro:
    print("Inicio de sesión exitoso!")
else:
    print("Contraseña incorrecta!")