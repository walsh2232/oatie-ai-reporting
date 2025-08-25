"""
Enterprise webhook system for comprehensive API ecosystem
Supports secure webhook delivery with retries, authentication, and monitoring
"""

import asyncio
import json
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import uuid

import aiohttp
import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


class WebhookEventType(str, Enum):
    """Supported webhook event types"""
    REPORT_GENERATED = "report.generated"
    REPORT_FAILED = "report.failed"
    QUERY_EXECUTED = "query.executed"
    USER_CREATED = "user.created"
    SYSTEM_ALERT = "system.alert"
    PERFORMANCE_THRESHOLD = "performance.threshold"


class WebhookStatus(str, Enum):
    """Webhook delivery status"""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


class WebhookEndpoint(BaseModel):
    """Webhook endpoint configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: str
    secret: str
    events: List[WebhookEventType]
    active: bool = True
    max_retries: int = 3
    timeout_seconds: int = 30
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WebhookPayload(BaseModel):
    """Webhook delivery payload"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: WebhookEventType
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = "oatie-ai-reporting"
    version: str = "3.0.0"


class WebhookDelivery(BaseModel):
    """Webhook delivery tracking"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    endpoint_id: str
    payload_id: str
    status: WebhookStatus = WebhookStatus.PENDING
    attempt_count: int = 0
    response_status: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_attempt_at: Optional[datetime] = None
    next_retry_at: Optional[datetime] = None


class WebhookManager:
    """Enterprise webhook management system"""
    
    def __init__(self):
        self.endpoints: Dict[str, WebhookEndpoint] = {}
        self.deliveries: Dict[str, WebhookDelivery] = {}
        self.event_handlers: Dict[WebhookEventType, List[Callable]] = {}
        self._retry_queue = asyncio.Queue()
        self._delivery_stats = {
            "total_sent": 0,
            "successful_deliveries": 0,
            "failed_deliveries": 0,
            "retry_count": 0
        }
    
    async def initialize(self):
        """Initialize webhook system"""
        # Start retry processor
        asyncio.create_task(self._process_retries())
        logger.info("Webhook system initialized")
    
    def register_endpoint(self, endpoint: WebhookEndpoint) -> str:
        """Register a new webhook endpoint"""
        self.endpoints[endpoint.id] = endpoint
        logger.info(
            "Webhook endpoint registered",
            endpoint_id=endpoint.id,
            url=endpoint.url,
            events=endpoint.events
        )
        return endpoint.id
    
    def unregister_endpoint(self, endpoint_id: str) -> bool:
        """Unregister a webhook endpoint"""
        if endpoint_id in self.endpoints:
            del self.endpoints[endpoint_id]
            logger.info("Webhook endpoint unregistered", endpoint_id=endpoint_id)
            return True
        return False
    
    def get_endpoint(self, endpoint_id: str) -> Optional[WebhookEndpoint]:
        """Get webhook endpoint by ID"""
        return self.endpoints.get(endpoint_id)
    
    def list_endpoints(self) -> List[WebhookEndpoint]:
        """List all registered webhook endpoints"""
        return list(self.endpoints.values())
    
    async def emit_event(self, event_type: WebhookEventType, data: Dict[str, Any]):
        """Emit a webhook event to all registered endpoints"""
        payload = WebhookPayload(
            event_type=event_type,
            data=data
        )
        
        # Find endpoints subscribed to this event type
        target_endpoints = [
            endpoint for endpoint in self.endpoints.values()
            if endpoint.active and event_type in endpoint.events
        ]
        
        if not target_endpoints:
            logger.debug("No endpoints subscribed to event", event_type=event_type)
            return
        
        # Create delivery records and send webhooks
        deliveries = []
        for endpoint in target_endpoints:
            delivery = WebhookDelivery(
                endpoint_id=endpoint.id,
                payload_id=payload.id
            )
            self.deliveries[delivery.id] = delivery
            deliveries.append(delivery)
            
            # Send webhook asynchronously
            asyncio.create_task(self._deliver_webhook(endpoint, payload, delivery))
        
        logger.info(
            "Webhook event emitted",
            event_type=event_type,
            payload_id=payload.id,
            endpoint_count=len(target_endpoints)
        )
        
        return deliveries
    
    async def _deliver_webhook(
        self, 
        endpoint: WebhookEndpoint, 
        payload: WebhookPayload, 
        delivery: WebhookDelivery
    ):
        """Deliver webhook to a specific endpoint"""
        delivery.attempt_count += 1
        delivery.last_attempt_at = datetime.utcnow()
        delivery.status = WebhookStatus.PENDING
        
        try:
            # Generate signature for security
            signature = self._generate_signature(payload, endpoint.secret)
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Oatie-AI-Reporting-Webhook/3.0.0",
                "X-Webhook-Signature": f"sha256={signature}",
                "X-Webhook-Event": payload.event_type,
                "X-Webhook-ID": payload.id,
                "X-Webhook-Timestamp": payload.timestamp.isoformat(),
            }
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=endpoint.timeout_seconds)
            ) as session:
                async with session.post(
                    endpoint.url,
                    json=payload.dict(),
                    headers=headers
                ) as response:
                    delivery.response_status = response.status
                    delivery.response_body = await response.text()
                    
                    if 200 <= response.status < 300:
                        delivery.status = WebhookStatus.DELIVERED
                        self._delivery_stats["successful_deliveries"] += 1
                        logger.info(
                            "Webhook delivered successfully",
                            endpoint_id=endpoint.id,
                            payload_id=payload.id,
                            status_code=response.status,
                            attempt=delivery.attempt_count
                        )
                    else:
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=f"HTTP {response.status}"
                        )
        
        except Exception as e:
            delivery.status = WebhookStatus.FAILED
            delivery.error_message = str(e)
            self._delivery_stats["failed_deliveries"] += 1
            
            logger.warning(
                "Webhook delivery failed",
                endpoint_id=endpoint.id,
                payload_id=payload.id,
                attempt=delivery.attempt_count,
                error=str(e)
            )
            
            # Schedule retry if attempts remaining
            if delivery.attempt_count < endpoint.max_retries:
                delivery.status = WebhookStatus.RETRYING
                delivery.next_retry_at = self._calculate_retry_time(delivery.attempt_count)
                await self._retry_queue.put(delivery.id)
                self._delivery_stats["retry_count"] += 1
        
        self._delivery_stats["total_sent"] += 1
    
    def _generate_signature(self, payload: WebhookPayload, secret: str) -> str:
        """Generate HMAC signature for webhook security"""
        payload_bytes = json.dumps(payload.dict(), sort_keys=True).encode('utf-8')
        signature = hmac.new(
            secret.encode('utf-8'),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _calculate_retry_time(self, attempt_count: int) -> datetime:
        """Calculate exponential backoff retry time"""
        delay_seconds = min(300, (2 ** attempt_count) * 30)  # Max 5 minutes
        return datetime.utcnow() + timedelta(seconds=delay_seconds)
    
    async def _process_retries(self):
        """Background task to process webhook retries"""
        while True:
            try:
                # Wait for retry or timeout
                delivery_id = await asyncio.wait_for(
                    self._retry_queue.get(), 
                    timeout=60
                )
                
                delivery = self.deliveries.get(delivery_id)
                if not delivery or delivery.next_retry_at > datetime.utcnow():
                    # Not time to retry yet, put back in queue
                    if delivery:
                        await self._retry_queue.put(delivery_id)
                    continue
                
                endpoint = self.endpoints.get(delivery.endpoint_id)
                if not endpoint or not endpoint.active:
                    continue
                
                # Reconstruct payload (in real implementation, store payload separately)
                payload = WebhookPayload(
                    id=delivery.payload_id,
                    event_type=WebhookEventType.SYSTEM_ALERT,
                    data={"retry": True}
                )
                
                # Retry delivery
                await self._deliver_webhook(endpoint, payload, delivery)
                
            except asyncio.TimeoutError:
                # Check for pending retries
                current_time = datetime.utcnow()
                for delivery in self.deliveries.values():
                    if (delivery.status == WebhookStatus.RETRYING and 
                        delivery.next_retry_at and 
                        delivery.next_retry_at <= current_time):
                        await self._retry_queue.put(delivery.id)
            
            except Exception as e:
                logger.error("Error in retry processor", error=str(e))
                await asyncio.sleep(5)
    
    def get_delivery_status(self, delivery_id: str) -> Optional[WebhookDelivery]:
        """Get webhook delivery status"""
        return self.deliveries.get(delivery_id)
    
    def get_delivery_stats(self) -> Dict[str, Any]:
        """Get webhook delivery statistics"""
        return {
            **self._delivery_stats,
            "success_rate": (
                self._delivery_stats["successful_deliveries"] / 
                max(1, self._delivery_stats["total_sent"]) * 100
            ),
            "endpoints_count": len(self.endpoints),
            "active_endpoints": len([e for e in self.endpoints.values() if e.active])
        }
    
    def register_event_handler(
        self, 
        event_type: WebhookEventType, 
        handler: Callable[[Dict[str, Any]], None]
    ):
        """Register internal event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def trigger_internal_handlers(
        self, 
        event_type: WebhookEventType, 
        data: Dict[str, Any]
    ):
        """Trigger internal event handlers"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception as e:
                    logger.error(
                        "Error in event handler",
                        event_type=event_type,
                        error=str(e)
                    )