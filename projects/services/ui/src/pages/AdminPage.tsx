import { useEffect, useState } from 'react';
import {
  App,
  Button,
  Card,
  Col,
  Form,
  Input,
  InputNumber,
  Modal,
  Popconfirm,
  Row,
  Space,
  Switch,
  Table,
  Tag,
  Tooltip,
  Typography,
} from 'antd';
import {
  EditOutlined,
  EyeInvisibleOutlined,
  EyeOutlined,
  PlusOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { api } from '../api/client';
import { useAuth } from '../hooks/useAuthContext';
import { getErrorMessage } from '../utils/errors';
import type { Product, Stock } from '../types';
import type { TableProps } from 'antd';

const { Title } = Typography;

interface EditState {
  mode: 'create' | 'edit';
  product?: Product;
}

export function AdminPage() {
  const { message } = App.useApp();
  const { user } = useAuth();
  const [products, setProducts] = useState<Product[]>([]);
  const [stocks, setStocks] = useState<Record<number, Stock>>({});
  const [loading, setLoading] = useState(false);
  const [editState, setEditState] = useState<EditState | null>(null);
  const [form] = Form.useForm();

  const token = user?.token ?? '';

  const loadProducts = async () => {
    setLoading(true);
    try {
      const data = await api.getProducts(1, 200);
      setProducts(data.items);
    } catch (e: unknown) {
      message.error(getErrorMessage(e));
    } finally {
      setLoading(false);
    }
  };

  const loadStocks = async (prods: Product[]) => {
    const entries = await Promise.all(
      prods.map(async (p) => {
        try {
          const s = await api.getStock(p.id, token);
          return [p.id, s] as const;
        } catch {
          return [p.id, null] as const;
        }
      })
    );
    const map: Record<number, Stock> = {};
    entries.forEach(([id, s]) => {
      if (s) map[id] = s;
    });
    setStocks(map);
  };

  useEffect(() => {
    if (!token) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadProducts().then(() => {
      // stocks загружаются после products
    });
  }, [token]);

  useEffect(() => {
    if (products.length > 0 && token) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      loadStocks(products);
    }
  }, [products, token]);

  const openCreate = () => {
    form.resetFields();
    form.setFieldsValue({
      is_active: true,
      stock: 0,
      min_players: 2,
      max_players: 4,
      play_time_minutes: 60,
      min_age: 8,
    });
    setEditState({ mode: 'create' });
  };

  const openEdit = (product: Product) => {
    form.setFieldsValue({
      name: product.name,
      description: product.description,
      publisher: product.publisher,
      min_players: product.min_players,
      max_players: product.max_players,
      play_time_minutes: product.play_time_minutes,
      min_age: product.min_age,
      price: product.price,
      stock: product.stock,
      is_active: product.is_active,
    });
    setEditState({ mode: 'edit', product });
  };

  const closeModal = () => {
    setEditState(null);
    form.resetFields();
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);

      if (editState?.mode === 'create') {
        await api.createProduct(values, token);
        message.success('Товар создан');
      } else if (editState?.mode === 'edit' && editState.product) {
        await api.updateProduct(editState.product.id, values, token);
        message.success('Товар обновлён');
      }

      closeModal();
      await loadProducts();
    } catch (e: unknown) {
      if (e && typeof e === 'object' && 'errorFields' in e) return; // validation
      message.error(getErrorMessage(e));
    } finally {
      setLoading(false);
    }
  };

  const toggleActive = async (product: Product) => {
    try {
      setLoading(true);
      await api.updateProduct(product.id, { is_active: !product.is_active }, token);
      message.success(product.is_active ? 'Товар скрыт' : 'Товар активирован');
      await loadProducts();
    } catch (e: unknown) {
      message.error(getErrorMessage(e));
    } finally {
      setLoading(false);
    }
  };

  const columns: TableProps<Product>['columns'] = [
    {
      title: 'ID',
      dataIndex: 'id',
      width: 60,
      sorter: (a: Product, b: Product) => a.id - b.id,
    },
    {
      title: 'Название',
      dataIndex: 'name',
      render: (v: string, r: Product) => (
        <Space direction="vertical" size={0}>
          <span style={{ fontWeight: 600 }}>{v}</span>
          <span style={{ fontSize: 12, color: '#888' }}>{r.publisher}</span>
        </Space>
      ),
    },
    {
      title: 'Цена',
      dataIndex: 'price',
      width: 120,
      render: (v: string) => <Tag color="green">{v} ₽</Tag>,
    },
    {
      title: 'Stock (каталог)',
      dataIndex: 'stock',
      width: 130,
      render: (v: number) => <span>{v}</span>,
    },
    {
      title: 'Inventory',
      key: 'inventory',
      width: 180,
      render: (_: unknown, r: Product) => {
        const s = stocks[r.id];
        if (!s) return <Tag>—</Tag>;
        return (
          <Space size={4}>
            <Tooltip title="Доступно">
              <Tag color="blue">{s.available}</Tag>
            </Tooltip>
            <Tooltip title="Зарезервировано">
              <Tag color="orange">{s.reserved}</Tag>
            </Tooltip>
          </Space>
        );
      },
    },
    {
      title: 'Статус',
      dataIndex: 'is_active',
      width: 120,
      filters: [
        { text: 'Активные', value: true },
        { text: 'Скрытые', value: false },
      ],
      onFilter: (value, r: Product) => r.is_active === value,
      render: (v: boolean) => (
        <Tag color={v ? 'green' : 'red'}>{v ? 'Активен' : 'Скрыт'}</Tag>
      ),
    },
    {
      title: 'Действия',
      key: 'actions',
      width: 180,
      render: (_: unknown, r: Product) => (
        <Space>
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => openEdit(r)}
          >
            Изменить
          </Button>
          <Popconfirm
            title={r.is_active ? 'Скрыть товар?' : 'Активировать товар?'}
            description={r.is_active ? 'Товар перестанет быть виден в каталоге' : 'Товар появится в каталоге'}
            onConfirm={() => toggleActive(r)}
            okText="Да"
            cancelText="Нет"
          >
            <Button
              size="small"
              danger={r.is_active}
              icon={r.is_active ? <EyeInvisibleOutlined /> : <EyeOutlined />}
            />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <Title level={2} style={{ margin: 0 }}>Управление товарами</Title>
        </Col>
        <Col>
          <Space>
            <Button icon={<ReloadOutlined />} onClick={loadProducts} loading={loading}>
              Обновить
            </Button>
            <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
              Создать товар
            </Button>
          </Space>
        </Col>
      </Row>

      <Card>
        <Table
          dataSource={products}
          rowKey="id"
          loading={loading}
          columns={columns}
          pagination={{ pageSize: 20, showSizeChanger: true }}
          rowClassName={(r) => (r.is_active ? '' : 'row-inactive')}
          style={{ background: 'white' }}
        />
      </Card>

      <Modal
        title={editState?.mode === 'create' ? 'Создать товар' : 'Редактировать товар'}
        open={editState !== null}
        onCancel={closeModal}
        onOk={handleSubmit}
        okText={editState?.mode === 'create' ? 'Создать' : 'Сохранить'}
        cancelText="Отмена"
        confirmLoading={loading}
        width={640}
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item
            name="name"
            label="Название"
            rules={[{ required: true, message: 'Введите название' }]}
          >
            <Input placeholder="Каркассон" />
          </Form.Item>

          <Form.Item name="description" label="Описание">
            <Input.TextArea rows={3} placeholder="Базовая игра о строительстве городов" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="publisher" label="Издатель">
                <Input placeholder="Hobby World" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item
                name="price"
                label="Цена (₽)"
                rules={[{ required: true, message: 'Введите цену' }]}
              >
                <Input placeholder="2990.00" />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item
                name="stock"
                label="Stock (каталог)"
                rules={[{ required: true }]}
              >
                <InputNumber min={0} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={6}>
              <Form.Item name="min_players" label="Мин. игроков">
                <InputNumber min={1} max={20} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="max_players" label="Макс. игроков">
                <InputNumber min={1} max={20} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="play_time_minutes" label="Время (мин)">
                <InputNumber min={1} max={1000} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="min_age" label="Возраст от">
                <InputNumber min={0} max={18} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="is_active"
            label="Активен"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}