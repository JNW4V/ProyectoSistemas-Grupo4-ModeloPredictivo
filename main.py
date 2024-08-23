import tkinter as tk
from tkinter import ttk
import re
from tkinter import messagebox
from PIL import Image, ImageTk
import pyodbc
import graficaBitcoin
import graficaEtherium
import graficaDogeCoin
import requestBitcoin
from tkcalendar import DateEntry
import modeloDeRecomendacionModificarCantidad
import threading
import time

class PantallaInicio:
    def __init__(self,conexion):
        self.conexion = conexion
        self.status = 1
        self.root = tk.Tk()
        self.root.title("Login")
        self.root.geometry("480x500")
        self.root.configure(bg = '#333333')
        
        #Centrar la ventana
        self.center_window(480, 500)
        

        self.image = Image.open("Desktop\\proyecto\\imagenes\\logo.png")
        self.image = self.image.resize((100, 100))
        self.photo = ImageTk.PhotoImage(self.image)  
        self.root.iconphoto(False, self.photo)
        self.frame = tk.Frame(bg = '#333333')
        self.labelTitulo = tk.Label(self.frame, text = "Login",bg = '#333333', fg = '#FF3399', font = ("New Times Roman", 30, "bold"))
        self.labelUsuario = tk.Label(self.frame, text = "Usuario o Correo",bg = '#333333', fg = 'white',font = ("New Times Roman", 14, ))
        self.labelContra = tk.Label(self.frame, text = "Contraseña",bg = '#333333' , fg = 'white',font = ("New Times Roman", 14))
        self.NombreEntry = tk.Entry(self.frame,font = ("New Times Roman", 14))
        self.ContraEntry = tk.Entry(self.frame, show = "*",font = ("New Times Roman", 14) )
        self.boton = tk.Button(self.frame, text = "Ingresar", command= lambda: self.login(self.NombreEntry.get(), self.ContraEntry.get(),self.conexion), 
                  bg = '#FF3399', fg = 'white',font = ("New Times Roman", 14, "bold"))
        self.registrarseButton = tk.Button(self.frame, text = "Registrarse", command= lambda: VentanaRegistro(self.conexion),
                              bg = '#FF3399', fg = 'white',font = ("New Times Roman", 14))
        
        self.frame.pack(expand = True)

        self.labelTitulo.grid(row = 0, column= 0, columnspan= 2, pady = 20, padx = 20)
        self.labelUsuario.grid(row = 3, column = 0)
        self.NombreEntry.grid(row = 3, column = 1,pady = 10)
        self.labelContra.grid(row = 4, column = 0)
        self.ContraEntry.grid(row = 4, column = 1, pady = 10)
        self.boton.grid(row = 5, column = 0, columnspan=2, padx = 20, pady =  20)
        self.registrarseButton.grid(row = 6, column = 0,columnspan=2, pady =  20, padx = 20)
        
        self.root.mainloop()

    def login(self,nombre, contra,conexion):
        bandera = False
        cursor = conexion.cursor() 
        cursor.execute("SELECT * FROM users;")
        if nombre == "" or contra == "":
            messagebox.showerror("Error", "Campos vacios")
        else:
            persona = cursor.fetchone()
            while persona:
                if((persona[1] == nombre or persona[3] == nombre) and persona[2] == contra):
                    bandera = True
                    break
                persona = cursor.fetchone()
                 
            if(bandera):
                messagebox.showinfo("Login success", "Bienvenido")
                self.root.destroy()

                PantallaEscoger(self.conexion, persona[0])
            else:
                messagebox.showinfo("Error", "Usuario o contraseña incorrecta")
        cursor.close()
    def center_window(self, width, height):
        # Obtener el tamaño de la pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calcular la posición x e y
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        # Establecer la geometría de la ventana
        self.root.geometry(f'{width}x{height}+{x}+{y}')
   


class VentanaRegistro:
    def __init__(self,conexion):
        self.ventanaRegistro = tk.Toplevel()
        self.ventanaRegistro.title("Registro")
        self.conexion = conexion
        self.ventanaRegistro.geometry("480x300")
        self.ventanaRegistro.configure(bg = '#333333')

        self.center_window(480, 500)

        try:
            image = Image.open("Desktop\\proyecto\\imagenes\\logo.png")
            image = image.resize((100, 100))
            photo = ImageTk.PhotoImage(image)
            self.ventanaRegistro.iconphoto(False, photo)
        except Exception as e:
            print(f"Error al cargar la imagen: {e}")

        self.frameRegistro = tk.Frame(self.ventanaRegistro,bg = '#333333')
        self.frameRegistro.pack()
        self.labelUsuario = tk.Label(self.frameRegistro, text = "Usuario",bg = '#333333', 
                           fg = 'white',font = ("New Times Roman", 14))
        self.usuarioEntry = tk.Entry(self.frameRegistro,font = ("New Times Roman", 14))
        self.labelCorreo = tk.Label(self.frameRegistro, text = "Correo",bg = '#333333',
                           fg = 'white',font = ("New Times Roman", 14))
        self.correoEntry = tk.Entry(self.frameRegistro, font = ("New Times Roman", 14))
        self.labelContra = tk.Label(self.frameRegistro, text = "Contraseña",bg = '#333333',
                           fg = 'white',font = ("New Times Roman", 14) )
        self.ContraEntry = tk.Entry(self.frameRegistro, font = ("New Times Roman", 14) )
        self.LabelNombre = tk.Label(self.frameRegistro, text = "Nombre",bg = '#333333', fg = 'white', font = ("New Times Roman", 14))
        self.NombreEntry = tk.Entry(self.frameRegistro,font = ("New Times Roman", 14))
        self.LabelApellido = tk.Label(self.frameRegistro, text ="Apellido", bg = '#333333', fg = 'white', font = ("New Times Roman", 14))
        self.ApellidoEntry = tk.Entry(self.frameRegistro,font = ("New Times Roman", 14))
        self.LabelNacimiento = tk.Label(self.frameRegistro, text = "Fecha de nacimiento",bg = '#333333', fg = 'white', font = ("New Times Roman", 14))
        self.Nacimiento = DateEntry(self.frameRegistro, width=33, background='darkblue',
                        borderwidth=2,date_pattern='yyyy-MM-DD')
        self.botonGuardar = tk.Button(self.frameRegistro, text= "Registrar", command= lambda: self.registrar(self.usuarioEntry.get(), self.correoEntry.get(), self.ContraEntry.get(), self.NombreEntry.get(), self.ApellidoEntry.get(), self.Nacimiento.get()), bg = '#FF3399', fg = 'white', font = ("New Times Roman", 14))
        self.a = tk.Label(self.frameRegistro, text = "Registro",bg = '#333333', fg = '#FF3399', font = ("New Times Roman", 30,"bold"))
        
        self.a.grid(row= 0, column = 0, pady = 50, padx = 40, columnspan = 2)
        self.labelUsuario.grid(row = 1, column = 0, padx = 20)
        self.usuarioEntry.grid(row = 1, column = 1, pady = 10)
        self.LabelNombre.grid(row = 2, column = 0, padx = 20)
        self.NombreEntry.grid(row = 2, column = 1, pady = 10)
        self.LabelApellido.grid(row = 3, column = 0, padx = 20)
        self.ApellidoEntry.grid(row = 3, column = 1, pady = 10)
        self.LabelNacimiento.grid(row = 4, column = 0, padx = 20)
        self.Nacimiento.grid(row = 4, column = 1, pady = 10)
        self.labelCorreo.grid(row= 5, column = 0)
        self.correoEntry.grid(row = 5, column = 1, pady = 10)
        self.labelContra.grid(row = 6, column = 0)
        self.ContraEntry.grid(row = 6, column = 1, pady = 10)
        self.botonGuardar.grid(row = 7, column = 1, pady = 30 )

    def registrar(self,usuario, correo, contra, primerN, segundoN, nacimiento):
        flag = False
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if re.match(email_pattern, correo):
            cursorInsert = self.conexion.cursor()
            cursorInsert.execute("SELECT * FROM users;")
            persona = cursorInsert.fetchone()
            while (persona and not flag):
                if(persona[2] == correo):
                    flag = True
                    break
                persona = cursorInsert.fetchone()
            if(flag):
                messagebox.showerror("Error", "Correo ya registrado")
            else:
                consulta = f"INSERT INTO users (username, password_hash, email, first_name, last_name, date_of_birth, is_active) VALUES ('{usuario}','{contra}', '{correo}','{primerN}','{segundoN}','{nacimiento}', 1);"
                cursorInsert.execute(consulta)
                self.conexion.commit()
                cursorInsert.close()
                messagebox.showinfo("Registro", "Usuario registrado con exito")
                self.ventanaRegistro.destroy()
        else:
            messagebox.showerror("Error", "Correo invalido")
        
        
        
    def center_window(self, width, height):
        # Obtener el tamaño de la pantalla
        screen_width = self.ventanaRegistro.winfo_screenwidth()
        screen_height = self.ventanaRegistro.winfo_screenheight()

        # Calcular la posición x e y
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        # Establecer la geometría de la ventana
        self.ventanaRegistro.geometry(f'{width}x{height}+{x}+{y}')


class PantallaRecomendacion:
    def __init__(self,conexion, id):
        self.conexion = conexion
        self.id = id
        self.stop_threads = False
        self.main_window = tk.Tk()
        image_path = "Desktop\\proyecto\\imagenes\\goat.ico"
        self.main_window.iconbitmap(image_path) 
        self.main_window.title("Panel Principal")
        self.main_window.configure(bg = '#333333')
        self.center_window(500, 400)        


        #Frame Principal
        self.frame = tk.Frame(self.main_window, bg = '#333333')
        self.frame.pack(fill = tk.BOTH, expand= True)
        #Frame superior
        self.FrameSuperior = tk.Frame(self.frame, bg = '#333333', bd = 2,  relief=tk.SOLID)
        self.FrameSuperior.pack(fill = tk.BOTH, expand= True)
        
       
        
        

        """Creacion de los widgets superior"""
        self.Titulo = tk.Label(self.FrameSuperior, text = "DEJE QUE LA IA SE ENCARGE",font = ("New Times Roman", 16, "bold"),bg = '#333333', fg = '#FF3399')
        self.labelCantidadI = tk.Label(self.FrameSuperior, text = "Cantidad", bg = '#333333', fg = '#FF3399', font = ("New Times Roman", 12))
        self.CantidadI = tk.Entry(self.FrameSuperior)
        self.BotonComenzarI = tk.Button (self.FrameSuperior, text = "Iniciar",command= lambda: self.comenzar_ia_thread(self.escogerTabla.get(),self.CantidadI.get(),id), bg = '#FF3399', fg = 'white', font = ("New Times Roman", 12))
        self.escogerMoneda = tk.Label(self.FrameSuperior, text = "Moneda", bg = '#333333', fg = '#FF3399', font = ("New Times Roman", 12))
        self.escogerTabla = ttk.Combobox(self.FrameSuperior, state = "readonly", values = ["BitCoin","Etherium", "Dogecoin"])
        self.Detener = tk.Button(self.FrameSuperior, text = "Detener", command = lambda: self.detener, bg = '#FF3399', fg = 'white', font = ("New Times Roman", 12))
        self.botonRegresar = tk.Button(self.FrameSuperior, text = "Regresar", command = lambda: self.regresar(), bg = '#FF3399', fg = 'white', font = ("New Times Roman", 10))
        self.labelBotonGrafica = tk.Button(self.FrameSuperior, text = "Grafica", command= lambda: self.mostrarGrafica(self.escogerTabla.get()))
        
        #Aparcion de los widgets
        self.Titulo.grid(row = 0, column = 1, pady = 10, columnspan= 2)
        self.labelCantidadI.grid(row = 1, column = 0, pady= 10, padx = 10)
        self.CantidadI.grid(row = 1, column = 1, columnspan = 2, pady = 20)
        self.escogerMoneda.grid(row = 2, column= 0)
        self.escogerTabla.grid(row = 2, column= 1, columnspan= 2, pady = 10)
        self.labelBotonGrafica.grid(row = 2, column = 2, columnspan = 2, pady = 20)
        self.BotonComenzarI.grid(row =3, column = 1, columnspan = 2, pady = 20)
        self.botonRegresar.grid(row = 4, column = 0, columnspan = 3, pady = 20)
        self.Detener.grid(row = 4, column = 3, columnspan = 1 )
        self.main_window.mainloop()

    def detener(self):
        self.stop_threads = True
        if self.thread.is_alive():
            self.thread.join()
        print("Proceso detenido por el usuario.")
    def regresar(self):
        self.main_window.destroy()
        PantallaEscoger(self.conexion, self.id)
    def center_window(self, width, height):
        # Obtener el tamaño de la pantalla
        screen_width = self.main_window.winfo_screenwidth()
        screen_height = self.main_window.winfo_screenheight()

        # Calcular la posición x e y
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        # Establecer la geometría de la ventana
        self.main_window.geometry(f'{width}x{height}+{x}+{y}')
    def mostrarGrafica(self, moneda):
        
        if(moneda == "BitCoin"):
            graficaBitcoin.mostrar_grafico_btc()
        elif(moneda == "Etherium"):
            graficaEtherium.mostrar_grafico_etherium()
        elif(moneda == "Dogecoin"):
            graficaDogeCoin.mostrar_grafico_dogeCoin()
        else:
            messagebox.showerror("Error", "Escoja una moneda")
    def iniciarIA(self, moneda, cantidad,user_id):
        cantidad = float(cantidad)
        
        try:
            con = self.conexion
            cursor = con.cursor()
            if(moneda == "BitCoin"):
                
                cursor.execute(f"INSERT INTO initial_balances (user_id, currency_id, initial_amount) VALUES ({self.id},1, {cantidad})")
                cursor.commit()          
                messagebox.showinfo("Exito", "Cantidad insertada con exito")
                self.comprobarCantidad(1, cantidad)      
                self.main_Bitcoin(cantidad,0.1, con, user_id)
                
            elif(moneda == "Etherium"):
                cursor.execute(f"INSERT INTO initial_balances (user_id, currency_id, initial_amount) VALUES ({self.id},3, {cantidad})")
                cursor.commit()    
                messagebox.showinfo("Exito", "Cantidad insertada con exito")
                self.comprobarCantidad(3, cantidad)
                self.main_Etherium(cantidad,0.1, con,user_id)
            elif(moneda == "Dogecoin"):
                cursor.execute(f"INSERT INTO initial_balances (user_id, currency_id, initial_amount) VALUES ({self.id},8, {cantidad})")
                cursor.commit()
                messagebox.showinfo("Exito", "Cantidad insertada con exito")
                self.comprobarCantidad(8, cantidad)
                self.main_dogecoin(cantidad,0.1, con, user_id)   
            else:
                messagebox.showerror("Error", "Escoja una una moneda y/o cantidad")

        except Exception as e:
            con.rollback()
            messagebox.showerror("Error", f"Error al insertar datos: {e}")
    
        finally:
            if con and not con.closed:
                con.close() 

    def comenzar_ia_thread(self, moneda, cantidad, user_id):
        self.stop_threads = False
        if not moneda:
            messagebox.showerror("Error", "Escoja una moneda")
            return
        if not cantidad:
            messagebox.showerror("Error", "Digite la cantidad")
            return
        try:
            cantidad = float(cantidad)
        except ValueError:
            messagebox.showerror("Error", "Cantidad inválida")
            return
        thread = threading.Thread(target=self.iniciarIA, args=(moneda, cantidad, user_id))
        thread.start()

    def comprobarCantidad(self, moneda_id, cantidad):
        cursor = self.conexion.cursor()
        try:
            cursor.execute(f"SELECT current_amount FROM current_balances WHERE user_id = ? AND currency_id = ?", (self.id, moneda_id))
            cantidad_actual = cursor.fetchone()
            
            if cantidad_actual is not None:    
                cursor.execute("""
                    UPDATE current_balances
                    SET current_amount = ?, update_at = GETDATE()
                    WHERE user_id = ? AND currency_id = ?
                """, (cantidad, self.id, moneda_id))
            else:
                cursor.execute(f"INSERT INTO current_balances (user_id, currency_id, current_amount) VALUES ({self.id},{moneda_id}, {cantidad})")
           
            self.conexion.commit()
        except Exception as e:
            self.conexion.rollback()
            print(f"Error al insertar datos: {e}")
        finally:    
            cursor.close()
    def main_Bitcoin(self,initial_capital, percentage, conexion,user_id):
        symbol = 'BTCUSD'
        exchange = 'BINANCE'
        interval = modeloDeRecomendacionModificarCantidad.Interval.in_daily
        n_bars = 100
        rsi_window = 14
        rsi_oversold = 48
        rsi_overbought = 70

        try:
            while not self.stop_threads:
                data = modeloDeRecomendacionModificarCantidad.get_crypto_data(symbol, exchange, interval, n_bars)
                data['RSI'] = modeloDeRecomendacionModificarCantidad.calculate_rsi(data, window=rsi_window)
                
                data = modeloDeRecomendacionModificarCantidad.simulate_trading(data, initial_capital, rsi_oversold, rsi_overbought,conexion, user_id)

                current_rsi = data['RSI'].iloc[-1]
                print(f"Current RSI: {current_rsi:.2f}")

                price = modeloDeRecomendacionModificarCantidad.get_current_price(symbol)
                modeloDeRecomendacionModificarCantidad.save_price_to_db(1, price, conexion)
                if current_rsi < rsi_oversold:
                    print("Recommendation: It's a good time to buy.")
                    amount = modeloDeRecomendacionModificarCantidad.calculate_amount(initial_capital, percentage, price)
                    modeloDeRecomendacionModificarCantidad.buy_crypto(1, amount, price, conexion, initial_capital, user_id)  # Ejecuta una orden de compra
                elif current_rsi > rsi_overbought:
                    print("Recommendation: It's a good time to sell.")
                    amount = modeloDeRecomendacionModificarCantidad.calculate_amount(initial_capital, percentage, price)
                    modeloDeRecomendacionModificarCantidad.sell_crypto(1, amount,price,conexion, user_id)   # Ejecuta una orden de venta
                else:
                    print("Recommendation: Hold.")
                time.sleep(60)
                if self.stop_threads:
                    return

        except KeyboardInterrupt:
            print("Proceso interrumpido por el usuario.")
        except Exception as e:
            print(f"Error en main_Bitcoin: {e}")
        finally:
            if not conexion.closed:
                conexion.close()
    def main_Etherium(self, initial_capital, porcentage, conexion, user_id):
        symbol = 'ETHUSD'
        exchange = 'BINANCE'
        interval = modeloDeRecomendacionModificarCantidad.Interval.in_daily
        n_bars = 100
        rsi_window = 14
        rsi_oversold = 50
        rsi_overbought = 70
        try:
            while not self.stop_threads:

                data = modeloDeRecomendacionModificarCantidad.get_crypto_data(symbol, exchange, interval, n_bars)
                data['RSI'] = modeloDeRecomendacionModificarCantidad.calculate_rsi(data, window=rsi_window)

                data = modeloDeRecomendacionModificarCantidad.simulate_trading(data, initial_capital, rsi_oversold, rsi_overbought,conexion, 3)

                current_rsi = data['RSI'].iloc[-1]
                print(f"Current RSI: {current_rsi:.2f}")

            
                price = modeloDeRecomendacionModificarCantidad.get_current_price(symbol)
                modeloDeRecomendacionModificarCantidad.save_price_to_db(3, price, conexion)
                if current_rsi < rsi_oversold:
                    print("Recommendation: It's a good time to buy.")
                    amount = modeloDeRecomendacionModificarCantidad.calculate_amount(initial_capital, porcentage, price)
                    modeloDeRecomendacionModificarCantidad.buy_crypto(3, amount, price, conexion, initial_capital, user_id)  # Ejecuta una orden de compra
                elif current_rsi > rsi_overbought:
                    print("Recommendation: It's a good time to sell.")
                    amount = modeloDeRecomendacionModificarCantidad.calculate_amount(initial_capital, porcentage, price)
                    modeloDeRecomendacionModificarCantidad.sell_crypto(3, amount,price,conexion, user_id)   # Ejecuta una orden de venta
                else:
                    print("Recommendation: Hold.")
                time.sleep(60)
                if self.stop_threads:
                    return
        except KeyboardInterrupt:
            print("Proceso interrumpido por el usuario.")
        except Exception as e:
            print(f"Error en main_Bitcoin: {e}")
        finally:
            if not conexion.closed:
                conexion.close()

    def main_dogecoin(self, initial_capital, percentage, conexion, user_id, ):
        symbol = 'DOGEUSD'
        exchange = 'BINANCE'
        interval = modeloDeRecomendacionModificarCantidad.Interval.in_daily
        n_bars = 100
        rsi_window = 14
        rsi_oversold = 50
        rsi_overbought = 70

        try:
            while not self.stop_threads:
                data = modeloDeRecomendacionModificarCantidad.get_crypto_data(symbol, exchange, interval, n_bars)
                data['RSI'] = modeloDeRecomendacionModificarCantidad.calculate_rsi(data, window=rsi_window)

                data = modeloDeRecomendacionModificarCantidad.simulate_trading(data, initial_capital, rsi_oversold, rsi_overbought, conexion, 8)

                current_rsi = data['RSI'].iloc[-1]
                print(f"Current RSI: {current_rsi:.2f}")

                price = modeloDeRecomendacionModificarCantidad.get_current_price(symbol)
                modeloDeRecomendacionModificarCantidad.save_price_to_db(8, price, conexion)
                if current_rsi < rsi_oversold:
                    print("Recommendation: It's a good time to buy.")
                    amount = modeloDeRecomendacionModificarCantidad.calculate_amount(initial_capital, percentage, price)
                    modeloDeRecomendacionModificarCantidad.buy_crypto(8, amount, price, conexion, initial_capital, user_id)  # Ejecuta una orden de compra
                elif current_rsi > rsi_overbought:
                    print("Recommendation: It's a good time to sell.")
                    amount = modeloDeRecomendacionModificarCantidad.calculate_amount(initial_capital, percentage, price)
                    modeloDeRecomendacionModificarCantidad.sell_crypto(8, amount,price,conexion, user_id)  # Ejecuta una orden de venta
                else:
                    print("Recommendation: Hold.")
                time.sleep(60)
                if self.stop_threads:
                    return
        except KeyboardInterrupt:
            print("Proceso interrumpido por el usuario.")
        except Exception as e:
            print(f"Error en main_Bitcoin: {e}")
        finally:
            if not conexion.closed:
                conexion.close()
class PantallaEscoger:
    def __init__(self, conexion, id):
        self.conexion = conexion
        self.id = id
        self.PantallaEscoger = tk.Tk()
        image_path = "Desktop\\proyecto\\imagenes\\goat.ico"
        self.PantallaEscoger.iconbitmap(image_path) 
        self.PantallaEscoger.title("Producto") 
        self.center_window(480,500)
        self.PantallaEscoger.configure(bg= '#333333')
        self.FrameEscoger = tk.Frame(self.PantallaEscoger,bg = '#333333')
        self.LabelOpciones = tk.Label(self.FrameEscoger, text = "OPCIONES",bg = '#333333', fg = '#FF3399', font = ("New Times Roman", 20,"bold"))
        self.labelRecomedacion = tk.Button(self.FrameEscoger,bg = '#FF3399', fg = 'white', text = "Recomendacion",font = ("New Times Roman", 12,"bold"), command = self.iniciarPantallaRecomendacion)
        self.labelRevisar = tk.Button(self.FrameEscoger, bg = '#FF3399', fg = 'white', text = "Revisar estado de cuenta",font = ("New Times Roman", 12,"bold"), command= self.iniciarPantallaRevisarEstado)
        self.CerrarSesion = tk.Button(self.FrameEscoger, text = "Cerrar Sesion", command = lambda: self.cerrarSesion(), bg = '#FF3399', fg = 'white', font = ("New Times Roman", 12, "bold"))
        
        self.FrameEscoger.pack()
        self.LabelOpciones.grid(row= 0, column = 0, pady = 20, padx = 20, columnspan = 2)
        self.labelRecomedacion.grid( row = 1, column = 0, pady = 100, padx = 20)
        self.labelRevisar.grid(row = 1, column = 1, pady = 100, padx = 20)
        self.CerrarSesion.grid(row = 2, column = 0, columnspan = 2, pady = 20)

    
    def cerrarSesion(self):
        self.PantallaEscoger.destroy()
        PantallaInicio(self.conexion)
    def iniciarPantallaRecomendacion(self):
        self.PantallaEscoger.destroy()
        PantallaRecomendacion(self.conexion, self.id)
        
        

    def iniciarPantallaRevisarEstado(self):

        PantallaRevisarCuenta(self.id, self.conexion)
        self.PantallaEscoger.destroy()


    def center_window(self, width, height):
        # Obtener el tamaño de la pantalla
        screen_width = self.PantallaEscoger.winfo_screenwidth()
        screen_height = self.PantallaEscoger.winfo_screenheight()

        # Calcular la posición x e y
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        # Establecer la geometría de la ventana
        self.PantallaEscoger.geometry(f'{width}x{height}+{x}+{y}')

    
class PantallaRevisarCuenta():
    

    def __init__(self, id, conexion):
        
        self.id = id
        self.conexion = conexion
        self.PantallaRevisar = tk.Tk()
        self.center_window(480,500)
        image_path = "Desktop\\proyecto\\imagenes\\goat.ico"
     
        self.PantallaRevisar.iconbitmap(image_path) 
        self.PantallaRevisar.configure(bg= '#333333')
        self.FrameRevisar = tk.Frame(self.PantallaRevisar,bg = '#333333')
        self.LabelRevisar = tk.Label(self.FrameRevisar, text = "Estado de cuenta",bg = '#333333', fg = '#FF3399', font = ("New Times Roman", 20,"bold"))
        self.LabelDineroInicial = tk.Label(self.FrameRevisar, text = "Dinero Inicial",bg = '#333333', fg = 'white', font = ("New Times Roman", 14))
        self.CantidadInicial = tk.Label(self.FrameRevisar, text = f"{self.obtenerCantidadInicial(self.conexion)}", bg = '#333333', fg = 'white')
        self.LabelDinerodActual = tk.Label(self.FrameRevisar, text = "Dinero Actual", bg = '#333333', fg = 'white', font = ("New Times Roman", 14))
        self.CantidadActual = tk.Label(self.FrameRevisar,  text = f"{self.obtenerCantidadActual(self.conexion)}", bg = '#333333', fg = 'white')
        self.LabelGanancia = tk.Label(self.FrameRevisar, text = "Ganancia", bg = '#333333', fg = 'white', font = ("New Times Roman", 14))
        self.MostrarGanancia = tk.Label(self.FrameRevisar, text = f"{self.obtenerGanancia(self.conexion)}%", bg = '#333333', fg = 'white')
        self.BotonRegresar = tk.Button(self.FrameRevisar, text = "Regresar", command = lambda: self.regresar(), bg = '#FF3399', fg = 'white', font = ("New Times Roman", 12, "bold"))
        
        self.FrameRevisar.pack()
        self.LabelRevisar.grid(row= 0, column = 0, pady = 20, padx = 20, columnspan = 2)
        self.LabelDineroInicial.grid(row = 1, column = 0, pady = 20, padx = 20)
        self.CantidadInicial.grid(row = 1, column = 1, pady = 20, padx = 20)
        self.LabelDinerodActual.grid(row = 2, column = 0, pady= 20, padx = 20)
        self.CantidadActual.grid(row = 2, column = 1, pady = 20, padx = 20)
        self.LabelGanancia.grid(row = 3, column = 0, pady = 20, padx = 20)
        self.MostrarGanancia.grid(row = 3, column = 1, pady = 20, padx = 20)

        self.BotonRegresar.grid(row = 4, column = 0, columnspan = 2, pady = 20, padx = 20)

        


    def center_window(self, width, height):
        # Obtener el tamaño de la pantalla
        screen_width = self.PantallaRevisar.winfo_screenwidth()
        screen_height = self.PantallaRevisar.winfo_screenheight()

        # Calcular la posición x e y
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        # Establecer la geometría de la ventana
        self.PantallaRevisar.geometry(f'{width}x{height}+{x}+{y}')
    def regresar(self):

        self.PantallaRevisar.destroy()
        PantallaEscoger(self.conexion, self.id)
    def comprobarConexion(self):
        if not self.conexion or self.conexion.closed:
            try:
                self.conexion = pyodbc.connect('DRIVER={SQL Server}; SERVER=DESKTOP-05H4Q3D\\TEW_SQLEXPRESS; DATABASE=proyectoSistemas; UID=soporte; PWD=123')
            except pyodbc.Error as e:
                print(f"Error al intentar conectarse: {e}")
    def obtenerCantidadInicial(self, conexion):

        try:
            if conexion.closed:
                conexion = pyodbc.connect('DRIVER={SQL Server}; SERVER=DESKTOP-05H4Q3D\\TEW_SQLEXPRESS; DATABASE=proyectoSistemas; UID=soporte; PWD=123')
            
            cursorConsulta = conexion.cursor()
            consulta = f"select initial_balances from accounts where user_id = {self.id} ORDER BY last_updated DESC "
            try:
                conexion = pyodbc.connect('DRIVER={SQL Server}; SERVER=DESKTOP-05H4Q3D\\TEW_SQLEXPRESS; DATABASE=proyectoSistemas; UID=soporte; PWD=123')
            except pyodbc.Error as e:
                return f"Error al conectar a la base de datos: {e}"

            cursorConsulta = conexion.cursor()
            consulta = f"select initial_balance from accounts where user_id = {self.id} ORDER BY last_updated DESC "
            cursorConsulta.execute(consulta)
            initial_amounts = cursorConsulta.fetchone()
            if initial_amounts:
                initial_amount = initial_amounts[0]
            else:
                initial_amount = "No se encontro deposito inicial"
        except:
            initial_amount = "Error al ejecutar la consulta"
            
        finally:
            cursorConsulta.close()
        return initial_amount
    def obtenerGanancia(self, conexion):
        try:
            inicial = float(self.obtenerCantidadInicial(conexion))
            actual = float(self.obtenerCantidadActual(conexion))
            if inicial == 0:
                return "La cantidad inicial no puede ser cero"
            
            request = "SELECT * FROM portfolio WHERE user_id = ? ORDER BY last_updated DESC"
            cursor = conexion.cursor()
            cursor.execute(request, (self.id))
            todo = cursor.fetchone()
            if todo is None:
                return "No se encontraron registros en el portfolio"
            
            amount = float(todo[3])
            value = float(todo[4])
            cursor.close()

            print(f"Initial amount: {inicial}")
            print(f"Current amount: {actual}")
            print(f"Amount: {amount}")
            print(f"Value: {value}")
            ganancia = ((actual + float(amount*value) )/inicial*100 - 100   )
        except ValueError:

            ganancia = "No se pudo calcular la ganancia"
        except Exception as e:
            ganancia = f"Error al obtener la ganancia: {e}"
    
        return ganancia

    def obtenerCantidadActual1(self, conexion):
        try:
            if conexion.closed:
                conexion = pyodbc.connect('DRIVER={SQL Server}; SERVER=DESKTOP-05H4Q3D\\TEW_SQLEXPRESS; DATABASE=proyectoSistemas; UID=soporte; PWD=123')
            
            cursorConsulta = conexion.cursor()
            inicial = float(self.obtenerCantidadInicial(conexion))
            actual = float(self.obtenerCantidadActual(conexion))
            if inicial == 0:
                return "La cantidad inicial no puede ser cero"
            
            request = "SELECT * FROM portfolio WHERE user_id = ? ORDER BY last_updated DESC"
            cursor = conexion.cursor()
            cursor.execute(request, (self.id))
            todo = cursor.fetchone()
            if todo is None:
                return "No se encontraron registros en el portfolio"
            
            amount = float(todo[3])
            value = float(todo[4])
            cursor.close()

            ganancia = ((actual + float(amount*value) )/100 - 100   )
        except ValueError:

            ganancia = "No se pudo calcular la ganancia"
        except Exception as e:
            ganancia = f"Error al obtener la ganancia: {e}"
    
        return ganancia

    def obtenerCantidadActual(self, conexion):
        try:
            if conexion.closed:
                conexion = pyodbc.connect('DRIVER={SQL Server}; SERVER=DESKTOP-05H4Q3D\\TEW_SQLEXPRESS; DATABASE=proyectoSistemas; UID=soporte; PWD=123')
            cursorConsulta = conexion.cursor()
            consulta = f"select current_balance from accounts where user_id = {self.id} ORDER BY last_updated DESC "
        
            cursorConsulta.execute(consulta)
            actual_amount = cursorConsulta.fetchone()
            if actual_amount:
                actual_amount = actual_amount[0]
            else:
                actual_amount = "No se encontro monto actual"
        except:
            actual_amount = "Error al ejecutar la consulta"
        finally:
            cursorConsulta.close()
        return actual_amount

def main():
    server = "DESKTOP-05H4Q3D\\TEW_SQLEXPRESS"
    bd = 'proyectoSistemas'
    usuario = 'soporte'
    contrasena = '123'

    try:

        conexion = pyodbc.connect('DRIVER={SQL Server}; SERVER='+server + '; DATABASE=' + bd + 
                                '; UID=' + usuario + '; PWD=' + contrasena)
        print('Conexion realizada con exito')
        PantallaInicio(conexion)

    except pyodbc.Error as e:
        print(f"Error al intentar conectarse: {e}")

if __name__ == "__main__":  
    main()
