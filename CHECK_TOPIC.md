# Проверка топика /args_map

## Способ 1: Через ROS2 команды в терминале

### 1. Проверить список всех топиков:
```bash
ros2 topic list
```

Должен появиться топик `/args_map` в списке.

### 2. Проверить тип топика:
```bash
ros2 topic type /args_map
```

Ожидаемый результат: `std_msgs/msg/Float64MultiArray`

### 3. Подписаться на топик и просматривать сообщения в реальном времени:
```bash
ros2 topic echo /args_map
```

После нажатия кнопки "Отправить в args_map" в веб-интерфейсе, вы увидите сообщения в терминале.

### 4. Проверить частоту публикации:
```bash
ros2 topic hz /args_map
```

### 5. Просмотреть информацию о топике:
```bash
ros2 topic info /args_map
```

## Способ 2: Через веб-интерфейс

1. Откройте веб-интерфейс и подключитесь к rosbridge
2. Нажмите кнопку **"Подписаться на args_map"** под таблицей точек
3. После подписки появится блок с последним полученным сообщением
4. Нажмите **"Отправить в args_map"** - данные появятся в блоке ниже

## Способ 3: Через Python скрипт

Создайте файл `test_args_map.py`:

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

class ArgsMapSubscriber(Node):
    def __init__(self):
        super().__init__('args_map_subscriber')
        self.subscription = self.create_subscription(
            Float64MultiArray,
            '/args_map',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info('Получено сообщение:')
        self.get_logger().info(f'  Размер данных: {len(msg.data)}')
        self.get_logger().info(f'  Данные: {msg.data}')
        
        # Парсим точки
        points = []
        for i in range(0, len(msg.data), 3):
            if i + 2 < len(msg.data):
                x = msg.data[i]
                y = msg.data[i + 1]
                angle = msg.data[i + 2]
                points.append((x, y, angle))
                self.get_logger().info(f'  Точка {len(points)}: x={x:.2f} м, y={y:.2f} м, угол={angle:.1f}°')

def main(args=None):
    rclpy.init(args=args)
    subscriber = ArgsMapSubscriber()
    rclpy.spin(subscriber)
    subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

Запустите:
```bash
python3 test_args_map.py
```

## Формат данных

Топик `/args_map` публикует сообщения типа `std_msgs/Float64MultiArray` со следующей структурой:

```json
{
  "layout": {
    "dim": [{
      "label": "points",
      "size": <количество_точек>,
      "stride": 3
    }],
    "data_offset": 0
  },
  "data": [x1, y1, angle1, x2, y2, angle2, ...]
}
```

Где:
- `x1, y1, angle1` - координаты и угол первой точки
- `x2, y2, angle2` - координаты и угол второй точки
- и т.д.

## Отладка

Если топик не появляется:

1. Проверьте подключение к rosbridge:
   ```bash
   ros2 topic list | grep args_map
   ```

2. Проверьте логи rosbridge на наличие ошибок

3. Убедитесь, что publisher активирован (в консоли браузера должно быть сообщение об активации)

4. Проверьте консоль браузера (F12) на наличие ошибок при отправке

