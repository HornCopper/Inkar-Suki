from bs4 import BeautifulSoup, element
from src.tools.dep import *
import uuid
import httpx
import asyncio
import time
from src.tools.utils import get_api, post_url
import json
from httpx import Response as XResponse


class Response:
    def __init__(self, data: dict) -> None:
        if isinstance(data, XResponse):
            data = data.json()
        self.code = data.get('code')
        self._data = data.get('data')

    @property
    def success(self):
        return self.code == 1


class TipResponse(Response):
    def __init__(self, data: dict) -> None:
        super().__init__(data)
        if not self.success:
            self.results = None
            return
        self.items = self._data.get('items')
        if self.items is None:
            self.results = None
            return
        self.results = [x.get('content') for x in self.items]
        pass

    def to_dict(self):
        return {'results': self.results, 'items': self.items}


class QuesResponse(Response):
    def __init__(self, data: dict) -> None:
        super().__init__(data)
        if not self.success:
            self.results = None
            return
        self.items = self._data.get('robotResults')
        if self.items is None:
            self.results = None
            return
        self.results = [x.get('answerContent') for x in self.items]
        pass

    def to_dict(self):
        return {'results': self.results, 'items': self.items}


class Jx3GuidResult:
    tip: TipResponse = None
    question: QuesResponse = None

    def __init__(self, tip: TipResponse, ques: QuesResponse) -> None:
        self.tip = tip
        self.question = ques

    def to_dict(self):
        return {'tip': self.tip.to_dict(), 'question': self.question.to_dict()}


class Jx3Guide:
    API_host = 'https://chatrobot.xoyo.com/chatbot/'
    # 初始化
    API_init = 'web/init/{channel}?sysNum={channel}&sourceId={source}&lang=zh_CN&_={timestamp}'
    # 获取提示
    API_tip = 'web/inputPrompt/{channel}?sourceId={source}&question={question}&_={timestamp}'
    # 发送问题
    API_ques = 'web/chat/{channel}?sourceId={source}'

    CHANNEL_Init = '1578898069071'
    CHANNEL_TIP = '1578898069072'

    def with_headers(self, raw: dict = None):
        if raw is None:
            raw = {}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }
        headers.update(raw)
        return headers

    def __init__(self, question: str) -> None:
        self.question = question
        self.session = httpx.AsyncClient(headers=self.with_headers())

    @staticmethod
    def get_url(url: str) -> str:
        u = url.replace('{timestamp}', str(int(time.time() * 1e3)))
        u = u.replace('{source}', '62203')
        u = f'{Jx3Guide.API_host}{u}'
        return u

    async def _step_init(self):
        url = Jx3Guide.get_url(Jx3Guide.API_init)
        url = url.replace('{channel}', Jx3Guide.CHANNEL_Init)
        data = await self.session.get(url)
        r = Response(data)
        return r

    async def _step_get_tip(self):
        url = Jx3Guide.get_url(Jx3Guide.API_tip)
        url = url.replace('{channel}', Jx3Guide.CHANNEL_Init)
        url = url.replace('{question}', self.question)
        data = await self.session.get(url)
        return TipResponse(data)

    async def _step_ques(self):
        url = Jx3Guide.get_url(Jx3Guide.API_ques)
        url = url.replace('{channel}', Jx3Guide.CHANNEL_Init)
        payload = {"content": self.question, "type": 0, "x": 0, "y": 0}
        headers = {
            'Content-Type': 'application/json'
        }
        data = await self.session.post(url, json=payload, headers=self.with_headers(headers))
        res = QuesResponse(data)
        await self.handle_answer(res)
        return res

    async def handle_single_res(self, res: str):
        doc = BeautifulSoup(res)
        ##############处理图片#################
        imgs = doc.find_all('img')
        for img in imgs:
            img: element.Tag = img
            src = img.attrs.get('src')
            if not src:
                continue
            img_data = await self.session.get(src)
            if not img_data.status_code == 200:
                img.attrs['src'] = ''  # 错误
                continue
            img_data = img_data.content
            img_file = f'{CACHE}{os.sep}{uuid.uuid1()}.png'
            with open(img_file, 'wb') as f:
                f.write(img_data)
            img.attrs['src'] = Path(img_file).as_uri()
        ##############处理图片#################

        ##############处理段落#################
        paras = doc.find_all('p')
        result = []
        for p in paras:
            contents = p.contents
            r = []
            for index in range(len(contents)):
                data = contents[index]
                if not type(data) == element.Tag:
                    r.append(data.get_text())
                    continue # 非标签则直接添加文字
                if data.has_attr('src'):
                    r.append(['IMG', data.attrs.get("src")])
                    continue # 图片
                if data.has_attr('data-question'):
                    x = ['RELA', data.attrs.get("data-question")]
                    r.append(x) # 关联问题
                r.append(data.get_text())
            result.append([x for x in r if x])  # 加入并排除空数据
        ##############处理段落#################
        return result

    async def handle_answer(self, res: QuesResponse):
        res.results = [await self.handle_single_res(x) for x in res.results]

    async def run_async(self):
        await self._step_init()
        tips = await self._step_get_tip()
        result = await self._step_ques()
        return Jx3GuidResult(tips, result)


async def get_guide(submit: str) -> Jx3GuidResult:
    '''
    获取jx3萌新指引的截图
    '''
    r = await Jx3Guide(submit).run_async()
    return r

if __name__ == '__main__':
    asyncio.run(get_guide('五行石'))
