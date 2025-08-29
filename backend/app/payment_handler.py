"""
Payment Handler for DealFlow Analytics
Manages Stripe payments and subscription handling
"""

import os
import stripe
from fastapi import HTTPException
from datetime import datetime, timedelta
from typing import Dict, Optional
import hashlib
import json

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_your_test_key_here")

# Pricing Configuration
PRICE_IDS = {
    "pro": os.getenv("STRIPE_PRO_PRICE_ID", "price_pro_monthly"),
    "premium": os.getenv("STRIPE_PREMIUM_PRICE_ID", "price_premium_monthly"),
    "enterprise": os.getenv("STRIPE_ENTERPRISE_PRICE_ID", "price_enterprise_monthly")
}

# For testing without real Stripe account
TEST_MODE = os.getenv("STRIPE_TEST_MODE", "true").lower() == "true"

class PaymentHandler:
    """Handles all payment-related operations"""
    
    def __init__(self):
        self.stripe = stripe
        self.test_mode = TEST_MODE
        
    async def create_checkout_session(
        self,
        plan: str,
        customer_id: Optional[str] = None,
        extension_id: Optional[str] = None
    ) -> Dict:
        """
        Create a Stripe Checkout session for subscription
        """
        try:
            # In test mode, return a mock checkout URL
            if self.test_mode:
                return {
                    "checkoutUrl": f"https://checkout.stripe.com/test/{plan}_checkout",
                    "sessionId": f"test_session_{hashlib.md5(f'{plan}{datetime.now()}'.encode()).hexdigest()[:16]}"
                }
            
            # Create or retrieve customer
            if customer_id:
                customer = stripe.Customer.retrieve(customer_id)
            else:
                customer = stripe.Customer.create(
                    metadata={"extension_id": extension_id}
                )
            
            # Create checkout session
            session = stripe.checkout.Session.create(
                customer=customer.id,
                payment_method_types=['card'],
                line_items=[{
                    'price': PRICE_IDS.get(plan),
                    'quantity': 1,
                }],
                mode='subscription',
                success_url='https://dealflowanalytics.com/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='https://dealflowanalytics.com/pricing',
                metadata={
                    'plan': plan,
                    'extension_id': extension_id
                }
            )
            
            return {
                "checkoutUrl": session.url,
                "sessionId": session.id,
                "customerId": customer.id
            }
            
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def verify_subscription(self, customer_id: str) -> Dict:
        """
        Verify if a customer has an active subscription
        """
        try:
            # In test mode, return mock subscription data
            if self.test_mode:
                # Simulate some customers having subscriptions
                if hashlib.md5(customer_id.encode()).hexdigest()[0] in '0123456':
                    return {
                        "active": True,
                        "plan": "pro",
                        "status": "active",
                        "current_period_end": (datetime.now() + timedelta(days=30)).isoformat()
                    }
                return {"active": False}
            
            # Retrieve customer's subscriptions
            subscriptions = stripe.Subscription.list(
                customer=customer_id,
                status='active',
                limit=1
            )
            
            if subscriptions.data:
                sub = subscriptions.data[0]
                
                # Determine plan from price ID
                plan = "free"
                for plan_name, price_id in PRICE_IDS.items():
                    if sub.items.data[0].price.id == price_id:
                        plan = plan_name
                        break
                
                return {
                    "active": True,
                    "plan": plan,
                    "status": sub.status,
                    "current_period_end": datetime.fromtimestamp(sub.current_period_end).isoformat()
                }
            
            return {"active": False}
            
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def cancel_subscription(self, customer_id: str) -> Dict:
        """
        Cancel a customer's subscription
        """
        try:
            if self.test_mode:
                return {"status": "cancelled", "message": "Test subscription cancelled"}
            
            subscriptions = stripe.Subscription.list(
                customer=customer_id,
                status='active',
                limit=1
            )
            
            if subscriptions.data:
                sub = stripe.Subscription.delete(subscriptions.data[0].id)
                return {
                    "status": "cancelled",
                    "cancelled_at": datetime.now().isoformat()
                }
            
            return {"status": "no_subscription"}
            
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def update_subscription(
        self,
        customer_id: str,
        new_plan: str
    ) -> Dict:
        """
        Update a customer's subscription to a new plan
        """
        try:
            if self.test_mode:
                return {
                    "status": "updated",
                    "new_plan": new_plan,
                    "message": "Test subscription updated"
                }
            
            subscriptions = stripe.Subscription.list(
                customer=customer_id,
                status='active',
                limit=1
            )
            
            if subscriptions.data:
                sub = subscriptions.data[0]
                
                # Update the subscription
                updated_sub = stripe.Subscription.modify(
                    sub.id,
                    items=[{
                        'id': sub.items.data[0].id,
                        'price': PRICE_IDS.get(new_plan)
                    }],
                    proration_behavior='create_prorations'
                )
                
                return {
                    "status": "updated",
                    "new_plan": new_plan,
                    "next_invoice": datetime.fromtimestamp(
                        updated_sub.current_period_end
                    ).isoformat()
                }
            
            return {"status": "no_subscription"}
            
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_usage_stats(self, customer_id: str) -> Dict:
        """
        Get usage statistics for a customer
        """
        # This would typically query a database
        # For now, return mock data
        return {
            "current_period": {
                "start": datetime.now().replace(day=1).isoformat(),
                "end": (datetime.now().replace(day=1) + timedelta(days=31)).isoformat()
            },
            "usage": {
                "analyses": 45,
                "exports": 12,
                "api_calls": 156
            },
            "limits": {
                "analyses": 100,
                "exports": 50,
                "api_calls": 1000
            }
        }
    
    async def handle_webhook(self, payload: Dict, signature: str) -> Dict:
        """
        Handle Stripe webhook events
        """
        try:
            if self.test_mode:
                return {"status": "success", "message": "Test webhook processed"}
            
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                os.getenv("STRIPE_WEBHOOK_SECRET")
            )
            
            # Handle different event types
            if event.type == 'checkout.session.completed':
                # Payment successful, provision service
                session = event.data.object
                customer_id = session.customer
                plan = session.metadata.get('plan')
                
                # Update user's subscription status in database
                # ... database update logic ...
                
                return {"status": "success", "event": "checkout_completed"}
                
            elif event.type == 'customer.subscription.deleted':
                # Subscription cancelled
                subscription = event.data.object
                customer_id = subscription.customer
                
                # Update user's subscription status in database
                # ... database update logic ...
                
                return {"status": "success", "event": "subscription_cancelled"}
                
            elif event.type == 'invoice.payment_failed':
                # Payment failed
                invoice = event.data.object
                customer_id = invoice.customer
                
                # Handle failed payment (send email, retry, etc.)
                # ... payment failure logic ...
                
                return {"status": "success", "event": "payment_failed"}
            
            return {"status": "success", "event": event.type}
            
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

# Create singleton instance
payment_handler = PaymentHandler()