import re
import json
import pytest

@pytest.mark.parametrize(
    'code, email, items',
    [   
        #success order creations
        (201, 'ivan@example.com', '1,2;5,1'),
        (201, 'ivan@example.com', '1,2;1,1'),
        (201, 'ivan@example.com', '1,2'),
        (201, 'ivan@example.com', '1,2;2,1;1,2;2,1;1,2;2,1'),
        (201, 'ivan@example.com', '1,1;2,1;3,1;4,1;5,1;6,1;7,1;8,1;9,1;10,1'),
        #incorrect patern in email or order
        (422, '', '1,1'),
        (422, '1', '1,1'),
        (422, '1@1.', '1,1'),
        (422, '1@.1', '1,1'),
        (422, '@1.1', '1,1'),
        (422, '1@1. ', '1,1'),
        (422, '1@ .1', '1,1'),
        (422, ' @1.1', '1,1'),
        (422, '1@1.1', ''),
        (422, '1@1.1', '1'),
        (422, '1@1.1', '1 1'),
        (422, '1@1.1', '1,'),
        (422, '1@1.1', '1,;'),
        (422, '1@1.1', '1,1;;'),
        (422, '1@1.1', '1,1;1;'),
        (422, '1@1.1', '1,1,1;'),
        (422, '1@1.1', '1,1;1,'),
        (422, '1@1.1', '1,1;1,1;'),
        (422, '1@1.1', ';;'),
        (422, '1@1.1', 'd,1'),
        #non existing furniture id
        (404, '1@1.1', '0,1'),
        (404, '1@1.1', '999999,1'),
    ]
)
def test_place_order(client, mock_sender, code, email, items):
    order_data = {
        "email": email,
        "items": items,
    }
    resp = client.post(
        '/orders/',
        data=order_data
    )

    pattern = (
        r"^Your order is:"
        r"(?:\n  - \w+ \(price:\d+\.\d{2}\$, quantity:\d+\), total: \d+\.\d{2}\$)+"
        r"\nTotal summ: \d+\.\d{2}\$$"
    )

    assert resp.status_code == code
    if code == 201:
        mock_sender.send_email.assert_called_once()
        message, recipient = mock_sender.send_email.call_args.args
        assert recipient == order_data["email"]
        assert re.fullmatch(pattern, message), message


@pytest.mark.parametrize(
    'code, email',
    [
        (200, 'example@gmail.com'),
        # non existing email
        (404, 'sample@gmail.com'),
        #incorrect email patern
        (422, ''),
        (422, '1'),
        (422, '1@1.'),
        (422, '1@.1'),
        (422, '@1.1'),
        (422, '1@1. '),
        (422, '1@ .1'),
        (422, ' @1.1'),
    ]
)
def test_get_order(client, mock_sender, code, email):
    client.post(
        '/orders/',
        data={
            "email": 'example@gmail.com',
            "items": '1,2;5,1',
        }
    )

    resp = client.get('/orders/', params={'q': email})

    assert resp.status_code == code


@pytest.mark.parametrize(
    'query, expects',
    [
        (None, True),
        ('abc', False),
        ('chairs', True),
    ]
)
def test_get_furniture(client, query, expects):
    resp = client.get('/furniture/', params={'category': query})
    assert resp.status_code == 200
    content = json.loads(resp.content)
    if expects:
        assert  len(content) > 0
    else:
        assert len(content) == 0


@pytest.mark.parametrize(
    'code, id',
    [
        (200, 1),
        #non existing id
        (404, 999999),
        #incorect id
        (422, -1),
        (422, None),
        (422, 0),
    ]
)
def test_get_furniture_by_id(client, code, id):
    resp = client.get(f'/furniture/{id}')
    assert resp.status_code == code