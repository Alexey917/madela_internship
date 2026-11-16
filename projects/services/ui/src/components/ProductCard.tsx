import { Button, Card, Tag } from 'antd';
import { motion } from 'motion/react';
import type { Product } from '../types';
import product_img from '../assets/product_img.png'
import product_3 from '../assets/product_3.png'
import product_1 from '../assets/product_1.png'

interface Props {
  product: Product;
  onBuy: (product: Product) => void;
}

export function ProductCard({ product, onBuy }: Props) {
  const inStock = product.stock > 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ scale: 1.02 }}
    >
      <Card
        title={product.name}
        style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
        styles={{ body: { flex: 1, display: 'flex', flexDirection: 'column' } }}
      >
        <div style={{ flex: 1 }}>
          <img src={product.id % 3 === 0 ? product_3 : product.id % 2 === 0 ? product_img : product_1} alt="Изображение" width={200} height={200} />
          <p style={{ color: '#666', fontSize: 13 }}>
            {product.publisher} · {product.min_players}–{product.max_players} игроков
            {product.play_time_minutes && ` · ${product.play_time_minutes} мин`}
          </p>
          <Tag color="green">{product.price} ₽</Tag>
          <Tag color={inStock ? 'blue' : 'red'}>
            {inStock ? `В наличии: ${product.stock}` : 'Нет в наличии'}
          </Tag>
        </div>
        <Button
          type="primary"
          block
          disabled={!inStock}
          onClick={() => onBuy(product)}
          style={{ marginTop: 16 }}
        >
          {inStock ? 'Купить' : 'Нет в наличии'}
        </Button>
      </Card>
    </motion.div>
  );
}