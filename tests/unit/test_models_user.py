import pytest
from info.models import User

def test_user_password_setter():
    u = User()
    u.password = 'secret'
    assert u.password_hash is not None
    assert u.password_hash != 'secret'
    with pytest.raises(AttributeError):
        _ = u.password

def test_user_check_password():
    u = User()
    u.password = 'secret'
    assert u.check_password('secret') is True
    assert u.check_password('wrong') is False

def test_user_to_dict_without_avatar(session, test_user):
    d = test_user.to_dict()
    assert d['avatar_url'] == ''
    assert 'password' not in d
    assert d['followers_count'] == 0
    assert d['news_count'] == 0

@pytest.mark.skip(reason="需要 constants.QINIU_DOMIN_PREFIX")
def test_user_to_dict_with_avatar(session, monkeypatch):
    monkeypatch.setattr('info.constants.QINIU_DOMIN_PREFIX', 'http://cdn.example.com/')
    u = User(nick_name='avatar_user', mobile='13900139000', avatar_url='avatars/123.jpg')
    u.password = 'pwd'
    session.add(u)
    session.commit()
    d = u.to_dict()
    assert d['avatar_url'] == 'http://cdn.example.com/avatars/123.jpg'

def test_user_to_admin_dict(session, test_user):
    d = test_user.to_admin_dict()
    assert d['mobile'] == '13800138000'
    assert 'register' in d
    assert 'last_login' in d

def test_user_mobile_unique_constraint(session):
    u1 = User(nick_name='u1', mobile='15000000000')
    u1.password = '1'
    u2 = User(nick_name='u2', mobile='15000000000')
    u2.password = '2'
    session.add(u1)
    session.commit()
    session.add(u2)
    with pytest.raises(Exception):  # IntegrityError
        session.commit()
    session.rollback()

def test_user_follow_relationship(session, test_user):
    other = User(nick_name='other', mobile='15100000000')
    other.password = 'pwd'
    session.add(other)
    session.commit()
    # test_user 关注 other
    test_user.followed.append(other)
    session.commit()
    assert test_user.followed.count() == 1
    assert other.followers.count() == 1