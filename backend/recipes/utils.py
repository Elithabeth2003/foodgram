"""from hashids import Hashids

from foodgram.constants import MIN_LENGTH_FOR_SHORT_URL, SALT


hashids = Hashids(min_length=MIN_LENGTH_FOR_SHORT_URL, salt=SALT)


def get_hashed_short_url(value):
    """"Возвращает хешированный url адрес.""""
    return hashids.encode(value)


def get_decoded_short_url(value):
    """"Возвращает декодированный url адрес.""""
    return hashids.decode(value)
"""