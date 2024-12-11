from tkinter import *
from tkinter import messagebox
from tkinter import Toplevel
from PIL import Image,ImageTk
import mysql.connector as mariadb
from mysql.connector import Error  # Para manejar errores específicos
import os
import subprocess

# Variable global para almacenar el ID del usuario que inició sesión
usuario_actual=None

def conectar():
   
    try:
        conexion = mariadb.connect(
            host='localhost',
            port=3306,
            user='root',
            password='MOREMORE',
            database='bd_mikes',
            charset='utf8mb4',  # Forzar uso de charset compatible
            collation='utf8mb4_general_ci'  # Forzar intercalación
        )
        print("Conexión exitosa a la base de datos")
        return conexion
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None
    
def act(conexion):
    try:
        cursor = conexion.cursor()  # Crear el cursor

        # Insertar productos
        for producto in productos:
            nombre_producto = producto[0]
            cursor.execute("SELECT COUNT(*) FROM Producto WHERE Nombre = %s", (nombre_producto,))
            result = cursor.fetchone()
            
            if result[0] == 0:  # Si el producto no existe
                cursor.execute(
                    "INSERT INTO Producto (Nombre, Descripcion, Precio, Stock) VALUES (%s, %s, %s, %s)",
                    producto
                )
                print(f"Producto '{nombre_producto}' agregado.")
            else:
                print(f"Producto '{nombre_producto}' ya existe en la base de datos.")
        
        # Insertar administradores
        for i, adm in enumerate(administrador):
            us_adm = adm[0]
            cursor.execute("SELECT COUNT(*) FROM administradores WHERE Usuario_Ad = %s", (us_adm,))
            result = cursor.fetchone()
            
            
            if result[0] == 0:  # Si el administrador no existe
                # Insertar información personal
                info_personal = inf_adm[i]
                cursor.execute(
                    "INSERT INTO informacion_personal (Nombres, ApellidoP, ApellidoM, Direccion) VALUES (%s, %s, %s, %s)",
                    info_personal
                )
                ID_InfoP = cursor.lastrowid

                # Insertar administrador
                cursor.execute(
                    "INSERT INTO administradores (Usuario_Ad, Contraseña, Puesto, FK_ID_InfoP) VALUES (%s, %s, %s, %s)",
                    (adm[0], adm[1], adm[2], ID_InfoP)
                )
                print(f"Administrador '{us_adm}' agregado.")
            else:
                print(f"Administrador '{us_adm}' ya existe en la base de datos.")
        
        # Confirmar los cambios
        conexion.commit()

    except mariadb.Error as error:
        print(f"Error al insertar datos: {error}")
        conexion.rollback()  # Revertir cambios en caso de error
    finally:
        cursor.close()  # Cerrar el cursor

# Lista de productos con precios
productos = [
    ('Pantalla', 'Pantalla LED 24 pulgadas', 1000,9),
    ('Telefono', 'Smartphone 128GB', 500,10),
    ('Tablet', 'Tablet 10 pulgadas 64GB', 300,5),
    ('Auriculares', 'Auriculares Bluetooth', 50,30),
    ('Teclado', 'Teclado mecánico retroiluminado', 30,2)
]    

# Lista de Administrador
administrador=[
    ('MARC','MOREMORE','Dueño')

]

# Lista de Info personal del Administrador
inf_adm=[
    ('Miguel Ángel','Rodríguez','Cervantes','Atlalilco')
]

# Carrito de compras
carrito = {}

# Función para registrar un nuevo usuario
def registrarse():
    registro = Toplevel(lista_productos)
    registro.title("Registro de Usuario")
    registro.geometry("600x400")
    registro.configure(bg="black")
    
    titulo = Label(registro, text="Registro",bg="black",fg="white")
    titulo.place(x=250, y=10)#Se pude hacer de 2 formas. Esta y la de abajo
    compra = Label(registro, text="Ingrese los datos del Usuario: ",bg="black",fg="white").place(x=1, y=25)

    Label(registro,text="Ingrese sus nombres: ",bg="grey").place(x=20,y=60)
    nombres=Entry(registro, width=50)
    nombres.place(x=190,y=60)

    Label(registro,text="Ingrese su Apellido Paterno: ",bg="grey").place(x=20,y=100)
    apellidop=Entry(registro, width=30)
    apellidop.place(x=190,y=100)

    Label(registro,text="Ingrese su Apellido Materno: ",bg="grey").place(x=20,y=140)
    apellidom=Entry(registro, width=30)
    apellidom.place(x=190,y=140)

    Label(registro,text="Ingrese su direccion: ",bg="grey").place(x=20, y=180)
    direc1=Entry(registro, width=50)
    direc1.place(x=190, y=180)

    Label(registro,text="Ingrese nombre de usuario: ",bg="grey").place(x=20, y=220)
    nombre_us=Entry(registro, width=50)
    nombre_us.place(x=190, y=220)

    Label(registro,text="Ingrese contraseña: ",bg="grey").place(x=20, y=260)
    contraseña=Entry(registro, width=50)
    contraseña.place(x=190, y=260)
    
    def guardar_datos():
        inf_name = nombres.get()
        inf_ap = apellidop.get()
        inf_am = apellidom.get()
        inf_dirc = direc1.get()
        us_nom = nombre_us.get()
        us_cont = contraseña.get()

        # Validar que todos los campos estén llenos
        if not (inf_name and inf_ap and inf_am and inf_dirc and us_nom and us_cont):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        # Intentar conectar a la base de datos
        conexion = conectar()
        if conexion:
            try:
                cursor = conexion.cursor()

                # Primera consulta: Insertar en la tabla 'informacion_personal'
                cursor.execute(
                    "INSERT INTO informacion_personal(Nombres, ApellidoP, ApellidoM, Direccion) VALUES (%s, %s, %s, %s)",
                    (inf_name, inf_ap, inf_am, inf_dirc)
                )

                ID_InfoP = cursor.lastrowid

                # Segunda consulta: Insertar en la tabla 'usuario'
                cursor.execute(
                    "INSERT INTO usuario(Nombre_Usuario, Contraseña,FK_ID_InfoP) VALUES (%s, %s,%s)",
                    (us_nom, us_cont,ID_InfoP)
                )

                # Confirmar los cambios
                conexion.commit()
                messagebox.showinfo("Éxito", "La información del usuario se registró correctamente")

            except mariadb.Error as error:
                # Manejar el error si ocurre
                if error.errno == mariadb.errorcode.ER_DUP_ENTRY:
                    messagebox.showerror("Error", "El usuario ya está registrado.")
                else:
                    messagebox.showerror("Error", f"Error al guardar el usuario: {error}")
            
            finally:
                # Asegurarse de cerrar la conexión a la base de datos
                conexion.close()
        
        else:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos")

    Button(registro, text="Verificar", command=guardar_datos).place(x=100, y=350)
    Button(registro, text="Cancelar", command=registro.destroy).place(x=500, y=350)


# Función para crear una ventana de inicio de sesión
def iniciar_sesion():
    global usuario_actual
    sesion = Toplevel(lista_productos)
    sesion.title("Iniciar Sesión")
    sesion.geometry("300x200")

    Label(sesion, text="Usuario:").place(x=20, y=30)
    usuario = Entry(sesion, width=25)
    usuario.place(x=100, y=30)

    Label(sesion, text="Contraseña:").place(x=20, y=70)
    contrasena = Entry(sesion, width=25, show="*")
    contrasena.place(x=100, y=70)

    def verificar_credenciales():
        global usuario_actual
        verf_usuario = usuario.get()
        verf_contrasena = contrasena.get()

        # Conectar a la base de datos
        conexion = conectar()
        if not conexion:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos")
            return

        try:
            cursor = conexion.cursor()

            # Verificar en la tabla 'usuario'
            cursor.execute(
                "SELECT ID_Usuario FROM usuario WHERE Nombre_Usuario = %s AND Contraseña = %s",
                (verf_usuario, verf_contrasena)
            )
            resultado = cursor.fetchone()

            if resultado:
                usuario_actual = resultado[0]
                messagebox.showinfo("Inicio de Sesión", "¡Inicio de sesión exitoso como usuario!")
                sesion.destroy()
                return

            # Si no se encontró en 'usuario', verificar en 'administradores'
            cursor.execute(
                "SELECT ID_Administrador FROM administradores WHERE Usuario_Ad = %s AND Contraseña = %s",
                (verf_usuario, verf_contrasena)
            )
            resultado = cursor.fetchone()

            if resultado:
                usuario_actual = resultado[0]
                messagebox.showinfo("Inicio de Sesión", "¡Inicio de sesión exitoso como administrador!")
                sesion.destroy()

                # Abrir el código en Visual Studio Code
                archivo_actual = os.path.abspath(__file__)  # Ruta absoluta del archivo Python actual

                try:
                    subprocess.run(["C:/Users/marc1/AppData/Local/Programs/Microsoft VS Code/Code.exe", archivo_actual],check=True)
                except FileNotFoundError:
                    messagebox.showerror(
                        "Error", "No se encontró Visual Studio Code. Configura correctamente la ruta del ejecutable."
                    )
                except Exception as e:
                    messagebox.showerror("Error", f"Error al abrir el archivo en Visual Studio Code: {e}")
                # Opción 1: Usar subprocess para abrir en VS Code
                #subprocess.run(['code', archivo_actual])

                # Opción 2: Usar os.system para abrir en VS Code (también puede funcionar)
                #os.system(f'code "{archivo_actual}"')

            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos")

        except mariadb.Error as e:
            messagebox.showerror("Error", f"Error al verificar credenciales: {e}")
        finally:
            conexion.close()

    Button(sesion, text="Iniciar Sesión", command=verificar_credenciales).place(x=100, y=120)
    Button(sesion, text="Cerrar", command=sesion.destroy).place(x=200, y=120)


#Obtener producto desde MARIADB
def obtener_producto_desde_bd(nombre_producto):
    conexion = conectar()
    if not conexion:
        messagebox.showerror("Error", "No se pudo conectar a la base de datos")
        return None
    
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT ID_Producto,Nombre, Descripcion, Precio FROM Producto WHERE Nombre = %s", (nombre_producto,))
        producto = cursor.fetchone()  # Obtener el primer resultado
        return producto  # Devuelve (Nombre, Descripción, Precio)
    except mariadb.Error as e:
        print(f"Error al obtener producto: {e}")
        return None
    finally:
        conexion.close()


# Función para agregar productos al carrito
def agregar_carrito(nombre_producto):
    producto = obtener_producto_desde_bd(nombre_producto)  # Consultar el producto en la base de datos
    if not producto:
        messagebox.showerror("Error", f"El producto '{nombre_producto}' no se encontró en la base de datos.")
        return

    id_producto, _, _, precio = producto  # Desempaquetar los valores de la base de datos
    if id_producto in carrito:
        carrito[id_producto]["cantidad"] += 1
    else:
        carrito[id_producto] = {"nombre": nombre_producto, "precio": precio, "cantidad": 1}

    actualizar_carrito()
    messagebox.showinfo("Producto agregado", f"{nombre_producto} ha sido agregado al carrito.")

# Función para actualizar la visualización del carrito
def actualizar_carrito():
    carrito_text.delete(1.0, END)
    total = 0
    for id_producto, datos in carrito.items():
        nombre = datos["nombre"]
        precio = datos["precio"]
        cantidad = datos["cantidad"]
        subtotal = precio * cantidad
        carrito_text.insert(END, f"{nombre} x{cantidad} - ${subtotal}\n")
        total += subtotal
    carrito_text.insert(END, f"\nTotal: ${total}")

# Función para vaciar el carrito
def vaciar_carrito():
    global carrito
    carrito.clear()  # Vaciar el diccionario del carrito
    actualizar_carrito()  # Actualizar la visualización
    messagebox.showinfo("Carrito", "El carrito ha sido vaciado.")

# Función para mostrar la información de la Pantalla
def crear_info_Pantalla():
    info_Pantalla = Toplevel(lista_productos)
    info_Pantalla.title("Información del Producto")
    info_Pantalla.geometry("400x300")
    info_Pantalla.configure(bg="darkblue")

     #Descripcion
    Label(info_Pantalla, text="Descripcion: ",bg="black",fg="white").place(x=230,y=50)
    Label(info_Pantalla, text="Pantalla LED 24 pulgadas",bg="darkblue",fg="white").place(x=230,y=80)

    #Precio
    Label(info_Pantalla,text="Precio: ",bg="black",fg="white").place(x=230,y=130)
    Label(info_Pantalla, text="$ 1,000", font=("Arial", 15),bg="darkblue",fg="white").place(x=280,y=160)
    
    # Añadir widgets en la ventana hija
    etiqueta = Label(info_Pantalla, text="Pantalla",bg="black",fg="white")
    etiqueta.place(x=20, y=20)

    #Imagenes "global" para que no se borre de la pantalla
    global imgP1
    img1=Image.open("Pantalla1.jpg")
    img1=img1.resize((200,132))
    imgP1=ImageTk.PhotoImage(img1)
    Label(info_Pantalla, image=imgP1).place(x=20,y=50)
    
    # Botón para agregar al carrito
    agregar = Button(info_Pantalla, text="Agregar", command=lambda: agregar_carrito("Pantalla"))

    agregar = Button(info_Pantalla, text="Agregar", command=lambda: agregar_carrito("Pantalla")) #and info_Pantalla.destroy)
    agregar.place(x=320, y=250)
    
    # Botón para cerrar la ventana hija
    regresar = Button(info_Pantalla, text="Cerrar", command=info_Pantalla.destroy)
    regresar.place(x=20, y=250)

# Función para mostrar la información del Teléfono
def crear_info_Tel():
    info_Tel = Toplevel(lista_productos)
    info_Tel.title("Información del Producto")
    info_Tel.geometry("400x300")
    info_Tel.configure(bg="darkblue")

    #Descripcion
    Label(info_Tel, text="Descripcion: ",bg="black",fg="white").place(x=230,y=50)
    Label(info_Tel, text="Smartphone 128GB",bg="darkblue",fg="white").place(x=230,y=80)

    #Precio
    Label(info_Tel,text="Precio: ",bg="black",fg="white").place(x=230,y=130)
    Label(info_Tel, text="$ 500", font=("Arial", 15),bg="darkblue",fg="white").place(x=290,y=160)

    #Imagen
    global imgT2
    img3=Image.open("smartphone.jpg")
    img3=img3.resize((200,132))
    imgT2=ImageTk.PhotoImage(img3)
    Label(info_Tel, image=imgT2).place(x=20,y=50)
    
    # Añadir widgets en la ventana hija
    etiqueta = Label(info_Tel, text="Teléfono",bg="black",fg="white")
    etiqueta.place(x=20, y=20)
    
    # Botón para agregar al carrito
    agregar = Button(info_Tel, text="Agregar", command=lambda: agregar_carrito("Telefono"))
    agregar.place(x=320, y=250)
    
    # Botón para cerrar la ventana hija
    regresar = Button(info_Tel, text="Cerrar", command=info_Tel.destroy)
    regresar.place(x=20, y=250)

def crear_info_Tab():
    info_Tab = Toplevel(lista_productos)
    info_Tab.title("Información del Producto")
    info_Tab.geometry("400x300")
    info_Tab.configure(bg="darkblue")

     #Descripcion
    Label(info_Tab, text="Descripcion: ",bg="black",fg="white").place(x=190,y=50)
    Label(info_Tab, text="Tablet 10 pulgadas 64GB",bg="darkblue",fg="white").place(x=190,y=80)

    #Precio
    Label(info_Tab,text="Precio: ",bg="black",fg="white").place(x=190,y=130)
    Label(info_Tab, text="$ 300", font=("Arial", 15),bg="darkblue",fg="white").place(x=250,y=160)

    #Imagen
    global imgT2
    img3=Image.open("Tab.jpg")
    img3=img3.resize((150,150))
    imgT2=ImageTk.PhotoImage(img3)
    Label(info_Tab, image=imgT2).place(x=20,y=50)
    
    # Añadir widgets en la ventana hija
    etiqueta = Label(info_Tab, text="Tableta",bg="black",fg="white")
    etiqueta.place(x=20, y=20)
    
    # Botón para agregar al carrito
    agregar = Button(info_Tab, text="Agregar", command=lambda: agregar_carrito("Tablet"))
    agregar.place(x=320, y=230)
    
    # Botón para cerrar la ventana hija
    regresar = Button(info_Tab, text="Cerrar", command=info_Tab.destroy)
    regresar.place(x=20, y=230)

def crear_info_Aud():
    info_Aud = Toplevel(lista_productos)
    info_Aud.title("Información del Producto")
    info_Aud.geometry("400x300")
    info_Aud.configure(bg="darkblue")

    #Descripcion
    Label(info_Aud, text="Descripcion: ",bg="black",fg="white").place(x=230,y=50)
    Label(info_Aud, text="Auriculares Bluetooth",bg="darkblue",fg="white").place(x=230,y=80)

    #Precio
    Label(info_Aud,text="Precio: ",bg="black",fg="white").place(x=230,y=130)
    Label(info_Aud, text="$ 50", font=("Arial", 15),bg="darkblue",fg="white").place(x=290,y=160)

    #Imagen
    global imgT2
    img3=Image.open("aud.jpg")
    img3=img3.resize((200,132))
    imgT2=ImageTk.PhotoImage(img3)
    Label(info_Aud, image=imgT2).place(x=20,y=50)
    
    # Añadir widgets en la ventana hija
    etiqueta = Label(info_Aud, text="Auriculares",bg="black",fg="white")
    etiqueta.place(x=20, y=20)
    
    # Botón para agregar al carrito
    agregar = Button(info_Aud, text="Agregar", command=lambda: agregar_carrito("Auriculares"))
    agregar.place(x=320, y=230)
    
    # Botón para cerrar la ventana hija
    regresar = Button(info_Aud, text="Cerrar", command=info_Aud.destroy)
    regresar.place(x=20, y=230)

# Función para mostrar la ventana de pago
def crear_vent_pag():
    global usuario_actual
    if not usuario_actual:
        messagebox.showerror("Error", "Debe iniciar sesión antes de realizar un pago.")
        return

    vent_pag = Toplevel(lista_productos)
    vent_pag.title("Motor de pago")
    vent_pag.geometry("600x400")
    vent_pag.configure(bg="black")

    titulo = Label(vent_pag, text="Motor de pago", bg="black", fg="white")
    titulo.place(x=250, y=10)
    Label(vent_pag, text="Ingrese los datos de la tarjeta:", bg="black", fg="white").place(x=1, y=25)

    name = Label(vent_pag, text="Nombre Propietario:", bg="grey")
    name.place(x=10, y=60)
    nomtj = Entry(vent_pag, width=50)
    nomtj.place(x=170, y=60)

    direc = Label(vent_pag, text="Dirección registrada:", bg="grey")
    direc.place(x=10, y=100)
    directj = Entry(vent_pag, width=50)
    directj.place(x=170, y=100)

    numt = Label(vent_pag, text="Número de tarjeta:", bg="grey")
    numt.place(x=10, y=140)
    numtj = Entry(vent_pag, width=30)
    numtj.place(x=170, y=140)

    fecht = Label(vent_pag, text="Fecha de tarjeta:", bg="grey")
    fecht.place(x=10, y=180)
    fechtj = Entry(vent_pag, width=10)
    fechtj.place(x=170, y=180)

    digt = Label(vent_pag, text="Dígitos de seguridad:", bg="grey")
    digt.place(x=260, y=180)
    digtj = Entry(vent_pag, width=5)
    digtj.place(x=410, y=180)

   # Cálculo del total del carrito
    total = 0
    for id_producto, datos in carrito.items():
        precio = datos["precio"]
        cantidad = datos["cantidad"]
        total += precio * cantidad

    # Mostrar total en la ventana de pago
    total_label = Label(vent_pag, text=f"Total a pagar: ${total:.2f}", font=("Arial", 15), bg="black", fg="white")
    total_label.place(x=200, y=250)


    def confirmar_pago():
        global carrito
        tj_nom = nomtj.get()
        tj_dir = directj.get()
        tj_num = numtj.get()
        tj_fech = fechtj.get()
        tj_dig = digtj.get()

        if not (tj_nom and tj_dir and tj_num and tj_fech and tj_dig):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        conexion = conectar()
        if conexion:
            try:
                cursor = conexion.cursor()

                # Inserta datos en datos_tarjeta
                cursor.execute(
                    "INSERT INTO datos_tarjeta(FK_ID_Usuario,Propietario,Direccion_Reg,Num_Tarjeta,Fecha_V,Dig_Seg) VALUES (%s,%s,%s,%s,%s,%s)",
                    (usuario_actual, tj_nom, tj_dir, tj_num, tj_fech, tj_dig)
                )

                # Inserta ticket
                cursor.execute(
                    "INSERT INTO ticket(FK_ID_Usuario,Total) VALUES (%s,%s)",
                    (usuario_actual,total)
                )

                ID_Ticket = cursor.lastrowid

                # Procesa los productos del carrito
                for id_producto, datos in carrito.items():
                    cantidad = datos["cantidad"]
                    total_producto = datos["precio"] * cantidad

                    # Verificar stock disponible
                    cursor.execute("SELECT Stock FROM producto WHERE ID_Producto = %s", (id_producto,))
                    stock_disponible = cursor.fetchone()

                    if stock_disponible is None:
                        messagebox.showerror("Error", f"El producto con ID {id_producto} no existe.")
                        conexion.rollback()
                        return

                    if stock_disponible[0] < cantidad:
                        messagebox.showerror("Error", f"No hay suficiente stock para el producto con ID {id_producto}. Stock disponible: {stock_disponible[0]}.")
                        conexion.rollback()
                        return

                    # Inserta el producto en la tabla carrito
                    cursor.execute(
                        "INSERT INTO carrito (FK_ID_Ticket,FK_ID_Usuario, FK_ID_Producto, Cantidad, Total) VALUES (%s, %s, %s, %s, %s)",
                        (ID_Ticket, usuario_actual, id_producto, cantidad, total_producto)
                    )

                    # Actualiza el stock del producto en la tabla productos
                    cursor.execute(
                        "UPDATE producto SET Stock = Stock - %s WHERE ID_Producto = %s",
                        (cantidad, id_producto)
                    )

                # Confirma los cambios
                conexion.commit()
                messagebox.showinfo("Pago", "Pago realizado con éxito. Los datos se han registrado y el stock se ha actualizado.")
                vent_pag.destroy()

            except mariadb.Error as e:
                messagebox.showerror("Error", f"Error al guardar los datos del pago: {e}")
                conexion.rollback()
            finally:
                conexion.close()


    confirmar = Button(vent_pag, text="Confirmar", command=confirmar_pago)
    confirmar.place(x=20, y=350)

    regresar = Button(vent_pag, text="Cerrar", command=vent_pag.destroy)
    regresar.place(x=500, y=350)

# Función para cerrar sesión
def cerrar_sesion():
    global usuario_actual
    if usuario_actual:
        usuario_actual = None
        messagebox.showinfo("Cerrar Sesión", "Has cerrado sesión exitosamente.")
    else:
        messagebox.showwarning("Cerrar Sesión", "No hay ningún usuario iniciado.")

# Crear la ventana principal
lista_productos = Tk()
lista_productos.title("Mike's")
lista_productos.geometry("800x600")
lista_productos.configure(bg="white")

# Crear una franja horizontal
franja_Horizontal = Frame(lista_productos, height=50, bg="darkblue", width=800)
franja_Horizontal.place(x=0, y=0)

# Crear una franja vertical
franja_Vertical = Frame(lista_productos, height=500, bg="beige", width=210)
franja_Vertical.place(x=590, y=50)

#Crear franja contacto
franja_contacto = Frame(lista_productos, height=100, width=210, bg="grey")
franja_contacto.place(x=590,y=500)

# título en la franja
Mensaje_B = Label(franja_Horizontal, text="Bienvenido a Mike's Store", bg="darkblue", fg="white", font=("Arial", 16))
Mensaje_B.place(x=60, y=10)

# Contacto en la franja
Inf_Cont= Label(franja_contacto, text="Número telefonico y Whatsapp:", bg="grey",fg="white")
Inf_Cont.place(x=2,y=2)

Num_Cont= Label(franja_contacto, text="5566956608", bg="grey",fg="black", font=("Arial",16))
Num_Cont.place(x=30,y=35)

# Mostrar carrito
label_carrito = Label(lista_productos, text="Carrito de compras: ", bg="beige", font=("Arial",12))
label_carrito.place(x=600, y=60)

carrito_text = Text(lista_productos, height=10, width=20)
carrito_text.place(x=600, y=90)

# Botón de iniciar sesión en la ventana de pago
Button(lista_productos, text="Iniciar Sesión", command=iniciar_sesion).place(x=600, y=15)

# Botón de registrarse en la ventana principal
Button(lista_productos, text="Registrarse", command=registrarse).place(x=700, y=15)

# Botones para productos
producto_1 = Button(lista_productos, text="Pantalla", command=crear_info_Pantalla)
producto_1.place(x=150, y=210)

producto_2 = Button(lista_productos, text="Teléfono", command=crear_info_Tel)
producto_2.place(x=400, y=210)

producto_3 = Button(lista_productos, text="Tablet", command=crear_info_Tab)
producto_3.place(x=150, y=370)

producto_4 = Button(lista_productos, text="Audiculares", command=crear_info_Aud)
producto_4.place(x=400, y=370)

#Imagen

Logo=Image.open("logo.png").convert("RGBA")
Logo=Logo.resize((40,40))
ImgL=ImageTk.PhotoImage(Logo)
Label(lista_productos, image=ImgL, bg="darkblue").place(x=5,y=2)

img=Image.open("Pantalla1.jpg")
img=img.resize((150,100))
imgP=ImageTk.PhotoImage(img)
Label(lista_productos, image=imgP).place(x=100,y=100)

img2=Image.open("smartphone.jpg")
img2=img2.resize((150,100))
imgT=ImageTk.PhotoImage(img2)
Label(lista_productos, image=imgT).place(x=350,y=100)

img3=Image.open("Tab.jpg")
img3=img3.resize((150,100))
imgTa=ImageTk.PhotoImage(img3)
Label(lista_productos, image=imgTa).place(x=100,y=260)

img4=Image.open("aud.jpg")
img4=img4.resize((150,100))
imgA=ImageTk.PhotoImage(img4)
Label(lista_productos, image=imgA).place(x=350,y=260)

# Botón para pagar
pagar = Button(lista_productos, text="Pagar", command=crear_vent_pag)
pagar.place(x=600, y=280)

# Botón para cerrar sesion
pagar = Button(lista_productos, text="Cerrar Sesion", bg="red", fg="white", command=cerrar_sesion)
pagar.place(x=650, y=280)

# Crear botón para vaciar el carrito
boton_vaciar_carrito = Button(lista_productos, text="Vaciar Carrito", bg="grey", fg="white", command=vaciar_carrito)
boton_vaciar_carrito.place(x=600, y=310)

# Establecer conexión y agregar productos
conexion = conectar()
if conexion:
    act(conexion)
    conexion.close()
else:
    print("No se pudo conectar a la base de datos")

lista_productos.mainloop()