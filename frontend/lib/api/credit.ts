import { apiClient } from '../api-client';
import { 
  SubscriptionPlansResponse,
  CreateSubscriptionPaymentResponse,
  SubscriptionType,
  SubscriptionPeriod,
  CreditTransactionsResponse,
  RedeemCodeResponse,
} from '../types/api';

/**
 * Get all available subscription plans
 * @returns Promise with list of subscription plans
 */
export async function getSubscriptionPlans() {
  return apiClient.get<SubscriptionPlansResponse>('/credit/subscription/plans');
}

/**
 * Create a subscription payment and get the payment URL
 * @param product_id - Product ID for the subscription
 * @param subscription_type - Type of subscription (basic, pro, enterprise)
 * @param subscription_period - Period of subscription (monthly, yearly)
 * @returns Promise with payment URL
 */
export async function createSubscriptionPayment(
  product_id: string,
  subscription_type: SubscriptionType,
  subscription_period: SubscriptionPeriod
) {
  return apiClient.get<CreateSubscriptionPaymentResponse>(
    '/credit/subscription/payment/create',
    {
      product_id,
      subscription_type,
      subscription_period,
    }
  );
}

/**
 * Get credit transaction history
 * @returns Promise with list of credit transactions and current balance
 */
export async function getCreditTransactions() {
  return apiClient.get<CreditTransactionsResponse>('/credit/transactions');
}

/**
 * Redeem a promo code to get credits
 * @param code - Promo code to redeem
 * @returns Promise with transaction details and updated balance
 */
export async function redeemCode(code: string) {
  return apiClient.post<RedeemCodeResponse>('/credit/redeem', { code });
}
