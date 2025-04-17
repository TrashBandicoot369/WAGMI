// Constants file for the application
// Will be used for status labels, color mappings, and button copy

export const CALL_STATUS = {
  LIVE: 'live',
  PENDING: 'pending',
  COMPLETED: 'completed',
  CANCELED: 'canceled',
} as const;

export const STATUS_LABELS = {
  [CALL_STATUS.LIVE]: 'Live',
  [CALL_STATUS.PENDING]: 'Pending',
  [CALL_STATUS.COMPLETED]: 'Completed',
  [CALL_STATUS.CANCELED]: 'Canceled',
} as const;

export const STATUS_COLORS = {
  [CALL_STATUS.LIVE]: 'bg-green-500',
  [CALL_STATUS.PENDING]: 'bg-yellow-500',
  [CALL_STATUS.COMPLETED]: 'bg-blue-500',
  [CALL_STATUS.CANCELED]: 'bg-red-500',
} as const;

export const BUTTON_COPY = {
  BUY_NOW: 'Buy Now',
  VIEW_CALL: 'View Call',
  JOIN_WAITLIST: 'Join Waitlist',
  CONNECT_WALLET: 'Connect Wallet',
} as const; 