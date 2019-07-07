import datasources.simple_parser
from DB.DB import DB
from datasources import YandexNewsRSS


class DataSourceProvider:
    def __init__(self):
        self.YandexN = YandexNewsRSS.YandexNews()
        self.VK = datasources.simple_parser.VKAPI()
        self.data_base = DB()

    def save_posts(self, quest, count):
        data_vk = self.VK.get_post(quest, count)
        comments = []
        posts = []
        for i in range(count):
            posts.append(data_vk[i][0])
            for j in range(len(data_vk[i][1])):
                if data_vk[i][1][j]['text'] != '0':
                    comments.append(data_vk[i][1][j])
        if len(comments) > 0:
            self.data_base.add_comments(comments)
        self.data_base.add_posts(posts)
        return posts

    def save_ya_news(self, request, count):
        self.data_base.add_news(self.YandexN.get_news_from_search_count(request, count))
        return self.data_base.get_news()