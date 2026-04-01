import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton
from inventario import InventarioWindow
from tickets import TicketsWindow
from produccion import ProduccionWindow
from PyQt5.QtGui import QFont
from conexion import inicializar_bd

inicializar_bd()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Almacén")
        self.setGeometry(200, 200, 800, 600)

        central_widget = QWidget()
        layout = QVBoxLayout()

        btn_tickets = QPushButton("Abrir Tickets")
        btn_tickets.clicked.connect(self.abrir_tickets)
        layout.addWidget(btn_tickets)

        btn_inventario = QPushButton("Abrir Inventario")
        btn_inventario.clicked.connect(self.abrir_inventario)
        layout.addWidget(btn_inventario)

        btn_produccion = QPushButton("Abrir Producción")
        btn_produccion.clicked.connect(self.abrir_produccion)
        layout.addWidget(btn_produccion)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def abrir_tickets(self):
        self.tickets_window = TicketsWindow()
        self.tickets_window.show()

    def abrir_inventario(self):
        self.inventario_window = InventarioWindow()
        self.inventario_window.show()

    def abrir_produccion(self):
        self.produccion_window = ProduccionWindow()  
        self.produccion_window.show()

if __name__ == "__main__":
    inicializar_bd()   

    app = QApplication(sys.argv)
    fuente = QFont("Arial", 20)
    app.setFont(fuente)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
