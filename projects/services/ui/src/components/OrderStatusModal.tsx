import { useEffect, useState } from 'react';
import { App, Modal, Result, Spin, Tag, Timeline, Typography } from 'antd';
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  CloseCircleOutlined,
  LoadingOutlined,
  SyncOutlined,
} from '@ant-design/icons';
import { motion } from 'motion/react';
import { api } from '../api/client';
import type { Order, OrderStatus } from '../types';
import { getErrorMessage }from '../utils/errors'
import { useAuth } from '../hooks/useAuthContext';

const { Text } = Typography;

interface Props {
  orderId: number;
  open: boolean;
  onClose: () => void;
}

const STATUS_CONFIG: Record<OrderStatus, { color: string; icon: React.ReactNode; label: string }> = {
  pending: { color: 'gold', icon: <ClockCircleOutlined />, label: 'Ожидание' },
  reserved: { color: 'blue', icon: <SyncOutlined spin />, label: 'Зарезервировано' },
  paid: { color: 'cyan', icon: <SyncOutlined spin />, label: 'Оплачено' },
  completed: { color: 'green', icon: <CheckCircleOutlined />, label: 'Завершено' },
  failed: { color: 'red', icon: <CloseCircleOutlined />, label: 'Ошибка' },
  cancelled: { color: 'red', icon: <CloseCircleOutlined />, label: 'Отменено' },
};

const STEPS_HAPPY: OrderStatus[] = ['pending', 'reserved', 'paid', 'completed'];
const STEPS_CANCEL: OrderStatus[] = ['pending', 'reserved', 'cancelled'];

export function OrderStatusModal({ orderId, open, onClose }: Props) {
  const { message } = App.useApp();
  const [order, setOrder] = useState<Order | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth()

  useEffect(() => {
    if (!open  || !user) return;

    let cancelled = false;
    let timer: ReturnType<typeof setTimeout>;

    const poll = async () => {
      try {
        const o = await api.getOrder(orderId, user.token);
        if (cancelled) return;
        setOrder(o);

        if (o.status !== 'completed' && o.status !== 'cancelled' && o.status !== 'failed') {
          timer = setTimeout(poll, 1000);
        }
      } catch (e: unknown) {
        const error = getErrorMessage(e)
        if (cancelled) return;
        setError(error);
         message.error(`Ошибка: ${error}`);
      }
    };

    poll();

    return () => {
      cancelled = true;
      if (timer) clearTimeout(timer);
    };
  }, [orderId, open, message]);

  const isFinal = order?.status === 'completed' || order?.status === 'cancelled';

  return (
    <Modal
      open={open}
      onCancel={onClose}
      footer={isFinal ? null : undefined}
      width={600}
      title={`Заказ #${orderId}`}
    >
      {error && <Result status="error" title="Ошибка" subTitle={error} />}

      {!error && !order && <Spin size="large" style={{ display: 'block', margin: '40px auto' }} />}

      {!error && order && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {isFinal && order.status === 'completed' && (
            <Result
              status="success"
              title="Заказ успешно завершён!"
              subTitle={`Сумма: ${order.total_amount} ₽`}
              icon={
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: 'spring', stiffness: 200, damping: 10 }}
                >
                  <CheckCircleOutlined style={{ color: '#52c41a', fontSize: 72 }} />
                </motion.div>
              }
            />
          )}

          {isFinal && order.status === 'cancelled' && (
            <Result
              status="error"
              title="Заказ отменён"
              subTitle={
                order.items.length > 0
                  ? 'Средства не списаны. Товары возвращены в наличие.'
                  : 'Заказ отменён'
              }
              icon={
                <motion.div
                  initial={{ rotate: -180, opacity: 0 }}
                  animate={{ rotate: 0, opacity: 1 }}
                  transition={{ duration: 0.5 }}
                >
                  <CloseCircleOutlined style={{ color: '#ff4d4f', fontSize: 72 }} />
                </motion.div>
              }
            />
          )}

          {!isFinal && (
            <div style={{ textAlign: 'center', marginBottom: 24 }}>
              <Spin indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />} />
              <div style={{ marginTop: 16 }}>
                <Tag color={STATUS_CONFIG[order.status].color} style={{ fontSize: 16, padding: '4px 12px' }}>
                  {STATUS_CONFIG[order.status].icon} {STATUS_CONFIG[order.status].label}
                </Tag>
              </div>
            </div>
          )}

          <div style={{ marginTop: 24 }}>
            <Text strong>Позиции:</Text>
            <ul>
              {order.items.map((item, i) => (
                <li key={i}>
                  Товар #{item.product_id} × {item.quantity} = {item.unit_price} ₽
                </li>
              ))}
            </ul>
            <Text strong>Итого: {order.total_amount} ₽</Text>
          </div>

          <div style={{ marginTop: 24 }}>
            <Text strong>Прогресс SAGA:</Text>
            <Timeline
              style={{ marginTop: 16 }}
              items={getTimelineItems(order.status)}
            />
          </div>
        </motion.div>
      )}
    </Modal>
  );
}

function getTimelineItems(currentStatus: OrderStatus) {
  const isCancel = currentStatus === 'cancelled' || currentStatus === 'failed';
  const steps = isCancel ? STEPS_CANCEL : STEPS_HAPPY;
  const currentIdx = steps.indexOf(currentStatus);

  return steps.map((s, i) => {
    const cfg = STATUS_CONFIG[s];
    const done = i <= currentIdx;
    const active = i === currentIdx;

    return {
      color: done ? (isCancel ? 'red' : 'green') : 'gray',
      dot: done ? cfg.icon : undefined,
      children: (
        <span style={{ fontWeight: active ? 'bold' : 'normal', opacity: done ? 1 : 0.4 }}>
          {cfg.label}
        </span>
      ),
    };
  });
}
