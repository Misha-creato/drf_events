import json
import redis
from typing import Any

from django.contrib.auth import get_user_model
from django.forms import model_to_dict

from config.settings import (
    REDIS_HOST,
    REDIS_PORT,
)

from utils.logger import get_logger


User = get_user_model()
logger = get_logger(__name__)
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=1)


def set_key(key: str, data: Any, time: int = None) -> int:
    logger.info(
        msg=f'Добавление данных {data} в redis по ключу {key}',
    )

    data_json = json.dumps(obj=data)
    try:
        if time is None:
            redis_client.set(name=key, value=data_json)
        else:
            redis_client.setex(name=key, time=time, value=data_json)
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при добавлении данных {data} '
                f'в redis по ключу {key}: {exc}',
        )
        return 500

    logger.info(
        msg=f'Успешно добавлены данные {data} в redis по ключу {key}',
    )
    return 200


def get(key: str, model: Any = None, timeout: int = None, **kwargs) -> (int, Any):
    logger.info(
        msg=f'Получение данных из redis по ключу {key}',
    )

    try:
        data = redis_client.get(name=key)
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при получении данных из redis '
                f'по ключу {key}: {exc}',
        )
        return 500, None

    if model and data is None:
        logger.error(
            msg=f'Данные по ключу {key} не существуют в redis',
        )
        try:
            data, created = model.objects.get_or_create(**kwargs)
        except Exception as exc:
            logger.error(
                msg=f'Возникла ошибка при получении данных из redis '
                    f'по ключу {key}: {exc}',
            )
            return 500, None

        data = model_to_dict(data)
        set_key(
            key=key,
            data=data,
            time=timeout,
        )
        return 200, data

    logger.info(
        msg=f'Успешно получены данные из redis по ключу {key}'
    )
    return 200, json.loads(s=data)


def get_matching_keys(key_pattern: str) -> (int, list):
    logger.info(
        msg=f'Получение списка подходящих ключей из redis '
            f'по шаблону {key_pattern}',
    )

    try:
        matching_keys = redis_client.keys(key_pattern)
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при получении списка подходящих '
                f'ключей из redis по шаблону {key_pattern}: {exc}',
        )
        return 500, []

    logger.info(
        msg=f'Получен список подходящих ключей из redis '
            f'по шаблону {key_pattern}',
    )
    return 200, matching_keys


def delete(key: str) -> int:
    logger.info(
        msg=f'Удаление ключа из redis {key}',
    )

    try:
        redis_client.delete(key)
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при удалении ключа {key} из redis:'
                f'{exc}',
        )
        return 500

    logger.info(
        msg=f'Успешно удален ключ {key} из redis',
    )
    return 200


def push_to_list(key: str, value: str | int) -> int:
    logger.info(
        msg=f'Добавление значения {value} в список redis по '
            f'ключу {key}',
    )

    try:
        redis_client.lpush(key, value)
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при добавлении значения {value} '
                f'в список redis по ключу {key}',
        )
        return 500

    logger.info(
        msg=f'Успешно добавлено значение {value} в список redis по'
            f'ключу {key}',
    )
    return 200


def get_list(key: str) -> (int, list):
    logger.info(
        msg=f'Получение списка из redis по ключу {key}',
    )

    try:
        redis_list = redis_client.lrange(name=key, start=0, end=-1)
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при получении списка из redis по'
                f'ключу {key}',
        )
        return 500, []

    value_list = [value.decode('utf-8') for value in redis_list]

    logger.info(
        msg=f'Успешно получен список из redis по ключу {key}',
    )
    return 200, value_list


def remove_from_list(key: str, value: str) -> int:
    logger.info(
        msg=f'Удаление значения {value} из списка redis по ключу {key}',
    )

    try:
        redis_client.lrem(name=key, count=0, value=value)
    except Exception as exc:
        logger.error(
            msg=f'Возникла ошибка при удалении значения {value} из '
                f'списка redis по ключу {key}',
        )
        return 500

    logger.info(
        msg=f'Успешно удалено значение {value} из списка redis по '
            f'ключу {key}',
    )
    return 200
