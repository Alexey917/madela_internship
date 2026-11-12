import { BrowserRouter, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { App as AntApp, Layout, Menu, Button, Space, Tag } from 'antd';
import { ShoppingCartOutlined, UserOutlined, LogoutOutlined } from '@ant-design/icons';
import { useState } from 'react';
import { AuthProvider } from './contexts/AuthContext';
import { useAuth } from './hooks/useAuthContext'
import { ProtectedRoute } from './components/ProtectedRoute';
import { LoginPage } from './pages/LoginPage';
import { CatalogPage } from './pages/CatalogPage';
// import { AdminPage } from './pages/AdminPage';
import { CartModal } from './components/CartModal';
import type { Product } from './types';

const { Header, Content } = Layout;

function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [cart, setCart] = useState<{ product: Product; quantity: number }[]>([]);
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
    setCart((prev) => prev.map((c) => (c.product.id === productId ? { ...c, quantity } : c)));
  };

  const removeFromCart = (productId: number) => {
    setCart((prev) => prev.filter((c) => c.product.id !== productId));
  };

  const totalItems = cart.reduce((s, c) => s + c.quantity, 0);

  if (location.pathname === '/login') {
    return (
      <Routes>
        <Route path="/login" element={<LoginPage />} />
      </Routes>
    );
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 32 }}>
          <div style={{ color: 'white', fontSize: 18, fontWeight: 600 }}>🎲 Board Games Shop</div>
          <Menu
            theme="dark"
            mode="horizontal"
            selectedKeys={[location.pathname]}
            onClick={({ key }) => navigate(key)}
            items={[
              { key: '/', label: 'Каталог' },
              ...(user?.role === 'admin' ? [{ key: '/admin', label: 'Админка' }] : []),
            ]}
            style={{ flex: 1, minWidth: 0 }}
          />
        </div>

        <Space>
          {user && (
            <>
              <Button
                type="text"
                icon={<ShoppingCartOutlined />}
                onClick={() => setCartOpen(true)}
                style={{ color: 'white' }}
              >
                Корзина ({totalItems})
              </Button>
              <Tag color={user.role === 'admin' ? 'gold' : 'blue'} icon={<UserOutlined />}>
                {user.email} ({user.role})
              </Tag>
              <Button type="text" icon={<LogoutOutlined />} onClick={logout} style={{ color: 'white' }}>
                Выйти
              </Button>
            </>
          )}
        </Space>
      </Header>

      <Content style={{ padding: 24, maxWidth: 1400, margin: '0 auto', width: '100%' }}>
        <Routes>
          <Route path="/" element={
            <ProtectedRoute><CatalogPage onBuy={addToCart} /></ProtectedRoute>
          } />
          {/* <Route path="/admin" element={
            <ProtectedRoute role="admin"><AdminPage /></ProtectedRoute>
          } /> */}
        </Routes>
      </Content>

      <CartModal
        open={cartOpen}
        cart={cart}
        onClose={() => setCartOpen(false)}
        onOrdered={() => setCart([])}
        onQuantityChange={updateQuantity}
        onRemove={removeFromCart}
      />
    </Layout>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AntApp>
        <AuthProvider>
          <AppLayout />
        </AuthProvider>
      </AntApp>
    </BrowserRouter>
  );
}