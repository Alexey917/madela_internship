import { useState } from 'react';
import { App, Button, Card, Form, Input } from 'antd';
import { useAuth } from '../hooks/useAuthContext';
import { useNavigate } from 'react-router-dom';
import { getErrorMessage } from '../utils/errors';

export function LoginPage() {
  const { message } = App.useApp();
  const { login } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: { email: string; password: string }) => {
    setLoading(true);
    try {
      await login(values.email, values.password);
      message.success('Вход выполнен');
      navigate('/');
    } catch (e) {
      message.error(getErrorMessage(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
      <Card title="Вход в Board Games Shop" style={{ width: 400 }}>
        <Form onFinish={onFinish} layout="vertical">
          <Form.Item name="email" label="Email" rules={[{ required: true, type: 'email' }]}>
            <Input placeholder="admin@shop.local" />
          </Form.Item>
          <Form.Item name="password" label="Пароль" rules={[{ required: true }]}>
            <Input.Password />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block>
            Войти
          </Button>
        </Form>
        <div style={{ marginTop: 16, fontSize: 12, color: '#666' }}>
          <div>Админ: admin@shop.local / admin123</div>
          <div>Юзер: user@shop.local / user123</div>
        </div>
      </Card>
    </div>
  );
}