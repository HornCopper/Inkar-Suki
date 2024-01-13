# from tests.test_docs.test_generate import test_docs_generate_detail as func
# from tests.test_jx3.test_pvx.test_horse import test_horse_list_view as func
# from tests.test_jx3.test_subscribe.test_event_daily import test_event_daily_plain_text as func
# from tests.test_args.test_auto_args import test_auto_args as func
# func()

import test_property


async def main():
    await test_property.run()
import asyncio
asyncio.run(main())