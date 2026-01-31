"""
Servicio de pagos abstracto para integración con diferentes gateways
Este módulo proporciona una arquitectura modular y extensible para pagos
"""
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, Optional, Tuple
from datetime import datetime


class PaymentResult:
    """Resultado de una operación de pago"""
    def __init__(self, success: bool, transaction_id: str = None, 
                 message: str = "", error: str = None, metadata: Dict = None):
        self.success = success
        self.transaction_id = transaction_id
        self.message = message
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = datetime.now()


class PaymentGateway(ABC):
    """
    Interfaz abstracta para gateways de pago
    Todos los gateways deben implementar estos métodos
    """
    
    @abstractmethod
    def process_payment(self, amount: Decimal, ticket_id: int, 
                       customer_data: Dict = None) -> PaymentResult:
        """
        Procesa un pago
        
        Args:
            amount: Monto a cobrar
            ticket_id: ID del ticket/pedido
            customer_data: Datos opcionales del cliente
            
        Returns:
            PaymentResult con el resultado de la transacción
        """
        pass
    
    @abstractmethod
    def refund_payment(self, transaction_id: str, amount: Decimal = None) -> PaymentResult:
        """
        Reembolsa un pago
        
        Args:
            transaction_id: ID de la transacción a reembolsar
            amount: Monto a reembolsar (None = reembolso total)
            
        Returns:
            PaymentResult con el resultado del reembolso
        """
        pass
    
    @abstractmethod
    def verify_payment(self, transaction_id: str) -> PaymentResult:
        """
        Verifica el estado de un pago
        
        Args:
            transaction_id: ID de la transacción a verificar
            
        Returns:
            PaymentResult con el estado actual
        """
        pass


class CashPaymentGateway(PaymentGateway):
    """Gateway para pagos en efectivo (sin procesamiento externo)"""
    
    def process_payment(self, amount: Decimal, ticket_id: int, 
                       customer_data: Dict = None) -> PaymentResult:
        """Procesa un pago en efectivo"""
        transaction_id = f"CASH-{ticket_id}-{int(datetime.now().timestamp())}"
        return PaymentResult(
            success=True,
            transaction_id=transaction_id,
            message="Pago en efectivo registrado correctamente",
            metadata={"payment_method": "cash", "amount": str(amount)}
        )
    
    def refund_payment(self, transaction_id: str, amount: Decimal = None) -> PaymentResult:
        """Registra un reembolso en efectivo"""
        return PaymentResult(
            success=True,
            transaction_id=f"REFUND-{transaction_id}",
            message="Reembolso en efectivo registrado",
            metadata={"refund_amount": str(amount) if amount else "total"}
        )
    
    def verify_payment(self, transaction_id: str) -> PaymentResult:
        """Verifica un pago en efectivo (siempre válido si existe)"""
        return PaymentResult(
            success=True,
            transaction_id=transaction_id,
            message="Pago en efectivo verificado"
        )


class StripePaymentGateway(PaymentGateway):
    """
    Gateway para Stripe (placeholder para implementación futura)
    
    Para usar: instalar stripe y configurar API keys
    pip install stripe
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "sk_test_..."  # Configurar con API key real
        # import stripe
        # stripe.api_key = self.api_key
    
    def process_payment(self, amount: Decimal, ticket_id: int, 
                       customer_data: Dict = None) -> PaymentResult:
        """Procesa un pago con Stripe"""
        # TODO: Implementar integración con Stripe API
        # charge = stripe.Charge.create(
        #     amount=int(amount * 100),  # Stripe usa centavos
        #     currency="mxn",
        #     source=customer_data.get("token"),
        #     description=f"Ticket #{ticket_id}"
        # )
        
        return PaymentResult(
            success=False,
            error="Stripe no configurado aún. Implementar integración real.",
            metadata={"gateway": "stripe", "amount": str(amount)}
        )
    
    def refund_payment(self, transaction_id: str, amount: Decimal = None) -> PaymentResult:
        """Reembolsa un pago en Stripe"""
        # TODO: stripe.Refund.create(charge=transaction_id, amount=...)
        return PaymentResult(success=False, error="Stripe refund no implementado")
    
    def verify_payment(self, transaction_id: str) -> PaymentResult:
        """Verifica un pago en Stripe"""
        # TODO: charge = stripe.Charge.retrieve(transaction_id)
        return PaymentResult(success=False, error="Stripe verify no implementado")


class MercadoPagoGateway(PaymentGateway):
    """
    Gateway para MercadoPago (placeholder para implementación futura)
    
    Para usar: instalar mercadopago SDK y configurar access token
    pip install mercadopago
    """
    
    def __init__(self, access_token: str = None):
        self.access_token = access_token or "TEST-..."
        # import mercadopago
        # self.sdk = mercadopago.SDK(self.access_token)
    
    def process_payment(self, amount: Decimal, ticket_id: int, 
                       customer_data: Dict = None) -> PaymentResult:
        """Procesa un pago con MercadoPago"""
        # TODO: Implementar integración con MercadoPago API
        # payment_data = {
        #     "transaction_amount": float(amount),
        #     "description": f"Ticket #{ticket_id}",
        #     "payment_method_id": customer_data.get("payment_method_id"),
        #     "payer": {...}
        # }
        # result = self.sdk.payment().create(payment_data)
        
        return PaymentResult(
            success=False,
            error="MercadoPago no configurado aún. Implementar integración real.",
            metadata={"gateway": "mercadopago", "amount": str(amount)}
        )
    
    def refund_payment(self, transaction_id: str, amount: Decimal = None) -> PaymentResult:
        """Reembolsa un pago en MercadoPago"""
        return PaymentResult(success=False, error="MercadoPago refund no implementado")
    
    def verify_payment(self, transaction_id: str) -> PaymentResult:
        """Verifica un pago en MercadoPago"""
        return PaymentResult(success=False, error="MercadoPago verify no implementado")


class PaymentService:
    """
    Servicio principal de pagos
    Orquesta los diferentes gateways de pago
    """
    
    def __init__(self):
        self.gateways = {
            'EFECTIVO': CashPaymentGateway(),
            'TARJETA': CashPaymentGateway(),  # Por ahora usa efectivo
            'TRANSFERENCIA': CashPaymentGateway(),
            'STRIPE': StripePaymentGateway(),
            'MERCADOPAGO': MercadoPagoGateway(),
        }
    
    def process_payment(self, ticket_id: int, amount: Decimal, 
                       method: str = 'EFECTIVO', 
                       customer_data: Dict = None) -> PaymentResult:
        """
        Procesa un pago usando el gateway apropiado
        
        Args:
            ticket_id: ID del ticket a pagar
            amount: Monto a cobrar
            method: Método de pago (EFECTIVO, TARJETA, STRIPE, etc.)
            customer_data: Datos adicionales del cliente/pago
            
        Returns:
            PaymentResult con el resultado
        """
        gateway = self.gateways.get(method.upper())
        if not gateway:
            return PaymentResult(
                success=False,
                error=f"Método de pago no soportado: {method}"
            )
        
        return gateway.process_payment(amount, ticket_id, customer_data)
