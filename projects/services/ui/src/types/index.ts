export interface Product {
  id: number;
  name: string;
  description: string | null;
  publisher: string | null;
  min_players: number | null;
  max_players: number | null;
  play_time_minutes: number | null;
  min_age: number | null;
  price: string;  // Decimal → строка
  stock: number;
  is_active: boolean;
}

export interface ProductListResponse {
  items: Product[];
  total: number;
  page: number;
  size: number;
}

export interface OrderItemCreate {
  product_id: number;
  quantity: number;
  unit_price: string;
}

export interface OrderCreate {
  user_id: string;
  items: OrderItemCreate[];
}

export type OrderStatus = 'pending' | 'reserved' | 'paid' | 'completed' | 'failed' | 'cancelled';

export interface Order {
  id: number;
  user_id: string;
  status: OrderStatus;
  total_amount: string;
  items: {
    product_id: number;
    quantity: number;
    unit_price: string;
  }[];
  created_at: string;
  updated_at: string;
}