from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QMessageBox, QTableWidget, QTableWidgetItem, QComboBox
from PyQt5.QtCore import Qt
from conexion import conectar

class InventarioWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventario")
        self.setGeometry(250, 250, 1000, 800)

        layout = QVBoxLayout()

        self.codigo_input = QLineEdit()
        self.codigo_input.setPlaceholderText("Código del producto")
        layout.addWidget(self.codigo_input)

        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre del producto")
        layout.addWidget(self.nombre_input)

        self.precio_input = QLineEdit()
        self.precio_input.setPlaceholderText("Precio")
        layout.addWidget(self.precio_input)

        self.stock_input = QLineEdit()
        self.stock_input.setPlaceholderText("Stock inicial")
        layout.addWidget(self.stock_input)

        self.tipo_input = QComboBox()
        self.tipo_input.addItems(["unidad", "peso"])
        layout.addWidget(self.tipo_input)

        guardar_btn = QPushButton("Guardar producto")
        guardar_btn.clicked.connect(self.guardar_producto)
        layout.addWidget(guardar_btn)

        self.codigo_compra_input = QLineEdit()
        self.codigo_compra_input.setPlaceholderText("Código del producto comprado")
        layout.addWidget(self.codigo_compra_input)

        self.cantidad_compra_input = QLineEdit()
        self.cantidad_compra_input.setPlaceholderText("Cantidad comprada")
        layout.addWidget(self.cantidad_compra_input)

        compra_btn = QPushButton("Registrar compra")
        compra_btn.clicked.connect(self.registrar_compra)
        layout.addWidget(compra_btn)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["Código", "Nombre", "Precio", "Stock", "Tipo", "Acciones"])
        layout.addWidget(self.tabla)

        self.setLayout(layout)

        self.cargar_productos()

        self.tabla.itemChanged.connect(self.actualizar_precio)

    def guardar_producto(self):
        codigo = self.codigo_input.text()
        nombre = self.nombre_input.text()
        precio = float(self.precio_input.text())
        stock = int(self.stock_input.text())
        tipo = self.tipo_input.currentText()

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY,
                codigo TEXT,
                nombre TEXT,
                precio REAL,
                stock INTEGER,
                tipo TEXT
            )
        ''')

        cursor.execute("INSERT INTO productos (codigo, nombre, precio, stock, tipo) VALUES (?, ?, ?, ?, ?)",
                       (codigo, nombre, precio, stock, tipo))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "Éxito", "Producto guardado correctamente")
        self.codigo_input.clear()
        self.nombre_input.clear()
        self.precio_input.clear()
        self.stock_input.clear()
        self.tipo_input.setCurrentIndex(0)

        self.cargar_productos()

    def registrar_compra(self):
        codigo = self.codigo_compra_input.text()
        cantidad = int(self.cantidad_compra_input.text())

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT nombre, stock FROM productos WHERE codigo = ?", (codigo,))
        resultado = cursor.fetchone()

        if resultado:
            nombre, stock_actual = resultado
            nuevo_stock = stock_actual + cantidad
            cursor.execute("UPDATE productos SET stock = ? WHERE codigo = ?", (nuevo_stock, codigo))
            conn.commit()
            QMessageBox.information(
                self,
                "Compra registrada",
                f"Nuevo stock de {codigo} - {nombre}: {nuevo_stock}"
            )
        else:
            QMessageBox.warning(self, "Error", "No existe un producto con ese código")

        conn.close()
        self.codigo_compra_input.clear()
        self.cantidad_compra_input.clear()
        self.cargar_productos()
        
    def cargar_productos(self):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, codigo, nombre, precio, stock, tipo FROM productos")
        productos = cursor.fetchall()
        conn.close()

        self.tabla.blockSignals(True)
        self.tabla.setRowCount(len(productos))
        for fila, producto in enumerate(productos):
            id_producto, codigo, nombre, precio, stock, tipo = producto

            codigo_item = QTableWidgetItem(str(codigo))
            codigo_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.tabla.setItem(fila, 0, codigo_item)

            nombre_item = QTableWidgetItem(str(nombre))
            nombre_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.tabla.setItem(fila, 1, nombre_item)

            precio_item = QTableWidgetItem(str(precio))
            precio_item.setData(Qt.UserRole, id_producto)
            precio_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            self.tabla.setItem(fila, 2, precio_item)

            stock_item = QTableWidgetItem(str(stock))
            stock_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.tabla.setItem(fila, 3, stock_item)

            tipo_item = QTableWidgetItem(str(tipo))
            tipo_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.tabla.setItem(fila, 4, tipo_item)

            btn_eliminar = QPushButton("Eliminar")
            btn_eliminar.clicked.connect(lambda _, id=id_producto: self.eliminar_producto(id))
            self.tabla.setCellWidget(fila, 5, btn_eliminar)

        self.tabla.blockSignals(False)

    def actualizar_precio(self, item):
        if item.column() == 2:
            try:
                nuevo_precio = float(item.text())
                id_producto = item.data(Qt.UserRole)

                conn = conectar()
                cursor = conn.cursor()
                cursor.execute("UPDATE productos SET precio = ? WHERE id = ?", (nuevo_precio, id_producto))
                conn.commit()
                conn.close()

                QMessageBox.information(self, "Actualizado", f"Precio actualizado a {nuevo_precio}")
            except ValueError:
                QMessageBox.warning(self, "Error", "El precio debe ser un número válido")

    def eliminar_producto(self, id_producto):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Eliminado", "Producto eliminado correctamente")
        self.cargar_productos()