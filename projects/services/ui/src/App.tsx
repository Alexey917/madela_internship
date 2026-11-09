import { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { App as AntApp, Layout, Typography, Menu } from 'antd';
import { ShoppingCartOutlined } from '@ant-design/icons';
import { CatalogPage } from './pages/CatalogPage';
import { CartModal } from './components/CartModal';
import type { Product } from './types';

const { Header, Content } = Layout;
const { Title } = Typography;

function AppContent() {
  const [cart, setCart] = useState<{ product: Product; quantity: number }[]>([]);
  const { user, logout } = useAuth();
  const [cartOpen, setCartOpen] = useState(false);

  const addToCart = (product: Product) => {
    setCart((prev) => {
      const existing = prev.find((c) => c.product.id === product.id);
      if (existing) {
        return prev.map((c) =>
          c.product.id === product.id ? { ...c, quantity: c.quantity + 1 } : c
        );
      }
      return [...prev, { product, quantity: 1 }];
    });
    setCartOpen(true);
  };

  const updateQuantity = (productId: number, quantity: number) => {
    setCart((prev) =>
      prev.map((c) =>
        c.product.id === productId ? { ...c, quantity } : c
      )
    );
  };

  const removeFromCart = (productId: number) => {
    setCart((prev) => prev.filter((c) => c.product.id !== productId));
  };

  const totalItems = cart.reduce((s, c) => s + c.quantity, 0);

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: '#001529' }}>
        <Title level={3} style={{ color: 'white', margin: 0 }}>
          🎲 Board Games Shop
        </Title>
        <Menu theme="dark" mode="horizontal" items={[
          { key: 'catalog', label: <a href="/">Каталог</a> },
          ...(user?.role === 'admin' ? [{ key: 'admin', label: <a href="/admin">Админка</a> }] : []),
          ...(user ? [{ key: 'logout', label: <a onClick={logout}>Выйти ({user.role})</a> }] : [{ key: 'login', label: <a href="/login">Войти</a> }]),
        ]} />
        <a onClick={() => setCartOpen(true)} style={{ color: 'white', fontSize: 18 }}>
          <ShoppingCartOutlined /> Корзина ({totalItems})
        </a>
      </Header>

      <Content style={{ padding: 24, maxWidth: 1200, margin: '0 auto', width: '100%' }}>
        <CatalogPage onBuy={addToCart} />
      </Content>
      
      <CartModal
        open={cartOpen}
        cart={cart}
        onClose={() => setCartOpen(false)}
        onOrdered={() => {
          setCart([]);
        }}
        onQuantityChange={updateQuantity}
        onRemove={removeFromCart}
      />
    </Layout>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  );
}