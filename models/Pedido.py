from models.Cliente import Cliente

class Pedido():
    idPedido: int
    fecha: str
    cliente: Cliente #relacion uno a uno
    
#relacion entre cliente y pedido
