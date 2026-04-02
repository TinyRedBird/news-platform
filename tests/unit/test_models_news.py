# # tests/unit/test_models_news.py
# from info.models import News, User, Comment
#
# def test_news_status_default(session):
#     """测试新闻状态默认值为0"""
#     n = News(title="t", source="s", digest="d", content="c")
#     session.add(n)
#     session.flush()   # 强制生成默认值
#     assert n.status == 0
#
# def test_news_to_dict_includes_comments_count(session, test_user):
#     """测试 to_dict 方法包含评论数"""
#     # 创建新闻
#     news = News(title="t", source="s", digest="d", content="c")
#     session.add(news)
#     session.flush()
#     # 添加两条评论
#     c1 = Comment(user_id=test_user.id, news_id=news.id, content="good")
#     c2 = Comment(user_id=test_user.id, news_id=news.id, content="bad")
#     session.add_all([c1, c2])
#     session.commit()
#     d = news.to_dict()
#     assert d["comments_count"] == 2