import hashlib


def get_hash(post_data):
    """
    Получаем на вход данные из полей (необходимые поля указаны в словаре)
    Преобразовываем в строковый тип и байты, и в дальнейшем в хэш.
    Возвращаем хэш
    """
    total = b""
    fields = [post_data.title, post_data.preview, post_data.body, post_data.image, post_data.category, post_data.tag]
    for field in fields:
        total += bytes(str(field).encode("utf-8"))
    hash_obj = hashlib.md5(total)
    result_hash = hash_obj.hexdigest()
    return result_hash


def hash_equality(hash_1, hash_2):
    """Сравниваем 2 хэша"""
    return hash_1 == hash_2
