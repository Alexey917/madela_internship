import { useEffect, useState } from 'react';
import { App, Col, Empty, Row, Spin } from 'antd';
import { api } from '../api/client';
import { ProductCard } from '../components/ProductCard';
import type { Product } from '../types';

interface Props {
  onBuy: (product: Product) => void;
}

export function CatalogPage({ onBuy }: Props) {
  const { message } = App.useApp();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getProducts()
      .then((data) => setProducts(data.items))
      .catch((e) => message.error(`Ошибка загрузки: ${e.message}`))
      .finally(() => setLoading(false));
  }, [message]);

  if (loading) {
    return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;
  }

  if (products.length === 0) {
    return <Empty description="Нет товаров" />;
  }

  return (
    <Row gutter={[16, 16]}>
      {products.map((p) => (
        <Col key={p.id} xs={24} sm={12} md={8} lg={6}>
          <ProductCard product={p} onBuy={onBuy} />
        </Col>
      ))}
    </Row>
  );
}