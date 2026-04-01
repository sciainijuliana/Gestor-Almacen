from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QLineEdit, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QComboBox, QMessageBox
)
from conexion import conectar
import os
from datetime import datetime

def inicializar_tablas_produccion():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS produccion_stock (
        id INTEGER PRIMARY KEY,
        codigo TEXT,
        nombre TEXT,
        tipo TEXT,
        cantidad REAL
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS recetas (
        id INTEGER PRIMARY KEY,
        codigo TEXT,
        nombre TEXT
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS receta_detalle (
        id INTEGER PRIMARY KEY,
        receta_id INTEGER,
        codigo_materia TEXT,
        cantidad REAL
    )''')

    conn.commit()
    conn.close()


class ProduccionWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Producción")
        self.setGeometry(250, 250, 1000, 800)

        inicializar_tablas_produccion()

        layout = QVBoxLayout()
        self.tabs = QTabWidget()

        self.tab_stock = QWidget()
        self.tab_recetas = QWidget()
        self.tab_ingresar = QWidget()
        self.tab_stock_produccion = QWidget()

        self.tabs.addTab(self.tab_stock, "Stock Materia Prima")
        self.tabs.addTab(self.tab_recetas, "Recetas")
        self.tabs.addTab(self.tab_ingresar, "Ingresar Producto")
        self.tabs.addTab(self.tab_stock_produccion, "Stock Producido")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

        self.init_stock_tab()
        self.init_recetas_tab()
        self.init_ingresar_tab()
        self.init_stock_produccion_tab()


    # ----------- STOCK PRODUCCION ----------

    def init_stock_produccion_tab(self):
        layout = QVBoxLayout()

        self.tabla_stock_produccion = QTableWidget()
        self.tabla_stock_produccion.setColumnCount(4)
        self.tabla_stock_produccion.setHorizontalHeaderLabels(["Código", "Nombre", "Cantidad", "Eliminar"])
        layout.addWidget(self.tabla_stock_produccion)

        self.tab_stock_produccion.setLayout(layout)
        self.cargar_stock_produccion()

    def cargar_stock_produccion(self):
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT codigo, nombre FROM recetas")
        recetas = cursor.fetchall()

        cursor.execute("SELECT codigo, cantidad FROM produccion_stock")
        cantidades = {codigo: cant for codigo, cant in cursor.fetchall()}

        conn.close()

        self.tabla_stock_produccion.setRowCount(len(recetas))
        for fila, (codigo, nombre) in enumerate(recetas):
            cantidad = cantidades.get(codigo, 0)
            self.tabla_stock_produccion.setItem(fila, 0, QTableWidgetItem(codigo))
            self.tabla_stock_produccion.setItem(fila, 1, QTableWidgetItem(nombre))
            self.tabla_stock_produccion.setItem(fila, 2, QTableWidgetItem(str(cantidad)))

            btn_eliminar = QPushButton("Eliminar")
            btn_eliminar.clicked.connect(lambda _, cod=codigo: self.eliminar_producto_final(cod))
            self.tabla_stock_produccion.setCellWidget(fila, 3, btn_eliminar)


    def eliminar_producto_final(self, id_prod):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM produccion_stock WHERE id = ?", (id_prod,))
        conn.commit()
        conn.close()
        QMessageBox.information(self, "Eliminado", "Producto final eliminado correctamente")
        self.cargar_stock_produccion()


    # ---------------- STOCK ----------------
    def init_stock_tab(self):
        layout = QVBoxLayout()

        self.codigo_input = QLineEdit()
        self.codigo_input.setPlaceholderText("Código materia prima")
        layout.addWidget(self.codigo_input)

        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre materia prima")
        layout.addWidget(self.nombre_input)

        self.tipo_input = QComboBox()
        self.tipo_input.addItems(["gramos", "mililitros"])
        layout.addWidget(self.tipo_input)

        self.cantidad_input = QLineEdit()
        self.cantidad_input.setPlaceholderText("Cantidad inicial")
        layout.addWidget(self.cantidad_input)

        guardar_btn = QPushButton("Guardar materia prima")
        guardar_btn.clicked.connect(self.guardar_materia_prima)
        layout.addWidget(guardar_btn)

        self.codigo_ingreso_input = QLineEdit()
        self.codigo_ingreso_input.setPlaceholderText("Código materia prima")
        layout.addWidget(self.codigo_ingreso_input)

        self.cantidad_ingreso_input = QLineEdit()
        self.cantidad_ingreso_input.setPlaceholderText("Cantidad adquirida")
        layout.addWidget(self.cantidad_ingreso_input)

        ingreso_btn = QPushButton("Registrar ingreso")
        ingreso_btn.clicked.connect(self.registrar_ingreso)
        layout.addWidget(ingreso_btn)

        self.tabla_stock = QTableWidget()
        self.tabla_stock.setColumnCount(5)
        self.tabla_stock.setHorizontalHeaderLabels(["Código", "Nombre", "Tipo", "Cantidad", "Eliminar"])
        layout.addWidget(self.tabla_stock)

        self.tab_stock.setLayout(layout)
        self.cargar_stock()


    def cargar_stock(self):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, codigo, nombre, tipo, cantidad FROM materia_prima_stock")
        productos = cursor.fetchall()
        conn.close()

        self.tabla_stock.setRowCount(len(productos))
        for fila, p in enumerate(productos):
            id_prod, codigo, nombre, tipo, cantidad = p
            self.tabla_stock.setItem(fila, 0, QTableWidgetItem(codigo))
            self.tabla_stock.setItem(fila, 1, QTableWidgetItem(nombre))
            self.tabla_stock.setItem(fila, 2, QTableWidgetItem(tipo))
            self.tabla_stock.setItem(fila, 3, QTableWidgetItem(str(cantidad)))

            btn_eliminar = QPushButton("Eliminar")
            btn_eliminar.clicked.connect(lambda _, id=id_prod: self.eliminar_materia_prima(id))
            self.tabla_stock.setCellWidget(fila, 4, btn_eliminar)

    def guardar_materia_prima(self):
        codigo = self.codigo_input.text()
        nombre = self.nombre_input.text()
        tipo = self.tipo_input.currentText()
        try:
            cantidad = float(self.cantidad_input.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Ingrese una cantidad válida")
            return

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO materia_prima_stock (codigo, nombre, tipo, cantidad) VALUES (?, ?, ?, ?)",
                    (codigo, nombre, tipo, cantidad))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Éxito", "Materia prima guardada correctamente")
        self.codigo_input.clear()
        self.nombre_input.clear()
        self.cantidad_input.clear()

        self.cargar_stock()

    
    def registrar_ingreso(self):
        codigo = self.codigo_ingreso_input.text()
        try:
            cantidad = float(self.cantidad_ingreso_input.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Ingrese una cantidad válida")
            return

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("UPDATE materia_prima_stock SET cantidad = cantidad + ? WHERE codigo = ?", (cantidad, codigo))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Éxito", "Ingreso registrado correctamente")
        self.codigo_ingreso_input.clear()
        self.cantidad_ingreso_input.clear()
        self.cargar_stock()



    def eliminar_materia_prima(self, id_prod):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM produccion_stock WHERE id = ?", (id_prod,))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Eliminado", "Materia prima eliminada correctamente")
        self.cargar_stock()

    # ---------------- RECETAS ----------------
    def init_recetas_tab(self):
        layout = QVBoxLayout()

        self.codigo_receta_input = QLineEdit()
        self.codigo_receta_input.setPlaceholderText("Código receta")
        layout.addWidget(self.codigo_receta_input)

        self.nombre_receta_input = QLineEdit()
        self.nombre_receta_input.setPlaceholderText("Nombre producto final")
        layout.addWidget(self.nombre_receta_input)

        self.tabla_receta = QTableWidget()
        self.tabla_receta.setColumnCount(2)
        self.tabla_receta.setHorizontalHeaderLabels(["Materia prima", "Cantidad usada"])
        layout.addWidget(self.tabla_receta)
    
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["unidad", "peso"])
        layout.addWidget(QLabel("Tipo de producto"))
        layout.addWidget(self.combo_tipo)

        btn_agregar_fila = QPushButton("Agregar ingrediente")
        btn_agregar_fila.clicked.connect(self.agregar_fila_ingrediente)
        layout.addWidget(btn_agregar_fila)

        btn_guardar_receta = QPushButton("Guardar receta")
        btn_guardar_receta.clicked.connect(self.guardar_receta)
        layout.addWidget(btn_guardar_receta)

        self.tabla_lista_recetas = QTableWidget()
        self.tabla_lista_recetas.setColumnCount(4)
        self.tabla_lista_recetas.setHorizontalHeaderLabels(["Código", "Nombre", "Ver ingredientes", "Eliminar"])
        layout.addWidget(self.tabla_lista_recetas)

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["unitario", "peso"])
        layout.addWidget(QLabel("Tipo de producto"))
        layout.addWidget(self.combo_tipo)


        self.tab_recetas.setLayout(layout)
        self.cargar_lista_recetas()

    def agregar_fila_ingrediente(self):
        fila = self.tabla_receta.rowCount()
        self.tabla_receta.insertRow(fila)

        combo = QComboBox()
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT codigo, nombre FROM materia_prima_stock")
        productos = cursor.fetchall()
        conn.close()

        for codigo, nombre in productos:
            combo.addItem(f"{codigo} - {nombre}", codigo)

        self.tabla_receta.setCellWidget(fila, 0, combo)

        self.tabla_receta.setItem(fila, 1, QTableWidgetItem(""))

    def guardar_receta(self):
        codigo = self.codigo_receta_input.text()
        nombre = self.nombre_receta_input.text()
        tipo =self.combo_tipo.currentText()

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO recetas (codigo, nombre, tipo) VALUES (?, ?, ?)", 
                   (codigo, nombre, tipo))
        receta_id = cursor.lastrowid

        for fila in range(self.tabla_receta.rowCount()):
            combo = self.tabla_receta.cellWidget(fila, 0)
            if combo:
                codigo_materia = combo.currentData() 
            else:
                codigo_materia = ""

            cantidad_item = self.tabla_receta.item(fila, 1)
            cantidad = float(cantidad_item.text()) if cantidad_item and cantidad_item.text() else 0

            if codigo_materia and cantidad > 0:
                cursor.execute("INSERT INTO receta_detalle (receta_id, codigo_materia, cantidad) VALUES (?, ?, ?)",
                            (receta_id, codigo_materia, cantidad))

        conn.commit()
        conn.close()
        QMessageBox.information(self, "Éxito", "Receta guardada correctamente")
        self.codigo_receta_input.clear()
        self.nombre_receta_input.clear()
        self.tabla_receta.setRowCount(0)

        self.cargar_lista_recetas()
        self.cargar_recetas_combo() 

    def cargar_lista_recetas(self):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, codigo, nombre FROM recetas")
        recetas = cursor.fetchall()
        conn.close()

        self.tabla_lista_recetas.setRowCount(len(recetas))
        for fila, rec in enumerate(recetas):
            id_receta, codigo, nombre = rec

            self.tabla_lista_recetas.setItem(fila, 0, QTableWidgetItem(codigo))
            self.tabla_lista_recetas.setItem(fila, 1, QTableWidgetItem(nombre))

            btn_ver = QPushButton("Ver ingredientes")
            btn_ver.clicked.connect(lambda _, id=id_receta: self.ver_ingredientes(id))
            self.tabla_lista_recetas.setCellWidget(fila, 2, btn_ver)

            btn_eliminar = QPushButton("Eliminar")
            btn_eliminar.clicked.connect(lambda _, id=id_receta: self.eliminar_receta(id))
            self.tabla_lista_recetas.setCellWidget(fila, 3, btn_eliminar)

    def ver_ingredientes(self, id_receta):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.codigo_materia, materia_prima_stock.nombre, d.cantidad, materia_prima_stock.tipo
            FROM receta_detalle d
            JOIN materia_prima_stock ON d.codigo_materia = materia_prima_stock.codigo
            WHERE d.receta_id = ?
        """, (id_receta,))

        ingredientes = cursor.fetchall()
        conn.close()

        ventana = QWidget()
        ventana.setWindowTitle("Ingredientes de la receta")
        layout = QVBoxLayout()

        tabla = QTableWidget()
        tabla.setColumnCount(4)
        tabla.setHorizontalHeaderLabels(["Código", "Nombre", "Cantidad usada", "Unidad"])
        tabla.setRowCount(len(ingredientes))

        for fila, ing in enumerate(ingredientes):
            codigo_materia, nombre, cantidad, tipo = ing
            tabla.setItem(fila, 0, QTableWidgetItem(codigo_materia))
            tabla.setItem(fila, 1, QTableWidgetItem(nombre))
            tabla.setItem(fila, 2, QTableWidgetItem(str(cantidad)))
            tabla.setItem(fila, 3, QTableWidgetItem("gr" if tipo == "gramos" else "ml"))

        layout.addWidget(tabla)

        btn_guardar = QPushButton("Guardar cambios")
        def guardar_cambios():
            conn = conectar()
            cursor = conn.cursor()
            for fila in range(tabla.rowCount()):
                codigo_materia = tabla.item(fila, 0).text()
                cantidad = float(tabla.item(fila, 2).text())
                cursor.execute("UPDATE receta_detalle SET cantidad = ? WHERE receta_id = ? AND codigo_materia = ?",
                            (cantidad, id_receta, codigo_materia))
            conn.commit()
            conn.close()
            QMessageBox.information(ventana, "Éxito", "Ingredientes actualizados")
            ventana.close()

        btn_guardar.clicked.connect(guardar_cambios)
        layout.addWidget(btn_guardar)

        ventana.setLayout(layout)
        ventana.show()


    def eliminar_receta(self, id_receta):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM receta_detalle WHERE receta_id = ?", (id_receta,))
        cursor.execute("DELETE FROM recetas WHERE id = ?", (id_receta,))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Eliminado", "Receta eliminada correctamente")
        self.cargar_lista_recetas()


    # ---------------- INGRESAR ----------------
    def init_ingresar_tab(self):
        layout = QVBoxLayout()

        self.combo_recetas = QComboBox()
        layout.addWidget(self.combo_recetas)
        self.cargar_recetas_combo()
        
        self.nombre_ingresar_label = QLabel("Producto final:")
        layout.addWidget(self.nombre_ingresar_label)

        self.cantidad_producida_input = QLineEdit()
        self.cantidad_producida_input.setPlaceholderText("Cantidad producida")
        layout.addWidget(self.cantidad_producida_input)

        self.combo_tipo_produccion = QComboBox()
        self.combo_tipo_produccion.addItems(["unidad", "peso"])
        layout.addWidget(QLabel("Tipo de producto producido"))
        layout.addWidget(self.combo_tipo_produccion)

        btn_confirmar = QPushButton("Confirmar producción")
        btn_confirmar.clicked.connect(self.confirmar_produccion)
        layout.addWidget(btn_confirmar)

        self.tabla_producciones = QTableWidget()
        self.tabla_producciones.setColumnCount(3)
        self.tabla_producciones.setHorizontalHeaderLabels(["Código receta", "Producto final", "Cantidad producida"])
        layout.addWidget(self.tabla_producciones)

        self.tabla_consumo = QTableWidget()
        self.tabla_consumo.setColumnCount(3)
        self.tabla_consumo.setHorizontalHeaderLabels(["Código materia prima", "Nombre", "Cantidad usada hoy"])
        layout.addWidget(self.tabla_consumo)


        self.tab_ingresar.setLayout(layout)

    def cargar_recetas_combo(self):
        self.combo_recetas.clear()
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT codigo, nombre FROM recetas")
        recetas = cursor.fetchall()
        conn.close()

        for codigo, nombre in recetas:
            self.combo_recetas.addItem(f"{codigo} - {nombre}", codigo)

        self.combo_recetas.currentIndexChanged.connect(self.actualizar_nombre_producto)


    def actualizar_nombre_producto(self):
        codigo_receta = self.combo_recetas.currentData()
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM recetas WHERE codigo = ?", (codigo_receta,))
        receta = cursor.fetchone()
        conn.close()
        if receta:
            self.nombre_ingresar_label.setText(f"Producto final: {receta[0]}")


    def guardar_produccion_diaria(self):
        escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")

        carpeta_produccion = os.path.join(escritorio, "Producción diaria")
        os.makedirs(carpeta_produccion, exist_ok=True)

        archivo = os.path.join(carpeta_produccion, f"produccion_{fecha_hoy}.txt")
        with open(archivo, "w", encoding="utf-8") as f:
            f.write(f"Producción del día {fecha_hoy}\n\n")
            for fila in range(self.tabla_producciones.rowCount()):
                nombre = self.tabla_producciones.item(fila, 1).text()
                cantidad = self.tabla_producciones.item(fila, 2).text()
                f.write(f"- {nombre} | Cantidad producida: {cantidad}\n")

    def guardar_consumo_diario(self):

        escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")

        carpeta_consumo = os.path.join(escritorio, "Consumo diario de materia prima")
        os.makedirs(carpeta_consumo, exist_ok=True)

        archivo = os.path.join(carpeta_consumo, f"consumo_{fecha_hoy}.txt")
        with open(archivo, "w", encoding="utf-8") as f:
            f.write(f"Consumo de materia prima - {fecha_hoy}\n\n")
            for fila in range(self.tabla_consumo.rowCount()):
                nombre = self.tabla_consumo.item(fila, 1).text()
                usado = self.tabla_consumo.item(fila, 2).text()
                codigo = self.tabla_consumo.item(fila, 0).text()

                conn = conectar()
                cursor = conn.cursor()
                cursor.execute("SELECT cantidad FROM materia_prima_stock WHERE codigo = ?", (codigo,))
                stock_restante = cursor.fetchone()[0]
                conn.close()

                f.write(f"- {nombre} | Usado: {usado} | Stock restante: {stock_restante}\n")



    def confirmar_produccion(self):
        codigo_receta = self.combo_recetas.currentData()
        try:
            cantidad_producida = float(self.cantidad_producida_input.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Ingrese una cantidad válida")
            return

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT id, nombre, tipo FROM recetas WHERE codigo = ?", (codigo_receta,))
        receta = cursor.fetchone()
        if not receta:
            QMessageBox.warning(self, "Error", "Receta no encontrada")
            conn.close()
            return

        receta_id, nombre_producto, tipo_producto = receta

        tipo_seleccionado = self.combo_tipo_produccion.currentText()
        if tipo_seleccionado:
            tipo_producto = tipo_seleccionado

        cursor.execute("SELECT codigo_materia, cantidad FROM receta_detalle WHERE receta_id = ?", (receta_id,))
        ingredientes = cursor.fetchall()

        for codigo_materia, cantidad_usada in ingredientes:
            cantidad_total = cantidad_usada * cantidad_producida
            cursor.execute("SELECT cantidad FROM materia_prima_stock WHERE codigo = ?", (codigo_materia,))
            existente = cursor.fetchone()
            if existente:
                nuevo_stock = existente[0] - cantidad_total
                cursor.execute("UPDATE materia_prima_stock SET cantidad = ? WHERE codigo = ?", (nuevo_stock, codigo_materia))

            encontrado = False
            for fila in range(self.tabla_consumo.rowCount()):
                codigo_existente = self.tabla_consumo.item(fila, 0).text()
                if codigo_existente == codigo_materia:
                    cantidad_actual = float(self.tabla_consumo.item(fila, 2).text())
                    nueva_cantidad = cantidad_actual + cantidad_total
                    self.tabla_consumo.setItem(fila, 2, QTableWidgetItem(str(nueva_cantidad)))
                    encontrado = True
                    break

            if not encontrado:
                cursor.execute("SELECT nombre FROM materia_prima_stock WHERE codigo = ?", (codigo_materia,))
                nombre_materia = cursor.fetchone()[0]
                fila = self.tabla_consumo.rowCount()
                self.tabla_consumo.insertRow(fila)
                self.tabla_consumo.setItem(fila, 0, QTableWidgetItem(codigo_materia))
                self.tabla_consumo.setItem(fila, 1, QTableWidgetItem(nombre_materia))
                self.tabla_consumo.setItem(fila, 2, QTableWidgetItem(str(cantidad_total)))

            cursor.execute("SELECT cantidad FROM produccion_stock WHERE codigo = ?", (codigo_receta,))
            existente = cursor.fetchone()
            if existente:
                nuevo_stock = existente[0] + cantidad_producida
                cursor.execute("UPDATE produccion_stock SET cantidad = ? WHERE codigo = ?", (nuevo_stock, codigo_receta))
            else:
                cursor.execute("INSERT INTO produccion_stock (codigo, nombre, cantidad, tipo) VALUES (?, ?, ?, ?)",
                            (codigo_receta, nombre_producto, cantidad_producida, tipo_producto))

            cursor.execute("SELECT stock FROM productos WHERE codigo = ?", (codigo_receta,))
            existente = cursor.fetchone()
            if existente:
                nuevo_stock = existente[0] + cantidad_producida
                cursor.execute("UPDATE productos SET stock = ? WHERE codigo = ?", (nuevo_stock, codigo_receta))
            else:
                cursor.execute("INSERT INTO productos (codigo, nombre, precio, stock, tipo) VALUES (?, ?, ?, ?, ?)",
                            (codigo_receta, nombre_producto, 0.0, cantidad_producida, tipo_producto))
                

        encontrado = False
        for fila in range(self.tabla_producciones.rowCount()):
            codigo_existente = self.tabla_producciones.item(fila, 0).text()
            if codigo_existente == codigo_receta:
                cantidad_actual = float(self.tabla_producciones.item(fila, 2).text())
                nueva_cantidad = cantidad_actual + cantidad_producida
                self.tabla_producciones.setItem(fila, 2, QTableWidgetItem(str(nueva_cantidad)))
                encontrado = True
                break

        if not encontrado:
            fila = self.tabla_producciones.rowCount()
            self.tabla_producciones.insertRow(fila)
            self.tabla_producciones.setItem(fila, 0, QTableWidgetItem(codigo_receta))
            self.tabla_producciones.setItem(fila, 1, QTableWidgetItem(nombre_producto))
            self.tabla_producciones.setItem(fila, 2, QTableWidgetItem(str(cantidad_producida)))


        QMessageBox.information(self, "Éxito", "Producción registrada correctamente")
        self.cantidad_producida_input.clear()

        
        conn.commit()
        conn.close()

        self.cargar_stock()              
        self.cargar_stock_produccion()   

        self.guardar_produccion_diaria()
        self.guardar_consumo_diario()
