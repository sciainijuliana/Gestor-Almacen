from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QLabel
)
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QTextDocument
from conexion import conectar
from datetime import datetime
from PyQt5.QtCore import QSizeF 
import os
import sqlite3


class TicketsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tickets de Venta")
        self.setGeometry(250, 250, 1000, 800)
        self.total = 0.0

        layout = QVBoxLayout()

        self.codigo_input = QLineEdit()
        self.codigo_input.setPlaceholderText("Código del producto")
        layout.addWidget(self.codigo_input)

        self.codigo_input.returnPressed.connect(self.agregar_producto)

        self.cantidad_input = QLineEdit()
        self.cantidad_input.setPlaceholderText("Cantidad vendida (default 1)")
        layout.addWidget(self.cantidad_input)

        self.agregar_btn = QPushButton("Agregar al ticket")
        self.agregar_btn.clicked.connect(self.agregar_producto)
        layout.addWidget(self.agregar_btn)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(
            ["Código", "Nombre", "Cantidad", "Precio unitario", "Monto total", "Acción"]
        )
        layout.addWidget(self.tabla)

        self.total_label = QLabel("Total: 0")
        layout.addWidget(self.total_label)

        self.finalizar_btn = QPushButton("Finalizar venta")
        self.finalizar_btn.clicked.connect(self.finalizar_ticket)
        layout.addWidget(self.finalizar_btn)

        self.imprimir_btn = QPushButton("Imprimir ticket")
        self.imprimir_btn.clicked.connect(self.imprimir_ticket)
        layout.addWidget(self.imprimir_btn)

        self.nueva_venta_btn = QPushButton("Nueva venta")
        self.nueva_venta_btn.clicked.connect(self.nueva_venta)
        layout.addWidget(self.nueva_venta_btn)

        self.setLayout(layout)

        self.productos_ticket = []

        self.ticket_id = None
        self.ticket_fecha = None

    def actualizar_total(self):
        total = 0.0
        for p in self.productos_ticket:
            total += p[5] 
        self.total = total
        self.total_label.setText(f"Total: {self.total:.2f}")

    def agregar_producto(self):
        if self.ticket_id is not None:
            QMessageBox.warning(self, "Error", "El ticket ya fue finalizado, no se puede editar")
            return

        codigo = self.codigo_input.text().strip()

        try:
            cantidad = int(self.cantidad_input.text()) if self.cantidad_input.text() else 1
        except ValueError:
            QMessageBox.warning(self, "Error", "Ingrese una cantidad válida")
            return

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, precio, stock, tipo FROM productos WHERE codigo = ?", (codigo,))
        producto = cursor.fetchone()

        if producto:
            id_producto, nombre, precio, stock, tipo = producto

            if tipo == "unidad":
                if cantidad <= stock:
                    monto_total = precio * cantidad
                    nuevo_stock = stock - cantidad
                    self.productos_ticket.append((id_producto, codigo, nombre, cantidad, precio, monto_total, tipo))
                    fila = self.tabla.rowCount()
                    self.tabla.insertRow(fila)
                    self.tabla.setItem(fila, 0, QTableWidgetItem(codigo))
                    self.tabla.setItem(fila, 1, QTableWidgetItem(nombre))
                    self.tabla.setItem(fila, 2, QTableWidgetItem(str(cantidad)))
                    self.tabla.setItem(fila, 3, QTableWidgetItem(f"{precio:.2f} /unidad"))
                    self.tabla.setItem(fila, 4, QTableWidgetItem(f"{monto_total:.2f}"))

                    btn_eliminar = QPushButton("Eliminar")
                    btn_eliminar.clicked.connect(lambda _, f=fila: self.eliminar_item_ticket(f))
                    self.tabla.setCellWidget(fila, 5, btn_eliminar)

                    self.actualizar_total()
                else:
                    QMessageBox.warning(self, "Error", "Stock insuficiente")

            elif tipo == "peso":
                if cantidad <= stock:
                    cantidad_kg = cantidad / 1000.0
                    monto_total = precio * cantidad_kg
                    nuevo_stock = stock - cantidad
                    self.productos_ticket.append((id_producto, codigo, nombre, cantidad, precio, monto_total, tipo))
                    fila = self.tabla.rowCount()
                    self.tabla.insertRow(fila)
                    self.tabla.setItem(fila, 0, QTableWidgetItem(codigo))
                    self.tabla.setItem(fila, 1, QTableWidgetItem(nombre))
                    self.tabla.setItem(fila, 2, QTableWidgetItem(f"{cantidad} g"))
                    self.tabla.setItem(fila, 3, QTableWidgetItem(f"{precio:.2f} /kg"))
                    self.tabla.setItem(fila, 4, QTableWidgetItem(f"{monto_total:.2f}"))

                    btn_eliminar = QPushButton("Eliminar")
                    btn_eliminar.clicked.connect(lambda _, f=fila: self.eliminar_item_ticket(f))
                    self.tabla.setCellWidget(fila, 5, btn_eliminar)

                    self.actualizar_total()
                else:
                    QMessageBox.warning(self, "Error", "Stock insuficiente")

        else:
            QMessageBox.warning(self, "Error", "Producto no encontrado")

        conn.close()
        self.codigo_input.clear()
        self.cantidad_input.clear()


    def eliminar_item_ticket(self, fila):
        if self.ticket_id is not None:
            QMessageBox.warning(self, "Error", "El ticket ya fue finalizado, no se puede editar")
            return
        if 0 <= fila < len(self.productos_ticket):
            self.productos_ticket.pop(fila)
            self.tabla.removeRow(fila)
            self.actualizar_total()

    def actualizar_reporte_diario(self):

        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        carpeta = os.path.join(desktop, "Ventas Diarias Totales")

        if not os.path.exists(carpeta):
            os.makedirs(carpeta)

        fecha = datetime.now().strftime("%Y-%m-%d")
        archivo = os.path.join(carpeta, f"{fecha}.txt")

        conn = sqlite3.connect("almacen.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.nombre, SUM(d.cantidad), SUM(d.subtotal)
            FROM detalle_ticket d
            JOIN productos p ON d.producto_id = p.id
            JOIN tickets t ON d.ticket_id = t.id
            WHERE DATE(t.fecha) = DATE('now', 'localtime')
            GROUP BY p.nombre
        """)
        ventas = cursor.fetchall()
        conn.close()

        with open(archivo, "w", encoding="utf-8") as f:
            f.write(f"Reporte de ventas - {fecha}\n")
            f.write("="*40 + "\n\n")
            total_general = 0
            for nombre, cantidad, total in ventas:
                f.write(f"{nombre}: {cantidad} unidades - ${total:.2f}\n")
                total_general += total
            f.write("\n" + "="*40 + "\n")
            f.write(f"TOTAL GENERAL DEL DÍA: ${total_general:.2f}\n")

    def guardar_ticket_diario(self):
        escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        hora_actual = datetime.now().strftime("%H:%M:%S")

        carpeta_ventas = os.path.join(escritorio, "Ventas diarias por Ticket", fecha_hoy)
        os.makedirs(carpeta_ventas, exist_ok=True)

        archivo = os.path.join(carpeta_ventas, f"ticket_{self.ticket_id}.txt")
        with open(archivo, "w", encoding="utf-8") as f:
            f.write(f"Fecha: {fecha_hoy} {hora_actual}\n")
            f.write(f"Número de Ticket: {self.ticket_id}\n\n")
            f.write("Productos:\n")
            for p in self.productos_ticket:
                _, codigo, nombre, cantidad, precio, subtotal, tipo = p
                f.write(f"- {nombre} ({codigo}) | Cantidad: {cantidad} | Precio: {precio:.2f} | Subtotal: {subtotal:.2f}\n")
            f.write(f"\nTotal: {self.total:.2f}\n")
        self.actualizar_reporte_diario()

    def finalizar_ticket(self):
        if not self.productos_ticket:
            QMessageBox.warning(self, "Error", "No hay productos en el ticket")
            return

        conn = conectar()
        cursor = conn.cursor()

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total = self.total
        cursor.execute("INSERT INTO tickets (fecha, total) VALUES (?, ?)", (fecha, total))
        self.ticket_id = cursor.lastrowid
        self.ticket_fecha = fecha

        for p in self.productos_ticket:
            id_producto, codigo, nombre, cantidad, precio_unitario, monto_total, tipo = p

            cursor.execute(
                "INSERT INTO detalle_ticket (ticket_id, producto_id, cantidad, subtotal, tipo) VALUES (?, ?, ?, ?, ?)",
                (self.ticket_id, id_producto, cantidad, monto_total, tipo)
            )

            cursor.execute("SELECT stock FROM productos WHERE id = ?", (id_producto,))
            stock_actual = cursor.fetchone()[0]

            nuevo_stock = stock_actual - cantidad
            cursor.execute("UPDATE productos SET stock = ? WHERE id = ?", (nuevo_stock, id_producto))

        conn.commit()
        conn.close()

        self.guardar_ticket_diario()

        QMessageBox.information(self, "Éxito", "Ticket finalizado correctamente")
        self.imprimir_ticket()

    def imprimir_ticket(self):
        if not self.ticket_id:
            QMessageBox.warning(self, "Error", "Debe finalizar el ticket antes de imprimir")
            return

        fecha = self.ticket_fecha
        ticket_id = self.ticket_id

        contenido = f"""
        <html>
        <head>
            <style>
                body {{ font-size: 16pt; }}
                h2 {{ font-size: 20pt; text-align: center; }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 16pt;
                }}
                th, td {{
                    padding: 6px;
                    text-align: right;
                }}
                th {{ border-bottom: 1px solid black; }}
                td {{ border-bottom: 1px dotted #999; }}
            </style>
        </head>
        <body>
            <h2>Almacén San Vicente</h2>
            <p><b>Fecha:</b> {fecha}</p>
            <p><b>Número de Ticket:</b> {ticket_id}</p>
            <hr>
            <table>
                <tr>
                    <th style="width:40%;">Nombre</th>
                    <th style="width:20%;">Cantidad</th>
                    <th style="width:20%;">Precio unitario</th>
                    <th style="width:20%;">Total</th>
                </tr>
        """

        for p in self.productos_ticket:
            id_producto, codigo, nombre, cantidad, precio_unitario, monto_total, tipo = p

            if tipo == "unidad":
                cantidad_str = f"{cantidad} u"
                precio_str = f"${precio_unitario:.2f} /unidad"
            else:
                cantidad_str = f"{cantidad} g"
                precio_str = f"${precio_unitario:.2f} /kg"

            contenido += f"""
                <tr>
                    <td>{nombre}</td>
                    <td>{cantidad_str}</td>
                    <td>{precio_str}</td>
                    <td>${monto_total:.2f}</td>
                </tr>
            """

        total = sum(p[5] for p in self.productos_ticket)
        contenido += f"""
            </table>
            <hr>
            <p style="text-align:right; font-size:18pt;"><b>Total: ${total:.2f}</b></p>
            <p style="text-align:center; font-size:16pt;">Gracias por su compra</p>
        </body>
        </html>
        """


        printer = QPrinter()
        from PyQt5.QtGui import QPageSize
        custom_size = QPageSize(QSizeF(227, 792), QPageSize.Point, "Ticket")
        printer.setPageSize(custom_size)
        printer.setPageMargins(10, 10, 10, 10, QPrinter.Point)

        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            doc = QTextDocument()
            doc.setHtml(contenido)
            doc.print_(printer)


    def bloquear_ticket(self):
            self.codigo_input.setDisabled(True)
            self.cantidad_input.setDisabled(True)

            self.agregar_btn.setDisabled(True)
            self.imprimir_btn.setDisabled(True)

            self.tabla.setDisabled(True)

            self.finalizar_btn.setEnabled(True)

            QMessageBox.information(self, "Ticket bloqueado", "El ticket fue impreso y ahora debe finalizarse para guardarse.")

    def nueva_venta(self):
        self.tabla.setRowCount(0)
        self.productos_ticket.clear()
        self.ticket_id = None
        self.ticket_fecha = None
        self.actualizar_total()

        self.codigo_input.setEnabled(True)
        self.cantidad_input.setEnabled(True)
        self.agregar_btn.setEnabled(True)
        self.imprimir_btn.setEnabled(True)
        self.tabla.setEnabled(True)

