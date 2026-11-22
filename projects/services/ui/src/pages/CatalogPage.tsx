import { useEffect, useState } from 'react';
import { App, Col, Empty, Row, Spin, Pagination } from 'antd';
import { api } from '../api/client';
import { ProductCard } from '../components/ProductCard';
import type { Product } from '../types';

interface Props {
  onBuy: (product: Product) => void;
}

export function CatalogPage({ onBuy }: Props) {
  const { message } = App.useApp();
  const [products, setProducts] = useState<Product[]>([]);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getProducts(currentPage, pageSize)
      .then((data) => {
        setProducts(data.items)
        setTotal(data.total)
      })
      .catch((e) => message.error(`Ошибка загрузки: ${e.message}`))
      .finally(() => setLoading(false));
  }, [message, currentPage, pageSize]);

  if (loading) {
    return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;
  }

  if (products.length === 0) {
    return <Empty description="Нет товаров" />;
  }

  return (
    <div>
      <Row gutter={[16, 16]}>
        {products.map((p) => (
          <Col key={p.id} xs={24} sm={12} md={8} lg={6}>
            <ProductCard product={p} onBuy={onBuy} />
          </Col>
        ))}
      </Row>

      <Pagination
        current={currentPage}
        pageSize={pageSize}
        total={total}
        onChange={(page, size) => {
          setCurrentPage(page);
          setPageSize(size);
        }}
        showSizeChanger
        pageSizeOptions={['5', '10', '20']}
        style={{ marginTop: 24, display: 'flex', justifyContent: 'center' }}
      />
    </div>
  );
}