##########################################
# Código creado por Sebastián Sterling
##########################################

from django import forms
from django.core.exceptions import ValidationError
from .models import User
from .Config import DB_CONFIG
import hashlib
import pymysql
import re

from django.contrib.auth import get_user_model


# from django.contrib.auth import authenticate

######################## Funciones de apoyo ######################## 

def validar_email(email):
    # Verificar que el email tenga un formato válido utilizando una expresión regular
    if re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return True
    else:
        return False

def establecer_conexion():
    connection = pymysql.connect(**DB_CONFIG)
    return connection

def get_username(email):
    # Establecer conexión a la base de datos
    connection = establecer_conexion()
    cursor = connection.cursor()
    
    # Consulta para obtener la contraseña asociada al correo electrónico dado
    query = "SELECT Username FROM register_user WHERE E_mail = %s"
    cursor.execute(query, (email,))
    result = cursor.fetchone()

    # Verificar si se obtuvo un resultado
    if result:
        username = result[0]  # Obtener el primer elemento de la tupla
    else:
        username = None  # O manejar el caso de no encontrar el usuario

    return username


def clean_username(username):
    username = re.sub(r'[^a-zA-Z0-9]', '', username)
    print(username)
    return username  # Solo permite letras y números

######################## Funciones de apoyo ######################## 

######################## Función de autenticar el usuario ######################## 

# Función para autenticar al usuario identificándolo con su correo registrado y comparando el Hash de las contraseñas
def autenticar(email, password):
    
    # Verificar el e-mail dado
    if not validar_email(email):
        return None 
    
    # Convertir la cadena concatenada en bytes y actualizar el hash
    hash_object = hashlib.sha256()
    hash_object.update(password.encode())
    given_password = hash_object.hexdigest()
    
    # Establecer conexión a la base de datos
    connection = establecer_conexion()
    cursor = connection.cursor()
    
    # Consulta para obtener la contraseña asociada al correo electrónico dado
    query = "SELECT Pass, Token FROM register_user WHERE E_mail = %s"
    cursor.execute(query, (email,))
    result = cursor.fetchone()
    
    if result:
        # Obtener la contraseña de la base de datos
        # db_password = result[0]
        db_password, db_token = result
        
        # Comparación
        if given_password == db_password:
            return db_token  
        else:
            return False
    else:
        return False

# ######################## Función de autenticar el usuario ######################## 

######################## Función de registro para usuario ######################## 

def tokenGen(user, email):
    
    # Concatenar el nombre de usuario y el correo electrónico, crear un objeto hash usando SHA-256
    data = user + email
    hash_object = hashlib.sha256()

    # Convertir la cadena concatenada en bytes y actualizar el hash
    hash_object.update(data.encode())
    token = hash_object.hexdigest()

    return token

class RegistroForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ['Username', 'E_mail', 'Pass', 'Phone_number', 'Token']
        
    # Verificar la fortaleza de las contraseñas
    def clean_Pass(self):
        password = self.cleaned_data.get('Pass')
        if any(c.isupper() for c in password) and any(c.islower() for c in password) and any(c.isdigit() for c in password) and len(password) >= 8:
            return password
        else:
            raise ValidationError("The password must contain at least 8 characters, one uppercase, one lowecase and one digit.")

    # Guardar la información
    def save(self, commit=True):
        self.full_clean()
        instance = super().save(commit=False)

        # Encriptar la contraseña utilizando PBKDF2 - pycryptodome
        #################################################
        # from Crypto.Random import get_random_bytes
        # from Crypto.Protocol.KDF import PBKDF2
        #################################################
        # password = self.cleaned_data.get('Pass')
        # salt = get_random_bytes(16)  # Generar una sal aleatoria de 16 bytes
        # encrypted_password = PBKDF2(password.encode(), salt, dkLen=32)  # Derivar una clave de 32 bytes
        # instance.Pass = encrypted_password
        
        password = self.cleaned_data.get('Pass')
        # Si se quiere encriptar, pero no tendría forma de hacer la comparación, dado que siempre sería un key aleatorio
        #################################################
        # from django.contrib.auth.hashers import make_password
        # import secrets
        #################################################
        # encrypted_password = make_password(password)
        hash_object = hashlib.sha256()
        hash_object.update(password.encode())
        encrypted_password = hash_object.hexdigest()
        
        # Asignar la contraseña encriptada al request para guardar el nuevo usuario
        instance.Pass = encrypted_password
        
        # Generar el token con el hash de usuario y correo electrónico
        username = self.cleaned_data.get('Username')
        email = self.cleaned_data.get('E_mail')
        token = tokenGen(username, email)
        
        # Asignar el token al campo 'Token' del modelo
        instance.Token = token

        if commit:
            instance.save()

        return instance

######################## Función de registro para usuario ######################## 