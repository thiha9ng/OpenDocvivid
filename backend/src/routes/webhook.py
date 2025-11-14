"""
Webhook routes for external payment providers
"""

import hashlib
import hmac
import uuid
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.configs.config import settings
from src.models import get_db
from src.services.subscription_service import SubscriptionService
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

WEBHOOK_SECRET = settings.webhook_secret

def verify_webhook_signature(signature_data: bytes, signature: str, secret: str) -> bool:
    """Verify webhook signature for security"""
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        signature_data,
        hashlib.sha256
    ).hexdigest()

    logger.info("expected_signature: ", expected_signature)
    logger.info("signature: ", signature)

    return hmac.compare_digest(expected_signature, signature)

@router.post("/bagelpay")
async def handle_bagelpay_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle BagelPay webhook"""
    try:
        payload = await request.json()
        timestamp = request.headers.get('timestamp').encode()
        signature = request.headers.get('Bagelpay-Signature')
        # Combine payload and timestamp
        signature_data = timestamp + ".".encode() + payload
        if not verify_webhook_signature(signature_data, signature, WEBHOOK_SECRET):
            logger.error("Invalid signature")
            return JSONResponse(status_code=401, content={"error": "Invalid signature"})
        logger.info(f"Received BagelPay webhook: {payload}")
        
        # Get event type
        event_type = payload.get("event_type")
        
        if event_type == "subscription.paid":
            # Handle subscription payment success event
            obj = payload.get("object", {})
            request_id = obj.get("request_id")
            metadata = obj.get("metadata", {})
            subscription_info = obj.get("subscription", {})
            
            # request_id is the subscription.id we used when creating the subscription
            if not request_id:
                logger.error("Missing request_id in webhook payload")
                return JSONResponse(status_code=400, content={"error": "Missing request_id"})
            
            # Get user ID and subscription info from metadata
            user_id = metadata.get("user_id")
            subscription_id = metadata.get("subscription_id")
            
            # request_id and subscription_id should be the same
            if not subscription_id:
                subscription_id = request_id
            
            if not user_id:
                logger.error("Missing user_id in webhook metadata")
                return JSONResponse(status_code=400, content={"error": "Missing user_id in metadata"})
            
            # Activate subscription
            try:
                subscription = await SubscriptionService.activate_subscription(
                    db=db,
                    subscription_id=uuid.UUID(subscription_id),
                    user_id=uuid.UUID(user_id)
                )
                
                logger.info(
                    f"Successfully activated subscription {subscription_id} for user {user_id}, "
                    f"BagelPay subscription: {subscription_info.get('id')}"
                )
                
                return JSONResponse(
                    status_code=200, 
                    content={
                        "message": "Subscription activated successfully",
                        "subscription_id": subscription_id
                    }
                )
                
            except Exception as e:
                logger.error(f"Failed to activate subscription {subscription_id}: {e}")
                return JSONResponse(
                    status_code=500, 
                    content={"error": f"Failed to activate subscription: {str(e)}"}
                )
        
        elif event_type == "subscription.canceled":
            # Handle subscription cancellation event
            obj = payload.get("object", {})
            metadata = obj.get("metadata", {})
            subscription_info = obj.get("subscription", {})
            
            # Get user ID and subscription info from metadata
            user_id = metadata.get("user_id")
            subscription_id = metadata.get("subscription_id")
            
            if not user_id or not subscription_id:
                logger.error("Missing user_id or subscription_id in webhook metadata")
                return JSONResponse(
                    status_code=400, 
                    content={"error": "Missing user_id or subscription_id in metadata"}
                )
            
            # Cancel subscription
            try:
                subscription = await SubscriptionService.cancel_subscription(
                    db=db,
                    user_id=uuid.UUID(user_id),
                    subscription_id=uuid.UUID(subscription_id)
                )
                
                logger.info(
                    f"Successfully canceled subscription {subscription_id} for user {user_id}, "
                    f"BagelPay subscription: {subscription_info.get('subscription_id')}"
                )
                
                return JSONResponse(
                    status_code=200, 
                    content={
                        "message": "Subscription canceled successfully",
                        "subscription_id": subscription_id
                    }
                )
                
            except Exception as e:
                logger.error(f"Failed to cancel subscription {subscription_id}: {e}")
                return JSONResponse(
                    status_code=500, 
                    content={"error": f"Failed to cancel subscription: {str(e)}"}
                )
        
        else:
            # Log other event types for now
            logger.info(f"Received webhook event: {event_type}, ignoring for now")
            return JSONResponse(status_code=200, content={"message": "Event received"})
            
    except Exception as e:
        logger.error(f"Error processing BagelPay webhook: {e}")
        return JSONResponse(status_code=400, content={"error": "Invalid request body"})

