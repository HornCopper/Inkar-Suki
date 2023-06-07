import random
from . import *
from src.views import get_render_content, get_render_image
test_base_path = 'src/views/test/index.html'


def test_vue():
    img = get_render_image(test_base_path)
    assert img.endswith('.png')


def test_render_data():
    rnd_id = random.randrange(int(10e7), int(10e8))
    content = get_render_content(test_base_path, {'test': rnd_id})
    assert str(rnd_id) in content, 'content should be in rendered result'
