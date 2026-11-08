import { useState } from 'react';
import {
  App,
  Button,
  Empty,
  InputNumber,
  List,
  Modal,
  Space,
  Typography,
} from 'antd';
import { DeleteOutlined } from '@ant-design/icons';
import { motion } from 'motion/react';
import { api } from '../api/client';
import { OrderStatusModal } from './OrderStatusModal';
import type { Product } from '../types';

const { Text } = Typography;

interface CartItem {
  product: Product;
  quantity: number;
}

interface Props {
  open: boolean;
  cart: CartItem[];
  onClose: () => void;
  onOrdered: () => void;
  onQuantityChange: (productId: number, quantity: number) => void;
  onRemove: (productId: number) => void;
}

export function CartModal({ open, cart, onClose, onOrdered, onQuantityChange, onRemove }: Props) {
  const { message } = App.useApp();
  const [loading, setLoading] = useState(false);
  const [orderId, setOrderId] = useState<number | null>(null);

  const totalAmount = cart.reduce(
    (s, c) => s + parseFloat(c.product.price) * c.quantity,
    0
  );

  const handleOrder = async () => {
    if (cart.length === 0) return;

    setLoading(true);
    try {
      const idempotencyKey = crypto.randomUUID();
      const user_id = `user-${Math.random().toString(36).substring(7)}`;

      const order = await api.createOrder(
        {
          user_id,
          items: cart.map((c) => ({
            product_id: c.product.id,
            quantity: c.quantity,
            unit_price: c.product.price,
          })),
        },
        idempotencyKey
      );

      message.success(`Заказ #${order.id} создан`);
      setOrderId(order.id);
      onOrdered();
    } catch (e: unknown) {
      if(typeof e === 'string') {
        message.error(`Ошибка: ${e.message}`);
      }
      
    } finally {
      setLoading(false);
    }
  };

  const handleCloseStatus = () => {
    setOrderId(null);
    onClose();
  };

  if (orderId !== null) {
    return (
      <OrderStatusModal
        orderId={orderId}
        open={true}
        onClose={handleCloseStatus}
      />
    );
  }

  return (
    <Modal
      title="Корзина"
      open={open}
      onCancel={onClose}
      footer={null}
      width={600}
    >
      {cart.length === 0 ? (
        <Empty description="Корзина пуста" />
      ) : (
        <>
          <List
            dataSource={cart}
            renderItem={(item) => (
              <motion.div
                layout
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
              >
                <List.Item
                  actions={[
                    <InputNumber
                      key="qty"
                      min={1}
                      max={item.product.stock}
                      value={item.quantity}
                      onChange={(v) =>
                        onQuantityChange(item.product.id, v || 1)
                      }
                      size="small"
                    />,
                    <Button
                      key="del"
                      type="text"
                      danger
                      icon={<DeleteOutlined />}
                      onClick={() => onRemove(item.product.id)}
                    />,
                  ]}
                >
                  <List.Item.Meta
                    title={item.product.name}
                    description={
                      <Space>
                        <Text type="secondary">{item.product.price} ₽ × {item.quantity}</Text>
                        <Text strong>
                          {(parseFloat(item.product.price) * item.quantity).toFixed(2)} ₽
                        </Text>
                      </Space>
                    }
                  />
                </List.Item>
              </motion.div>
            )}
          />

          <div style={{ marginTop: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Text strong style={{ fontSize: 20 }}>
              Итого: {totalAmount.toFixed(2)} ₽
            </Text>
            <Button
              type="primary"
              size="large"
              loading={loading}
              onClick={handleOrder}
            >
              Оформить заказ
            </Button>
          </div>
        </>
      )}
    </Modal>
  );
}