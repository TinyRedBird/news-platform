import pytest

from info.models import User, News
@pytest.fixture
def test_user_collect_news(db_session):
    user = User(nick_name="u", mobile="1")
    user.password = "p"
    news = News(title="t", source="s", digest="d", content="c")
    db_session.add_all([user, news])
    db_session.commit()
    user.collection_news.append(news)
    db_session.commit()
    assert news in user.collection_news
    user.collection_news.append(news)
    db_session.commit()
    assert user.collection_news.count() == 1